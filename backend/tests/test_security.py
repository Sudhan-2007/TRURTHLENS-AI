import pytest

from app.config import Settings
from app.db import get_users_collection

from .conftest import auth_headers, register_user
from .test_news import submit_text

SUPPORTED_TEXT = (
    "Global average temperatures have increased by more than one degree Fahrenheit "
    "since the late 19th century. Scientists at NASA have confirmed the planet is "
    "getting warmer every decade."
)


async def _setup_user(client, name="Test User", email="test@example.com"):
    await register_user(client, name=name, email=email)
    return await auth_headers(client, email=email)


async def _full_submit(client, headers, content=SUPPORTED_TEXT):
    res = await submit_text(client, headers, content=content)
    sid = res.json()["submission_id"]
    res = await client.post(f"/api/trust-score/{sid}", headers=headers)
    assert res.status_code == 200, res.text
    return sid


async def _make_admin(client, email="test@example.com"):
    await get_users_collection().update_one(
        {"email": email}, {"$set": {"role": "admin"}}
    )
    return await auth_headers(client, email=email)


async def test_all_protected_endpoints_reject_unauthenticated(client):
    routes = [
        ("GET", "/api/users/me"),
        ("GET", "/api/users"),
        ("GET", "/api/news/history"),
        ("POST", "/api/ai/detect/TL-000000000000-ABC"),
        ("GET", "/api/ai/prediction/TL-000000000000-ABC"),
        ("GET", "/api/sources"),
        ("POST", "/api/verification/TL-000000000000-ABC"),
        ("POST", "/api/trust-score/TL-000000000000-ABC"),
        ("GET", "/api/trust-score/TL-000000000000-ABC"),
        ("POST", "/api/explanation/TL-000000000000-ABC"),
        ("GET", "/api/explanation/TL-000000000000-ABC"),
        ("GET", "/api/dashboard/user"),
        ("GET", "/api/dashboard/user/statistics"),
        ("GET", "/api/dashboard/admin"),
        ("GET", "/api/dashboard/admin/statistics"),
        ("GET", "/api/history"),
        ("GET", "/api/history/TL-000000000000-ABC"),
    ]
    for method, url in routes:
        res = await client.request(method, url)
        assert res.status_code == 401, f"{method} {url} -> {res.status_code}"


async def test_cross_user_access_denied_across_modules(client):
    headers_a = await _setup_user(client, name="First", email="first@example.com")
    sid = await _full_submit(client, headers_a)
    await client.post(f"/api/explanation/{sid}", headers=headers_a)

    headers_b = await _setup_user(client, name="Second", email="second@example.com")
    for path in [
        f"/api/trust-score/{sid}",
        f"/api/explanation/{sid}",
        f"/api/history/{sid}",
        f"/api/ai/prediction/{sid}",
        f"/api/verification/{sid}",
        f"/api/news/{sid}",
    ]:
        res = await client.get(path, headers=headers_b)
        assert res.status_code == 403, f"GET {path} -> {res.status_code}"

    res = await client.post(f"/api/ai/detect/{sid}", headers=headers_b)
    assert res.status_code == 403, f"POST /api/ai/detect -> {res.status_code}"


async def test_user_cannot_delete_another_users_submission(client):
    headers_a = await _setup_user(client, name="First", email="first@example.com")
    sid = await _full_submit(client, headers_a)

    headers_b = await _setup_user(client, name="Second", email="second@example.com")
    res = await client.delete(f"/api/news/{sid}", headers=headers_b)
    assert res.status_code == 403


async def test_normal_user_blocked_from_admin_endpoints(client):
    headers = await _setup_user(client)

    res = await client.get("/api/users", headers=headers)
    assert res.status_code == 403

    res = await client.post(
        "/api/sources",
        headers=headers,
        json={
            "name": "WHO",
            "domain": "who.int",
            "category": "Health",
            "country": "US",
            "source_type": "official",
            "trust_level": "high",
            "verification_method": "manual",
        },
    )
    assert res.status_code == 403

    me = await client.get("/api/users/me", headers=headers)
    my_id = me.json()["id"]
    res = await client.put(f"/api/users/{my_id}/role?role=admin", headers=headers)
    assert res.status_code == 403

    res = await client.get("/api/dashboard/admin", headers=headers)
    assert res.status_code == 403
    res = await client.get("/api/dashboard/admin/statistics", headers=headers)
    assert res.status_code == 403


async def test_admin_can_register_official_source(client):
    headers = await _setup_user(client)
    headers = await _make_admin(client)
    res = await client.post(
        "/api/sources",
        headers=headers,
        json={
            "name": "World Health Organization",
            "domain": "who.int",
            "category": "Health",
            "country": "US",
            "source_type": "official",
            "trust_level": "high",
            "verification_method": "domain_verified",
        },
    )
    assert res.status_code == 200
    assert res.json()["domain"] == "who.int"

    res = await client.get("/api/sources", headers=headers)
    domains = {s["domain"] for s in res.json()["sources"]}
    assert "who.int" in domains


