from app.db import get_news_collection
from app.services import news_service
from app.utils.validators import TEXT_MAX_LENGTH, URL_MAX_LENGTH

from .conftest import auth_headers, register_user

VALID_TEXT = (
    "A viral claim says that drinking a spoonful of cinnamon every morning "
    "cures all diseases within one week. Health experts strongly disagree."
)
VALID_URL = "https://example.com/news/health-claim-about-cinnamon-cures"


async def submit_text(client, headers, content=VALID_TEXT):
    return await client.post(
        "/api/news/submit",
        headers=headers,
        json={"input_type": "text", "content": content},
    )


async def submit_url(client, headers, url=VALID_URL):
    return await client.post(
        "/api/news/submit-url",
        headers=headers,
        json={"input_type": "url", "url": url},
    )


async def test_submit_valid_text(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await submit_text(client, headers)
    assert res.status_code == 201
    body = res.json()
    assert body["message"] == "News submitted successfully"
    assert body["status"] == "submitted"
    assert body["submission_id"].startswith("TL-")

    stored = await get_news_collection().find_one(
        {"submission_id": body["submission_id"]}
    )
    assert stored is not None
    assert stored["input_type"] == "text"
    assert stored["status"] in ("submitted", "processing", "completed")


async def test_submit_empty_text(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await submit_text(client, headers, content="   ")
    assert res.status_code == 422


async def test_submit_very_short_text(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await submit_text(client, headers, content="too short")
    assert res.status_code == 422


async def test_submit_text_exceeding_max_length(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await submit_text(client, headers, content="a" * (TEXT_MAX_LENGTH + 1))
    assert res.status_code == 413


async def test_submit_valid_url(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await submit_url(client, headers)
    assert res.status_code == 201
    assert res.json()["message"] == "URL submitted successfully"


async def test_submit_malformed_url(client):
    await register_user(client)
    headers = await auth_headers(client)
    for bad in ("not-a-url", "ftp://example.com/file", "http://"):
        res = await submit_url(client, headers, url=bad)
        assert res.status_code == 422


async def test_submit_url_exceeding_max_length(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await submit_url(
        client, headers, url="https://example.com/" + "a" * URL_MAX_LENGTH
    )
    assert res.status_code == 413


async def test_submit_without_authentication(client):
    res = await submit_text(client, {})
    assert res.status_code == 401


async def test_get_own_submission(client):
    await register_user(client)
    headers = await auth_headers(client)
    created = await submit_text(client, headers)
    sid = created.json()["submission_id"]

    res = await client.get(f"/api/news/{sid}", headers=headers)
    assert res.status_code == 200
    assert res.json()["submission_id"] == sid
    assert "password" not in res.text


async def test_access_another_users_submission(client):
    await register_user(client, name="First", email="first@example.com")
    headers_a = await auth_headers(client, email="first@example.com")
    created = await submit_text(client, headers_a)
    sid = created.json()["submission_id"]

    await register_user(client, name="Second", email="second@example.com")
    headers_b = await auth_headers(client, email="second@example.com")
    res = await client.get(f"/api/news/{sid}", headers=headers_b)
    assert res.status_code == 403


async def test_get_nonexistent_submission(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await client.get("/api/news/TL-000000000000-ABC", headers=headers)
    assert res.status_code == 404


async def test_delete_own_submission(client):
    await register_user(client)
    headers = await auth_headers(client)
    created = await submit_text(client, headers)
    sid = created.json()["submission_id"]

    res = await client.delete(f"/api/news/{sid}", headers=headers)
    assert res.status_code == 204
    assert await get_news_collection().find_one({"submission_id": sid}) is None


async def test_delete_another_users_submission(client):
    await register_user(client, name="First", email="first@example.com")
    headers_a = await auth_headers(client, email="first@example.com")
    created = await submit_text(client, headers_a)
    sid = created.json()["submission_id"]

    await register_user(client, name="Second", email="second@example.com")
    headers_b = await auth_headers(client, email="second@example.com")
    res = await client.delete(f"/api/news/{sid}", headers=headers_b)
    assert res.status_code == 403
    assert await get_news_collection().find_one({"submission_id": sid}) is not None


async def test_history_requires_auth(client):
    res = await client.get("/api/news/history")
    assert res.status_code == 401


async def test_history_lists_only_own_submissions(client):
    await register_user(client, name="First", email="first@example.com")
    headers_a = await auth_headers(client, email="first@example.com")
    await submit_text(client, headers_a)
    await submit_url(client, headers_a)

    await register_user(client, name="Second", email="second@example.com")
    headers_b = await auth_headers(client, email="second@example.com")
    await submit_text(client, headers_b)

    res = await client.get("/api/news/history", headers=headers_a)
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 2
    assert all(item["submission_id"].startswith("TL-") for item in items)


async def test_database_failure_handling(client, monkeypatch):
    await register_user(client)
    headers = await auth_headers(client)

    async def boom(*args, **kwargs):
        raise RuntimeError("db down")

    monkeypatch.setattr(news_service, "create_submission", boom)
    res = await submit_text(client, headers)
    assert res.status_code == 500


async def test_api_rate_limit(client):
    await register_user(client)
    headers = await auth_headers(client)
    responses = []
    for _ in range(11):
        res = await submit_text(client, headers)
        responses.append(res.status_code)
    assert responses[:10] == [201] * 10
    assert responses[10] == 429
