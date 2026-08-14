from app.db import get_ai_explanations_collection
from app.services import (
    ai_pipeline,
    explanation_service,
    score_explanation_service,
    summary_service,
)

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


def _fake_prediction(prediction="FAKE", confidence=0.91):
    return {
        "prediction": prediction,
        "confidence": confidence,
        "model_name": "distilbert",
        "model_version": "1.0.0",
    }


def _fake_verification(status="CONTRADICTED", confidence=0.89, count=2, sources=1):
    return {
        "verification_status": status,
        "verification_confidence": confidence,
        "evidence_count": count,
        "official_source_count": sources,
    }


def _fake_trust(score=28, level="VERY_LOW"):
    return {"final_score": score, "trust_level": level}


def _fake_evidence(status="CONTRADICTED", domain="cdc.gov"):
    return [
        {
            "claim": "Vaccines cause autism in children.",
            "evidence_status": status,
            "similarity_score": 0.81,
            "evidence_summary": "Scientific studies find no link between vaccines and autism.",
            "source_name": "Centers for Disease Control and Prevention",
            "source_domain": domain,
            "source_url": "https://www.cdc.gov/vaccinesafety/index.html",
            "source_title": "Vaccine Safety",
            "publication_date": "2024-01-15",
        }
    ]


async def _explain(submission, prediction, verification, trust_score, evidence):
    return await explanation_service.generate_explanation(
        submission, prediction, verification, trust_score, evidence
    )


async def _explanation(client, headers, content=SUPPORTED_TEXT):
    res = await submit_text(client, headers, content=content)
    sid = res.json()["submission_id"]
    res = await client.post(f"/api/explanation/{sid}", headers=headers)
    assert res.status_code == 200, res.text
    return sid, res.json()


async def test_supported_claim_explanation():
    submission = {"submission_id": "TL-SUPPORTED", "user_id": "u1"}
    explanation = await _explain(
        submission,
        _fake_prediction("REAL", 0.82),
        _fake_verification("SUPPORTED", 0.85, 2, 1),
        _fake_trust(88, "HIGH"),
        _fake_evidence("SUPPORTED", "nasa.gov"),
    )
    assert "supports the submitted claim" in explanation["overall_result"]
    assert "AI model" in explanation["ai_explanation"]
    assert "approved official source" in explanation["verification_explanation"]
    assert "HIGH" in explanation["trust_score_explanation"]
    assert explanation["explanation_version"] == "1.0"


async def test_contradicted_claim_explanation():
    submission = {"submission_id": "TL-CONTRADICTED", "user_id": "u1"}
    explanation = await _explain(
        submission,
        _fake_prediction(),
        _fake_verification(),
        _fake_trust(),
        _fake_evidence(),
    )
    assert "caution" in explanation["overall_result"]
    assert explanation["components"]["verification_status"] == "CONTRADICTED"
    assert explanation["components"]["prediction"] == "FAKE"


async def test_partially_supported_explanation():
    submission = {"submission_id": "TL-PARTIAL", "user_id": "u1"}
    explanation = await _explain(
        submission,
        _fake_prediction("REAL", 0.6),
        _fake_verification("PARTIALLY_SUPPORTED", 0.5, 1, 1),
        _fake_trust(55, "LOW"),
        _fake_evidence("PARTIALLY_SUPPORTED"),
    )
    assert "partially supported" in explanation["overall_result"]
    assert explanation["components"]["verification_status"] == "PARTIALLY_SUPPORTED"


async def test_unverified_claim_explanation():
    submission = {"submission_id": "TL-UNVERIFIED", "user_id": "u1"}
    explanation = await _explain(
        submission,
        _fake_prediction("REAL", 0.55),
        _fake_verification("UNVERIFIED", 0.2, 0, 0),
        _fake_trust(40, "LOW"),
        [],
    )
    assert "does not mean the claim is false" in explanation["overall_result"]
    assert explanation["evidence_summary"] == []
    assert explanation["source_references"] == []
    assert any("not been proven false" in limit for limit in explanation["limitations"])


async def test_conflicting_evidence_is_not_hidden():
    submission = {"submission_id": "TL-CONFLICT", "user_id": "u1"}
    evidence = _fake_evidence("SUPPORTED", "nasa.gov") + _fake_evidence(
        "CONTRADICTED", "cdc.gov"
    )
    explanation = await _explain(
        submission,
        _fake_prediction(),
        _fake_verification("PARTIALLY_SUPPORTED", 0.6, 2, 2),
        _fake_trust(45, "LOW"),
        evidence,
    )
    labels = {item["label"] for item in explanation["evidence_summary"]}
    assert "Supported" in labels
    assert "Contradicted" in labels
    assert len(explanation["source_references"]) == 2


async def test_source_reference_accuracy():
    submission = {"submission_id": "TL-SOURCES", "user_id": "u1"}
    explanation = await _explain(
        submission,
        _fake_prediction("REAL", 0.82),
        _fake_verification("SUPPORTED", 0.85, 1, 1),
        _fake_trust(88, "HIGH"),
        _fake_evidence("SUPPORTED", "cdc.gov"),
    )
    refs = explanation["source_references"]
    assert len(refs) == 1
    assert refs[0]["domain"] == "cdc.gov"
    assert refs[0]["name"] == "Centers for Disease Control and Prevention"
    assert refs[0]["publication_date"] == "2024-01-15"
    assert refs[0]["trust_level"] in ("high", "medium", "low")


