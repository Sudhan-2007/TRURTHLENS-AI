from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings
from app.db import get_users_collection
from app.utils.security import create_access_token

from .conftest import auth_headers, login, register_user


async def test_successful_registration(client):
    res = await register_user(client)
    assert res.status_code == 201
    body = res.json()
    assert body["message"] == "User registered successfully"
    assert body["user_id"]

    stored = await get_users_collection().find_one({"email": "test@example.com"})
    assert stored is not None
    assert stored["password_hash"] != "password123"
    assert stored["password_hash"].startswith("$2")


async def test_duplicate_email_registration(client):
    await register_user(client)
    res = await register_user(client, name="Another")
    assert res.status_code == 409


async def test_invalid_email_registration(client):
    res = await register_user(client, email="not-an-email")
    assert res.status_code == 422


async def test_weak_password_registration(client):
    res = await register_user(client, password="short")
    assert res.status_code == 422
    res = await register_user(client, password="onlyletters")
    assert res.status_code == 422


async def test_successful_login(client):
    await register_user(client)
    res = await login(client)
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["expires_in"] == 1800


async def test_incorrect_password(client):
    await register_user(client)
    res = await login(client, password="wrongpass1")
    assert res.status_code == 401


async def test_nonexistent_user_login(client):
    res = await login(client, email="ghost@example.com")
    assert res.status_code == 401


async def test_password_hash_not_exposed(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await client.get("/api/users/me", headers=headers)
    assert res.status_code == 200
    assert "password_hash" not in res.text
    assert "password" not in res.json()


async def test_unauthorized_api_access(client):
    res = await client.get("/api/users/me")
    assert res.status_code == 401


async def test_invalid_jwt(client):
    res = await client.get("/api/users/me", headers={"Authorization": "Bearer not.a.token"})
    assert res.status_code == 401


async def test_expired_jwt(client):
    await register_user(client)
    user = await get_users_collection().find_one({"email": "test@example.com"})
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {"sub": str(user["_id"]), "role": "user", "exp": now - timedelta(minutes=1)},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    res = await client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401


async def test_profile_retrieval(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await client.get("/api/users/me", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == "test@example.com"
    assert body["role"] == "user"
    assert body["name"] == "Test User"


async def test_profile_update(client):
    await register_user(client)
    headers = await auth_headers(client)

    res = await client.put(
        "/api/users/me", headers=headers, json={"name": "Updated Name"}
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Updated Name"

    res = await client.put(
        "/api/users/me", headers=headers, json={"password": "newpass123"}
    )
    assert res.status_code == 200
    bad = await login(client, password="password123")
    assert bad.status_code == 401
    good = await login(client, password="newpass123")
    assert good.status_code == 200


async def test_update_profile_conflict(client):
    await register_user(client, name="First", email="first@example.com")
    await register_user(client, name="Second", email="second@example.com")
    headers = await auth_headers(client, email="first@example.com")
    res = await client.put(
        "/api/users/me", headers=headers, json={"email": "second@example.com"}
    )
    assert res.status_code == 409


async def test_user_role_authorization(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await client.get("/api/users", headers=headers)
    assert res.status_code == 403


async def test_admin_role_authorization(client):
    await register_user(client)
    await get_users_collection().update_one(
        {"email": "test@example.com"}, {"$set": {"role": "admin"}}
    )
    headers = await auth_headers(client)
    res = await client.get("/api/users", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


async def test_logout_revokes_token(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await client.post("/api/auth/logout", headers=headers)
    assert res.status_code == 204
    res = await client.get("/api/users/me", headers=headers)
    assert res.status_code == 401
