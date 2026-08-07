import asyncio

import httpx
import pytest

from app.config import settings
from app.db import (
    close_db,
    connect_db,
    get_blacklist_collection,
    get_users_collection,
    init_indexes,
)
from app.main import app

settings.MONGODB_DB = "truthlens_test"


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    settings.MONGODB_DB = "truthlens_test"
    connect_db()
    await init_indexes()
    yield
    close_db()


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture(autouse=True)
async def clean_db():
    await get_users_collection().delete_many({})
    await get_blacklist_collection().delete_many({})
    yield


async def register_user(client, **overrides):
    payload = {"name": "Test User", "email": "test@example.com", "password": "password123"}
    payload.update(overrides)
    return await client.post("/api/auth/register", json=payload)


async def login(client, email="test@example.com", password="password123"):
    return await client.post("/api/auth/login", json={"email": email, "password": password})


async def auth_headers(client, email="test@example.com", password="password123"):
    res = await login(client, email, password)
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}