def test_score_explanation_levels():
    assert "HIGH" in score_explanation_service.explain_trust_score(
        _fake_trust(90, "HIGH")
    )
    assert "VERY_LOW" in score_explanation_service.explain_trust_score(
        _fake_trust(28, "VERY_LOW")
    )
    assert "not absolute proof" in score_explanation_service.explain_trust_score(
        _fake_trust()
    )


def test_overall_result_templates():
    assert summary_service.overall_result(
        _fake_prediction(), _fake_verification("SUPPORTED"), _fake_trust(88, "HIGH")
    ).endswith("supports the submitted claim.")
    assert "caution" in summary_service.overall_result(
        _fake_prediction(), _fake_verification(), _fake_trust()
    )
    assert "partially supported" in summary_service.overall_result(
        _fake_prediction(),
        _fake_verification("PARTIALLY_SUPPORTED"),
        _fake_trust(55, "LOW"),
    )
    assert "does not mean the claim is false" in summary_service.overall_result(
        _fake_prediction(), _fake_verification("UNVERIFIED"), _fake_trust(40, "LOW")
    )


async def test_supported_end_to_end(client):
    await register_user(client)
    headers = await auth_headers(client)
    sid, explanation = await _explanation(client, headers, content=SUPPORTED_TEXT)
    assert explanation["submission_id"] == sid
    assert explanation["components"]["verification_status"] == "SUPPORTED"
    assert explanation["evidence_summary"]
    assert explanation["source_references"]
    assert explanation["limitations"]


async def test_contradicted_end_to_end(client):
    await register_user(client)
    headers = await auth_headers(client)
    _, explanation = await _explanation(client, headers, content=CONTRADICTED_TEXT)
    assert explanation["components"]["verification_status"] == "CONTRADICTED"
    assert explanation["components"]["trust_level"] in ("LOW", "VERY_LOW")


async def test_unverified_end_to_end(client):
    await register_user(client)
    headers = await auth_headers(client)
    _, explanation = await _explanation(client, headers, content=UNVERIFIED_TEXT)
    assert explanation["components"]["verification_status"] == "UNVERIFIED"
    assert explanation["evidence_summary"] == []
    assert explanation["source_references"] == []


async def test_explanation_consistency(client):
    await register_user(client)
    headers = await auth_headers(client)
    sid, first = await _explanation(client, headers, content=SUPPORTED_TEXT)

    res = await client.post(f"/api/explanation/{sid}", headers=headers)
    assert res.status_code == 200
    second = res.json()
    assert second["overall_result"] == first["overall_result"]
    assert second["ai_explanation"] == first["ai_explanation"]

    res = await client.get(f"/api/explanation/{sid}", headers=headers)
    assert res.status_code == 200
    assert res.json()["trust_score_explanation"] == first["trust_score_explanation"]

    count = await get_ai_explanations_collection().count_documents(
        {"submission_id": sid}
    )
    assert count == 1


async def test_unauthorized_access(client):
    await register_user(client, name="First", email="first@example.com")
    headers_a = await auth_headers(client, email="first@example.com")
    created = await submit_text(client, headers_a)
    sid = created.json()["submission_id"]

    await register_user(client, name="Second", email="second@example.com")
    headers_b = await auth_headers(client, email="second@example.com")
    res = await client.post(f"/api/explanation/{sid}", headers=headers_b)
    assert res.status_code == 403
    res = await client.get(f"/api/explanation/{sid}", headers=headers_b)
    assert res.status_code == 403


async def test_requires_authentication(client):
    res = await client.post("/api/explanation/TL-000000000000-ABC")
    assert res.status_code == 401
    res = await client.get("/api/explanation/TL-000000000000-ABC")
    assert res.status_code == 401


async def test_get_without_generated_explanation(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await submit_text(client, headers)
    sid = res.json()["submission_id"]
    res = await client.get(f"/api/explanation/{sid}", headers=headers)
    assert res.status_code == 404


async def test_generate_nonexistent_submission_404(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await client.post("/api/explanation/TL-000000000000-ABC", headers=headers)
    assert res.status_code == 404


async def test_generate_bad_gateway_when_pipeline_produces_nothing(client, monkeypatch):
    await register_user(client)
    headers = await auth_headers(client)

    async def noop(*args, **kwargs):
        return None

    monkeypatch.setattr(ai_pipeline, "run_pipeline", noop)
    res = await submit_text(client, headers)
    sid = res.json()["submission_id"]

    res = await client.post(f"/api/explanation/{sid}", headers=headers)
    assert res.status_code == 502
    assert res.json()["detail"] == "AI detection produced no result for explanation"


async def test_generate_explanation_fallback_when_insert_returns_none(monkeypatch):
    from bson import ObjectId

    async def none_(*args, **kwargs):
        return None

    monkeypatch.setattr(
        explanation_service.explanation_repository, "insert_explanation", none_
    )
    monkeypatch.setattr(
        explanation_service.explanation_repository, "find_by_submission_id", none_
    )
    result = await explanation_service.generate_explanation(
        {"submission_id": "TL-FALLBACK", "user_id": ObjectId()},
        {
            "prediction": "REAL",
            "confidence": 0.9,
            "model_name": "m",
            "model_version": "v",
        },
        {
            "verification_status": "SUPPORTED",
            "verification_confidence": 0.8,
            "evidence_count": 1,
            "official_source_count": 1,
        },
        {"final_score": 80, "trust_level": "HIGH"},
        [],
    )
    assert result["submission_id"] == "TL-FALLBACK"
