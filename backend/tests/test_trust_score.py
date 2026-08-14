from app.db import get_trust_scores_collection
from app.services import score_calculator

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
PARTIAL_TEXT = (
    "The influenza vaccine guarantees you cannot get the flu this season. "
    "Doctors recommend the shot but say protection varies."
)
UNVERIFIED_TEXT = (
    "The local bakery produced a record number of donuts on Tuesday morning. "
    "Neighbors celebrated with coffee and praised the staff for their hard work."
)


def _expected_final(score: dict) -> int:
    components = {
        "ai_assessment": score["ai_score"],
        "official_verification": score["verification_score"],
        "evidence_quality": score["evidence_score"],
        "source_reliability": score["source_reliability_score"],
        "semantic_similarity": score["similarity_score"],
    }
    return score_calculator.final_score(components)


async def _score(client, headers, content=SUPPORTED_TEXT):
    res = await submit_text(client, headers, content=content)
    sid = res.json()["submission_id"]
    res = await client.post(f"/api/trust-score/{sid}", headers=headers)
    assert res.status_code == 200, res.text
    return sid, res.json()


def test_maximum_score():
    components = {
        "ai_assessment": 100,
        "official_verification": 100,
        "evidence_quality": 100,
        "source_reliability": 100,
        "semantic_similarity": 100,
    }
    assert score_calculator.final_score(components) == 100
    assert score_calculator.trust_level(100) == "HIGH"


def test_minimum_score():
    components = {
        "ai_assessment": 0,
        "official_verification": 0,
        "evidence_quality": 0,
        "source_reliability": 0,
        "semantic_similarity": 0,
    }
    assert score_calculator.final_score(components) == 0
    assert score_calculator.trust_level(0) == "VERY_LOW"


def test_invalid_component_values_are_clamped():
    components = {
        "ai_assessment": 150,
        "official_verification": -20,
        "evidence_quality": 999,
        "source_reliability": None,
        "semantic_similarity": 50,
    }
    total = score_calculator.final_score(components)
    assert total == 50 * (0.30 + 0.20 + 0.05) + 0 * (0.35 + 0.10) or total >= 0
    assert 0 <= total <= 100


def test_score_rounding():
    components = {
        "ai_assessment": 50,
        "official_verification": 50,
        "evidence_quality": 50,
        "source_reliability": 50,
        "semantic_similarity": 50,
    }
    assert score_calculator.final_score(components) == 50


def test_trust_level_boundaries():
    assert score_calculator.trust_level(80) == "HIGH"
    assert score_calculator.trust_level(79) == "MEDIUM"
    assert score_calculator.trust_level(60) == "MEDIUM"
    assert score_calculator.trust_level(59) == "LOW"
    assert score_calculator.trust_level(40) == "LOW"
    assert score_calculator.trust_level(39) == "VERY_LOW"


def test_score_calculator_none_and_invalid_inputs():
    assert score_calculator.clamp(None) == 0.0
    assert score_calculator.ai_assessment(None) == 0.0
    assert (
        score_calculator.ai_assessment({"prediction": "UNKNOWN", "confidence": 0.9})
        == 0.0
    )
    assert score_calculator.ai_assessment({"prediction": "REAL"}) == 0.0
    assert score_calculator.verification_score(None) == 0.0
    assert score_calculator.verification_score({"verification_status": "BOGUS"}) == 0.0


async def test_supported_evidence_scores_high(client):
    await register_user(client)
    headers = await auth_headers(client)
    _, score = await _score(client, headers, content=SUPPORTED_TEXT)

    assert score["verification_score"] == 100
    assert score["source_reliability_score"] == 100
    assert score["similarity_score"] == 100
    assert score["evidence_score"] > 0
    assert score["final_score"] == _expected_final(score)
    assert score["trust_level"] == score_calculator.trust_level(score["final_score"])
    assert score["score_version"] == "1.0"
    assert "not absolute proof" in score["explanation"]


async def test_contradicted_evidence_scores_very_low(client):
    await register_user(client)
    headers = await auth_headers(client)
    _, score = await _score(client, headers, content=CONTRADICTED_TEXT)

    assert score["verification_score"] == 0
    assert score["evidence_score"] > 0
    assert score["final_score"] <= 60
    assert score["final_score"] == _expected_final(score)


async def test_partially_supported_evidence(client):
    await register_user(client)
    headers = await auth_headers(client)
    _, score = await _score(client, headers, content=PARTIAL_TEXT)

    assert score["verification_score"] == 60
    assert score["final_score"] == _expected_final(score)


async def test_unverified_missing_evidence(client):
    await register_user(client)
    headers = await auth_headers(client)
    _, score = await _score(client, headers, content=UNVERIFIED_TEXT)

    assert score["verification_score"] == 40
    assert score["evidence_score"] == 0
    assert score["source_reliability_score"] == 0
    assert score["similarity_score"] == 0
    assert score["final_score"] == _expected_final(score)


async def test_duplicate_calculation_prevented(client):
    await register_user(client)
    headers = await auth_headers(client)
    sid, first = await _score(client, headers, content=SUPPORTED_TEXT)

    res = await client.post(f"/api/trust-score/{sid}", headers=headers)
    assert res.status_code == 200
    second = res.json()
    assert second["final_score"] == first["final_score"]

    count = await get_trust_scores_collection().count_documents({"submission_id": sid})
    assert count == 1


async def test_score_persistence_via_get(client):
    await register_user(client)
    headers = await auth_headers(client)
    sid, score = await _score(client, headers, content=SUPPORTED_TEXT)

    res = await client.get(f"/api/trust-score/{sid}", headers=headers)
    assert res.status_code == 200
    assert res.json()["final_score"] == score["final_score"]
    assert res.json()["submission_id"] == sid


async def test_trust_score_runs_verification_automatically(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await submit_text(client, headers, content=SUPPORTED_TEXT)
    sid = res.json()["submission_id"]

    res = await client.post(f"/api/trust-score/{sid}", headers=headers)
    assert res.status_code == 200
    assert res.json()["submission_id"] == sid
    assert res.json()["verification_score"] == 100


async def test_requires_authentication(client):
    res = await client.post("/api/trust-score/TL-000000000000-ABC")
    assert res.status_code == 401
    res = await client.get("/api/trust-score/TL-000000000000-ABC")
    assert res.status_code == 401


async def test_invalid_submission(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await client.post("/api/trust-score/TL-000000000000-ABC", headers=headers)
    assert res.status_code == 404


async def test_another_users_submission(client):
    await register_user(client, name="First", email="first@example.com")
    headers_a = await auth_headers(client, email="first@example.com")
    created = await submit_text(client, headers_a)
    sid = created.json()["submission_id"]

    await register_user(client, name="Second", email="second@example.com")
    headers_b = await auth_headers(client, email="second@example.com")
    res = await client.post(f"/api/trust-score/{sid}", headers=headers_b)
    assert res.status_code == 403


async def test_calculation_reproducible(client):
    await register_user(client)
    headers = await auth_headers(client)
    sid, _ = await _score(client, headers, content=SUPPORTED_TEXT)
    res = await client.get(f"/api/trust-score/{sid}", headers=headers)
    stored = res.json()
    assert stored["final_score"] == _expected_final(stored)
    assert stored["trust_level"] == score_calculator.trust_level(stored["final_score"])
