"""End-to-end tests mapping to Phase 9 acceptance test cases TC-001..TC-012."""

from app.db import get_ai_predictions_collection, get_news_collection, get_users_collection

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


async def _register_login(client, email="test@example.com"):
    await register_user(client, email=email)
    return await auth_headers(client, email=email)


async def _full_pipeline(client, headers, content=SUPPORTED_TEXT):
    res = await submit_text(client, headers, content=content)
    sid = res.json()["submission_id"]
    res = await client.post(f"/api/trust-score/{sid}", headers=headers)
    assert res.status_code == 200, res.text
    await client.post(f"/api/explanation/{sid}", headers=headers)
    return sid


async def test_tc001_registration(client):
    res = await register_user(client)
    assert res.status_code == 201
    assert res.json()["user_id"]
    stored = await get_users_collection().find_one({"email": "test@example.com"})
    assert stored is not None
    assert stored["password_hash"].startswith("$2")


async def test_tc002_login_issues_bearer_token(client):
    headers = await _register_login(client)
    assert headers["Authorization"].startswith("Bearer ")


async def test_tc003_submission_completes(client):
    headers = await _register_login(client)
    res = await submit_text(client, headers, content=SUPPORTED_TEXT)
    assert res.status_code == 201
    sid = res.json()["submission_id"]
    res = await client.get(f"/api/news/{sid}", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "completed"


async def test_tc004_ai_prediction_stored(client):
    headers = await _register_login(client)
    res = await submit_text(client, headers, content=SUPPORTED_TEXT)
    sid = res.json()["submission_id"]
    prediction = await get_ai_predictions_collection().find_one({"submission_id": sid})
    assert prediction is not None
    assert prediction["prediction"] in ("REAL", "FAKE")
    assert 0.0 <= prediction["confidence"] <= 1.0

    news = await get_news_collection().find_one({"submission_id": sid})
    assert news["verification_result"]["verdict"] == prediction["prediction"]


async def test_tc005_verification_returns_evidence(client):
    headers = await _register_login(client)
    res = await submit_text(client, headers, content=SUPPORTED_TEXT)
    sid = res.json()["submission_id"]
    res = await client.post(f"/api/verification/{sid}", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["verification_status"] in (
        "SUPPORTED",
        "CONTRADICTED",
        "PARTIALLY_SUPPORTED",
        "UNVERIFIED",
    )
    assert 0.0 <= body["verification_confidence"] <= 1.0
    assert body["evidence_count"] >= 0
    assert isinstance(body["sources"], list)


async def test_tc006_trust_score_generated(client):
    headers = await _register_login(client)
    res = await submit_text(client, headers, content=SUPPORTED_TEXT)
    sid = res.json()["submission_id"]
    res = await client.post(f"/api/trust-score/{sid}", headers=headers)
    assert res.status_code == 200
    score = res.json()
    assert isinstance(score["final_score"], int)
    assert 0 <= score["final_score"] <= 100
    assert score["score_version"] == "1.0"
    assert score["trust_level"] in ("HIGH", "MEDIUM", "LOW", "VERY_LOW")


async def test_tc007_explanation_generated(client):
    headers = await _register_login(client)
    res = await submit_text(client, headers, content=CONTRADICTED_TEXT)
    sid = res.json()["submission_id"]
    res = await client.post(f"/api/explanation/{sid}", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["explanation_version"] == "1.0"
    assert body["components"]
    assert body["components"]["verification_status"] == "CONTRADICTED"
    assert body["limitations"]
    assert all(isinstance(limit, str) and limit for limit in body["limitations"])


async def test_tc008_history_lists_enriched_record(client):
    headers = await _register_login(client)
    await _full_pipeline(client, headers)

    res = await client.get("/api/history", headers=headers)
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) == 1
    item = items[0]
    assert item["ai_prediction"] in ("REAL", "FAKE")
    assert item["verification_status"]
    assert item["trust_level"]
    assert item["final_score"] is not None


async def test_tc009_history_detail_complete(client):
    headers = await _register_login(client)
    sid = await _full_pipeline(client, headers)

    res = await client.get(f"/api/history/{sid}", headers=headers)
    assert res.status_code == 200
    item = res.json()
    assert item["submission_id"] == sid
    assert item["status"] == "completed"
    assert item["content"]
    assert item["ai_prediction"] in ("REAL", "FAKE")
    assert item["verification_status"]
    assert item["trust_level"]
    assert isinstance(item["final_score"], int)


async def test_tc010_user_dashboard_reflects_activity(client):
    headers = await _register_login(client)
    await _full_pipeline(client, headers, content=SUPPORTED_TEXT)
    await _full_pipeline(client, headers, content=CONTRADICTED_TEXT)

    res = await client.get("/api/dashboard/user", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total_submissions"] == 2
    assert body["completed_verifications"] == 2
    assert body["average_trust_score"] >= 0
    assert len(body["recent_verifications"]) == 2


async def test_tc011_admin_dashboard_rbac(client):
    headers = await _register_login(client)
    await _full_pipeline(client, headers)

    res = await client.get("/api/dashboard/admin", headers=headers)
    assert res.status_code == 403

    await get_users_collection().update_one(
        {"email": "test@example.com"}, {"$set": {"role": "admin"}}
    )
    headers = await auth_headers(client)

    res = await client.get("/api/dashboard/admin", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total_users"] >= 1
    assert body["total_submissions"] >= 1
    assert body["official_sources"] == 14


async def test_tc012_cross_user_isolation(client):
    headers_a = await _register_login(client, email="first@example.com")
    await _full_pipeline(client, headers_a)

    headers_b = await _register_login(client, email="second@example.com")
    res = await client.get("/api/history", headers=headers_b)
    assert res.json()["total"] == 0

    res = await client.get("/api/dashboard/user", headers=headers_b)
    assert res.json()["total_submissions"] == 0
