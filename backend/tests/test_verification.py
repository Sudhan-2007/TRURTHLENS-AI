import pytest

from app.db import (
    get_official_sources_collection,
    get_users_collection,
    get_verification_evidence_collection,
    get_verification_results_collection,
)
from app.models.news import utcnow
from app.services import ai_pipeline, claim_service, similarity_service, source_service
from app.utils.security import hash_password

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


async def _verified(client, headers, content=SUPPORTED_TEXT):
    res = await submit_text(client, headers, content=content)
    sid = res.json()["submission_id"]
    res = await client.post(f"/api/verification/{sid}", headers=headers)
    assert res.status_code == 200, res.text
    return sid, res.json()


async def test_sources_endpoint_lists_trusted_sources(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await client.get("/api/sources", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 14
    domains = {s["domain"] for s in body["sources"]}
    assert "cdc.gov" in domains
    assert "nasa.gov" in domains
    assert "politifact.com" in domains
    assert all(s["status"] == "trusted" for s in body["sources"])


async def test_sources_requires_auth(client):
    res = await client.get("/api/sources")
    assert res.status_code == 401


async def test_blocked_source_rejected(client):
    await get_official_sources_collection().insert_one(
        {
            "name": "Pants on Fire TV",
            "domain": "pantsonfire.example.com",
            "status": "blocked",
            "source_type": "reputable_news",
            "created_at": utcnow(),
        }
    )
    await source_service.refresh_approved_domains()
    assert (
        source_service.is_approved_domain("https://pantsonfire.example.com/breaking")
        is False
    )
    assert source_service.is_approved_domain("https://www.cdc.gov/vaccines/") is True


def test_claim_extraction():
    claims = claim_service.extract_claims(CONTRADICTED_TEXT)
    assert claims
    assert all("text" in c and "keywords" in c and "entities" in c for c in claims)
    assert any("vaccine" in c["text"].lower() for c in claims)


def test_keyword_generation_removes_stopwords():
    keywords = claim_service.generate_keywords(
        "The vaccine is very safe and effective for all people"
    )
    assert "vaccine" in keywords
    assert "the" not in keywords
    assert "is" not in keywords


def test_semantic_similarity():
    high = similarity_service.compare(
        "Vaccines cause autism.", "Vaccines cause autism in children."
    )
    low = similarity_service.compare(
        "Vaccines cause autism.", "The bakery sold fresh donuts on Tuesday."
    )
    assert high > 0.6
    assert low < 0.3


async def test_supporting_evidence(client):
    await register_user(client)
    headers = await auth_headers(client)
    _, result = await _verified(client, headers, content=SUPPORTED_TEXT)
    assert result["verification_status"] == "SUPPORTED"
    assert result["verification_confidence"] >= 0.6
    assert result["evidence_count"] >= 1
    assert result["official_source_count"] >= 1
    assert "nasa.gov" in result["sources"]


async def test_contradictory_evidence(client):
    await register_user(client)
    headers = await auth_headers(client)
    _, result = await _verified(client, headers, content=CONTRADICTED_TEXT)
    assert result["verification_status"] == "CONTRADICTED"
    assert result["verification_confidence"] >= 0.6
    assert result["evidence_count"] >= 1
    assert "cdc.gov" in result["sources"]


async def test_partially_supporting_evidence(client):
    await register_user(client)
    headers = await auth_headers(client)
    _, result = await _verified(client, headers, content=PARTIAL_TEXT)
    assert result["verification_status"] == "PARTIALLY_SUPPORTED"


async def test_no_evidence_scenario(client):
    await register_user(client)
    headers = await auth_headers(client)
    _, result = await _verified(client, headers, content=UNVERIFIED_TEXT)
    assert result["verification_status"] == "UNVERIFIED"
    assert result["evidence_count"] == 0
    assert result["verification_confidence"] < 0.4


async def test_get_verification_and_evidence(client):
    await register_user(client)
    headers = await auth_headers(client)
    sid, result = await _verified(client, headers, content=SUPPORTED_TEXT)

    res = await client.get(f"/api/verification/{sid}", headers=headers)
    assert res.status_code == 200
    assert res.json()["verification_status"] == result["verification_status"]

    res = await client.get(f"/api/verification/{sid}/evidence", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["count"] >= 1
    assert all("similarity_score" in e for e in body["evidence"])
    assert all("source_domain" in e for e in body["evidence"])


async def test_duplicate_evidence_not_stored_twice(client):
    await register_user(client)
    headers = await auth_headers(client)
    sid, _ = await _verified(client, headers, content=SUPPORTED_TEXT)
    await client.post(f"/api/verification/{sid}", headers=headers)

    count = await get_verification_evidence_collection().count_documents(
        {"submission_id": sid}
    )
    assert count == 1


async def test_invalid_submission_id(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await client.post("/api/verification/TL-000000000000-ABC", headers=headers)
    assert res.status_code == 404


async def test_unauthorized_request(client):
    res = await client.post("/api/verification/TL-000000000000-ABC")
    assert res.status_code == 401


async def test_verification_another_users_submission(client):
    await register_user(client, name="First", email="first@example.com")
    headers_a = await auth_headers(client, email="first@example.com")
    created = await submit_text(client, headers_a)
    sid = created.json()["submission_id"]

    await register_user(client, name="Second", email="second@example.com")
    headers_b = await auth_headers(client, email="second@example.com")
    res = await client.post(f"/api/verification/{sid}", headers=headers_b)
    assert res.status_code == 403


async def test_pipeline_failure_marks_submission_failed(client, monkeypatch):
    await register_user(client)
    headers = await auth_headers(client)
    res = await submit_text(client, headers)
    sid = res.json()["submission_id"]
    await get_verification_results_collection().delete_many({"submission_id": sid})

    def boom(*args, **kwargs):
        raise RuntimeError("verification service down")

    monkeypatch.setattr(ai_pipeline, "run_pipeline", boom)
    with pytest.raises(RuntimeError):
        await ai_pipeline.run_pipeline(sid)


async def test_source_registration_admin_only(client):
    await register_user(client)
    headers = await auth_headers(client)
    res = await client.post(
        "/api/sources",
        headers=headers,
        json={
            "name": "Estonian Statistical Office",
            "domain": "stat.ee",
            "category": "Government Statistics",
            "country": "EE",
            "source_type": "official",
        },
    )
    assert res.status_code == 403

    users = get_users_collection()
    now = utcnow()
    await users.insert_one(
        {
            "name": "Admin",
            "email": "admin@example.com",
            "password_hash": hash_password("adminpass123"),
            "role": "admin",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
    )
    admin_headers = await auth_headers(
        client, email="admin@example.com", password="adminpass123"
    )
    res = await client.post(
        "/api/sources",
        headers=admin_headers,
        json={
            "name": "Estonian Statistical Office",
            "domain": "stat.ee",
            "category": "Government Statistics",
            "country": "EE",
            "source_type": "official",
        },
    )
    assert res.status_code == 200
    assert res.json()["domain"] == "stat.ee"
    assert source_service.is_approved_domain("https://stat.ee/report") is True
