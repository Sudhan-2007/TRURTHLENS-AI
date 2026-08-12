import pytest

from app.db import get_ai_predictions_collection, get_news_collection
from app.services import ai_pipeline, ai_service

from .conftest import auth_headers, register_user
from .test_news import submit_text

REAL_TEXT = (
    "The federal minimum wage is worth about 20 percent less than it was when "
    "President Reagan took office, and it is far below the poverty line for a "
    "family of three."
)
FAKE_TEXT = (
    "Says Dick Cheney de-Baathisized the Iraqi government and created ISIS. "
    "The former vice president is personally responsible for the rise of the "
    "terrorist group in Iraq."
)


async def test_pipeline_completes_with_verdict(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await submit_text(client, headers, content=REAL_TEXT)
    sid = res.json()["submission_id"]

    doc = await get_news_collection().find_one({"submission_id": sid})
    assert doc is not None
    assert doc["status"] == "completed"
    assert doc["verification_result"]["verdict"] in ("REAL", "FAKE")
    assert 0.0 <= doc["verification_result"]["confidence"] <= 1.0
    assert "summary" in doc["verification_result"]

    prediction = await get_ai_predictions_collection().find_one({"submission_id": sid})
    assert prediction is not None
    assert prediction["prediction"] == doc["verification_result"]["verdict"]
    assert prediction["confidence"] == doc["verification_result"]["confidence"]


async def test_pipeline_marks_failed_on_error(client, monkeypatch):
    await register_user(client)
    headers = await auth_headers(client)
    res = await submit_text(client, headers)
    sid = res.json()["submission_id"]

    def boom(*args, **kwargs):
        raise RuntimeError("ai down")

    monkeypatch.setattr(ai_pipeline.ai_service, "analyze_text", boom)
    with pytest.raises(RuntimeError):
        await ai_pipeline.run_pipeline(sid)

    doc = await get_news_collection().find_one({"submission_id": sid})
    assert doc["status"] == "failed"


async def test_analyze_short_text_rejected():
    with pytest.raises(ValueError):
        ai_service.analyze_text("too short")


def test_analyze_text_classifies_real_and_fake():
    real = ai_service.analyze_text(REAL_TEXT)
    assert real["verdict"] == "REAL"
    assert real["confidence"] >= 0.5

    fake = ai_service.analyze_text(FAKE_TEXT)
    assert fake["verdict"] == "FAKE"
    assert fake["confidence"] >= 0.5


async def test_model_info_endpoint(client):
    res = await client.get("/api/ai/model-info")
    assert res.status_code == 200
    body = res.json()
    assert body["active_backend"] in ("baseline", "distilbert")
    assert body["labels"] == ["REAL", "FAKE"]
    assert isinstance(body["baseline_report"], dict) or body["baseline_report"] is None


async def test_detect_runs_and_stores_prediction(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await submit_text(client, headers, content=REAL_TEXT)
    sid = res.json()["submission_id"]

    res = await client.post(f"/api/ai/detect/{sid}", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["submission_id"] == sid
    assert body["prediction"] in ("REAL", "FAKE")
    assert 0.0 <= body["confidence"] <= 1.0
    assert body["model_name"]
    assert body["confidence_level"] in ("high", "medium", "low")


async def test_detect_requires_auth(client):
    res = await client.post("/api/ai/detect/TL-000000000000-ABC")
    assert res.status_code == 401


async def test_detect_invalid_submission(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await client.post("/api/ai/detect/TL-000000000000-ABC", headers=headers)
    assert res.status_code == 404


async def test_detect_another_users_submission(client):
    await register_user(client, name="First", email="first@example.com")
    headers_a = await auth_headers(client, email="first@example.com")
    created = await submit_text(client, headers_a)
    sid = created.json()["submission_id"]

    await register_user(client, name="Second", email="second@example.com")
    headers_b = await auth_headers(client, email="second@example.com")
    res = await client.post(f"/api/ai/detect/{sid}", headers=headers_b)
    assert res.status_code == 403


async def test_get_prediction(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await submit_text(client, headers, content=REAL_TEXT)
    sid = res.json()["submission_id"]

    res = await client.get(f"/api/ai/prediction/{sid}", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["submission_id"] == sid
    assert body["prediction"] in ("REAL", "FAKE")


async def test_get_prediction_not_generated(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await submit_text(client, headers, content=REAL_TEXT)
    sid = res.json()["submission_id"]
    await get_ai_predictions_collection().delete_many({"submission_id": sid})

    res = await client.get(f"/api/ai/prediction/{sid}", headers=headers)
    assert res.status_code == 404


def test_confidence_level_mapping():
    assert ai_service.confidence_level(0.95) == "high"
    assert ai_service.confidence_level(0.80) == "high"
    assert ai_service.confidence_level(0.70) == "medium"
    assert ai_service.confidence_level(0.59) == "low"
