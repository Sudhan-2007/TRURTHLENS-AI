from .conftest import auth_headers, register_user
from .test_news import submit_text

SUPPORTED_TEXT = (
    "Global average temperatures have increased by more than one degree Fahrenheit "
    "since the late 19th century. Scientists at NASA have confirmed the planet is "
    "getting warmer every decade."
)
CONTRADICTED_TEXT = (
    "Vaccines cause autism in children. Routine childhood immunization is linked to "
    "autism spectrum disorder and should be stopped."
)
UNVERIFIED_TEXT = (
    "The local bakery produced a record number of donuts on Tuesday morning. "
    "Neighbors celebrated with coffee and praised the staff for their hard work."
)


async def _full_submit(client, headers, content=SUPPORTED_TEXT):
    res = await submit_text(client, headers, content=content)
    sid = res.json()["submission_id"]
    res = await client.post(f"/api/trust-score/{sid}", headers=headers)
    assert res.status_code == 200, res.text
    return sid


async def _setup_user(client, name="Test User", email="test@example.com"):
    await register_user(client, name=name, email=email)
    return await auth_headers(client, email=email)


async def _seed(client, headers):
    supported = await _full_submit(client, headers, content=SUPPORTED_TEXT)
    contradicted = await _full_submit(client, headers, content=CONTRADICTED_TEXT)
    unverified = await _full_submit(client, headers, content=UNVERIFIED_TEXT)
    return supported, contradicted, unverified


async def test_history_lists_all(client):
    headers = await _setup_user(client)
    await _seed(client, headers)

    res = await client.get("/api/history", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 3
    assert len(body["items"]) == 3
    assert body["limit"] == 20
    assert body["skip"] == 0


async def test_history_search(client):
    headers = await _setup_user(client)
    await _seed(client, headers)

    res = await client.get(
        "/api/history", params={"search": "Vaccines cause autism"}, headers=headers
    )
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) == 1
    assert "Vaccines cause autism" in items[0]["content"]


async def test_history_filter_prediction(client):
    headers = await _setup_user(client)
    await _seed(client, headers)

    res = await client.get("/api/history", params={"prediction": "FAKE"}, headers=headers)
    assert res.status_code == 200
    items = res.json()["items"]
    assert items
    assert all(item["ai_prediction"] == "FAKE" for item in items)


async def test_history_filter_verification_status(client):
    headers = await _setup_user(client)
    await _seed(client, headers)

    res = await client.get(
        "/api/history", params={"verification_status": "SUPPORTED"}, headers=headers
    )
    assert res.status_code == 200
    items = res.json()["items"]
    assert items
    assert all(item["verification_status"] == "SUPPORTED" for item in items)


async def test_history_filter_trust_level(client):
    headers = await _setup_user(client)
    await _seed(client, headers)

    res = await client.get("/api/history", params={"trust_level": "VERY_LOW"}, headers=headers)
    assert res.status_code == 200
    items = res.json()["items"]
    assert items
    assert all(item["trust_level"] == "VERY_LOW" for item in items)


async def test_history_pagination(client):
    headers = await _setup_user(client)
    await _seed(client, headers)

    res = await client.get("/api/history", params={"limit": 2, "skip": 0}, headers=headers)
    assert res.status_code == 200
    first = res.json()
    assert len(first["items"]) == 2
    assert first["total"] == 3

    res = await client.get("/api/history", params={"limit": 2, "skip": 2}, headers=headers)
    second = res.json()
    assert len(second["items"]) == 1
    assert second["items"][0]["submission_id"] != first["items"][0]["submission_id"]


async def test_history_sort_ascending(client):
    headers = await _setup_user(client)
    await _seed(client, headers)

    res = await client.get("/api/history", params={"sort": "created_asc"}, headers=headers)
    assert res.status_code == 200
    items = res.json()["items"]
    dates = [item["created_at"] for item in items]
    assert dates == sorted(dates)


async def test_history_invalid_filter(client):
    headers = await _setup_user(client)
    await _seed(client, headers)

    res = await client.get("/api/history", params={"prediction": "MAYBE"}, headers=headers)
    assert res.status_code == 400
    res = await client.get("/api/history", params={"sort": "bogus"}, headers=headers)
    assert res.status_code == 400


async def test_history_scoped_to_owner(client):
    headers_a = await _setup_user(client, name="First", email="first@example.com")
    await _seed(client, headers_a)

    headers_b = await _setup_user(client, name="Second", email="second@example.com")
    res = await client.get("/api/history", headers=headers_b)
    assert res.status_code == 200
    assert res.json()["total"] == 0


async def test_history_detail(client):
    headers = await _setup_user(client)
    sid, _, _ = await _seed(client, headers)

    res = await client.get(f"/api/history/{sid}", headers=headers)
    assert res.status_code == 200
    item = res.json()
    assert item["submission_id"] == sid
    assert item["ai_prediction"] in ("REAL", "FAKE")
    assert item["verification_status"]
    assert item["trust_level"]
    assert item["final_score"] is not None


async def test_history_detail_not_found(client):
    headers = await _setup_user(client)
    res = await client.get("/api/history/TL-000000000000-ABC", headers=headers)
    assert res.status_code == 404


async def test_history_detail_forbidden_other_user(client):
    headers_a = await _setup_user(client, name="First", email="first@example.com")
    sid, _, _ = await _seed(client, headers_a)

    headers_b = await _setup_user(client, name="Second", email="second@example.com")
    res = await client.get(f"/api/history/{sid}", headers=headers_b)
    assert res.status_code == 403


async def test_history_requires_authentication(client):
    res = await client.get("/api/history")
    assert res.status_code == 401
    res = await client.get("/api/history/TL-000000000000-ABC")
    assert res.status_code == 401
