from app.db import get_users_collection

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


async def test_user_dashboard_overview(client):
    headers = await _setup_user(client)
    await _full_submit(client, headers, content=SUPPORTED_TEXT)
    await _full_submit(client, headers, content=CONTRADICTED_TEXT)
    await _full_submit(client, headers, content=UNVERIFIED_TEXT)

    res = await client.get("/api/dashboard/user", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total_submissions"] == 3
    assert body["completed_verifications"] == 3
    assert body["fake_predictions"] >= 1
    assert body["real_predictions"] >= 1
    assert body["unverified_claims"] == 1
    assert 0 <= body["average_trust_score"] <= 100
    assert len(body["recent_verifications"]) == 3
    first = body["recent_verifications"][0]
    assert first["submission_id"]
    assert "verification_status" in first
    assert "trust_level" in first


async def test_user_dashboard_scoped_to_owner(client):
    headers_a = await _setup_user(client, name="First", email="first@example.com")
    await _full_submit(client, headers_a)

    headers_b = await _setup_user(client, name="Second", email="second@example.com")
    res = await client.get("/api/dashboard/user", headers=headers_b)
    assert res.status_code == 200
    assert res.json()["total_submissions"] == 0
    assert res.json()["recent_verifications"] == []


async def test_user_statistics_charts(client):
    headers = await _setup_user(client)
    await _full_submit(client, headers, content=SUPPORTED_TEXT)
    await _full_submit(client, headers, content=CONTRADICTED_TEXT)

    res = await client.get("/api/dashboard/user/statistics", headers=headers)
    assert res.status_code == 200
    body = res.json()

    statuses = {row["value"] for row in body["verification_distribution"]}
    assert {
        "SUPPORTED",
        "CONTRADICTED",
        "PARTIALLY_SUPPORTED",
        "UNVERIFIED",
    } == statuses

    levels = {row["value"] for row in body["trust_score_distribution"]}
    assert {"HIGH", "MEDIUM", "LOW", "VERY_LOW"} == levels

    predictions = {row["value"] for row in body["prediction_distribution"]}
    assert {"REAL", "FAKE"} == predictions

    trend = body["verification_trend"]
    assert set(trend.keys()) == {"daily", "weekly", "monthly"}
    assert len(trend["daily"]) == 14
    assert len(trend["weekly"]) == 8
    assert len(trend["monthly"]) == 6
    assert trend["daily"][-1]["count"] >= 2


async def test_admin_dashboard_requires_admin(client):
    headers = await _setup_user(client)
    res = await client.get("/api/dashboard/admin", headers=headers)
    assert res.status_code == 403
    res = await client.get("/api/dashboard/admin/statistics", headers=headers)
    assert res.status_code == 403


async def test_admin_dashboard_overview(client):
    headers = await _setup_user(client)
    await _full_submit(client, headers, content=SUPPORTED_TEXT)

    await get_users_collection().update_one(
        {"email": "test@example.com"}, {"$set": {"role": "admin"}}
    )
    headers = await auth_headers(client)

    res = await client.get("/api/dashboard/admin", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total_users"] >= 1
    assert body["active_users"] >= 1
    assert body["total_submissions"] >= 1
    assert body["completed_verifications"] >= 1
    assert body["failed_verifications"] >= 0
    assert body["fake_predictions"] >= 0
    assert body["real_predictions"] >= 0
    assert body["unverified_claims"] >= 0
    assert body["official_sources"] == 14
    assert 0 <= body["average_trust_score"] <= 100


async def test_admin_statistics_charts(client):
    headers = await _setup_user(client)
    await _full_submit(client, headers, content=SUPPORTED_TEXT)

    await get_users_collection().update_one(
        {"email": "test@example.com"}, {"$set": {"role": "admin"}}
    )
    headers = await auth_headers(client)

    res = await client.get("/api/dashboard/admin/statistics", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert set(body.keys()) == {
        "verification_distribution",
        "trust_score_distribution",
        "prediction_distribution",
        "verification_trend",
    }
    assert body["verification_distribution"]
    assert body["prediction_distribution"]


async def test_dashboard_requires_authentication(client):
    res = await client.get("/api/dashboard/user")
    assert res.status_code == 401
    res = await client.get("/api/dashboard/user/statistics")
    assert res.status_code == 401
    res = await client.get("/api/dashboard/admin")
    assert res.status_code == 401