async def test_admin_user_list_does_not_expose_hashes(client):
    headers = await _setup_user(client)
    headers = await _make_admin(client)
    res = await client.get("/api/users", headers=headers)
    assert res.status_code == 200
    body = res.text
    assert "password_hash" not in body
    assert "$2" not in body


async def test_history_query_validation(client):
    headers = await _setup_user(client)

    res = await client.get("/api/history", params={"limit": 51}, headers=headers)
    assert res.status_code == 422
    res = await client.get("/api/history", params={"limit": -1}, headers=headers)
    assert res.status_code == 422
    res = await client.get("/api/history", params={"limit": "abc"}, headers=headers)
    assert res.status_code == 422
    res = await client.get("/api/history", params={"sort": "bogus"}, headers=headers)
    assert res.status_code == 400
    res = await client.get(
        "/api/history", params={"prediction": "MAYBE"}, headers=headers
    )
    assert res.status_code == 400


async def test_search_parameter_is_treated_literally(client):
    headers = await _setup_user(client)
    sid = await _full_submit(client, headers)

    res = await client.get(
        "/api/history",
        params={"search": "<script>alert(1)</script>"},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["total"] == 0

    res = await client.get(f"/api/history/{sid}", headers=headers)
    assert res.status_code == 200


async def test_oversized_request_body_rejected(client):
    res = await client.post(
        "/api/auth/register",
        json={"name": "Big", "email": "big@example.com", "password": "x" * 70000},
    )
    assert res.status_code == 413
    assert res.json()["detail"] == "Request body is too large"


async def test_analytics_rate_limit(client):
    headers = await _setup_user(client)
    statuses = []
    for _ in range(31):
        res = await client.get("/api/dashboard/user/statistics", headers=headers)
        statuses.append(res.status_code)
    assert statuses[:30] == [200] * 30
    assert statuses[30] == 429


async def test_responses_do_not_leak_internal_errors(client):
    headers = await _setup_user(client)
    sid = await _full_submit(client, headers)

    res = await client.get(f"/api/trust-score/{sid}", headers=headers)
    assert "Traceback" not in res.text
    assert "password_hash" not in res.text

    res = await client.get(f"/api/explanation/{sid}", headers=headers)
    assert "Traceback" not in res.text
    assert "password_hash" not in res.text

    res = await client.get("/api/history", headers=headers)
    assert "password_hash" not in res.text


async def test_xss_content_round_trips_as_json(client):
    headers = await _setup_user(client)
    payload = "<script>alert('xss')</script> <b>bold</b>"
    res = await submit_text(client, headers, content=payload)
    sid = res.json()["submission_id"]

    res = await client.get(f"/api/history/{sid}", headers=headers)
    assert res.status_code == 200
    assert res.json()["content"] == payload


def test_production_rejects_default_jwt_secret():
    with pytest.raises(ValueError):
        Settings(DEBUG=False, JWT_SECRET="change-me")
    with pytest.raises(ValueError):
        Settings(DEBUG=False, JWT_SECRET="short-secret")


def test_production_validator_rejects_placeholder_secret_and_uri():
    with pytest.raises(ValueError):
        Settings(ENVIRONMENT="production", JWT_SECRET="change-me")
    with pytest.raises(ValueError):
        Settings(
            ENVIRONMENT="production",
            JWT_SECRET="a" * 40,
            MONGODB_URI="mongodb://localhost:27017",
        )
    with pytest.raises(ValueError):
        Settings(
            ENVIRONMENT="production",
            JWT_SECRET="a" * 40,
            MONGODB_URI="mongodb+srv://<user>:<password>@<cluster-url>",
        )


def test_production_validator_accepts_strong_secret_and_real_uri():
    s = Settings(
        ENVIRONMENT="production",
        JWT_SECRET="a" * 40,
        MONGODB_URI="mongodb+srv://user:pass@cluster0.example.mongodb.net/?retryWrites=true",
    )
    assert s.ENVIRONMENT == "production"
    assert s.debug is False


def test_debug_defaults_follow_environment():
    assert Settings(ENVIRONMENT="development").debug is True
    assert Settings(ENVIRONMENT="testing").debug is True
    assert (
        Settings(
            ENVIRONMENT="production",
            JWT_SECRET="a" * 40,
            MONGODB_URI="mongodb://real-host:27017",
        ).debug
        is False
    )
    assert Settings(ENVIRONMENT="development", DEBUG=True).debug is True
