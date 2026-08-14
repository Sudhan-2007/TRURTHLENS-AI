import pytest
from bson import ObjectId
from pydantic import ValidationError

from app.config import Settings
from app.logging_config import configure_logging
from app.models import news as news_models
from app.models import official_source as official_source_models
from app.models import user as user_models
from app.repositories import (
    analytics_repository,
    evidence_repository,
    explanation_repository,
    news_repository,
    trust_score_repository,
)
from app.schemas.verification import SourceRegister
from app.services import (
    claim_service,
    evidence_explanation_service,
    similarity_service,
    source_reliability_service,
    source_service,
)
from app.utils.validators import validate_url


def test_settings_rejects_invalid_environment():
    with pytest.raises(ValueError):
        Settings(ENVIRONMENT="staging")


def test_source_register_validation():
    with pytest.raises(ValidationError):
        SourceRegister(name="   ", domain="example.gov", category="Health")
    with pytest.raises(ValidationError):
        SourceRegister(name="WHO", domain="nodot", category="Health")


def test_configure_logging_is_idempotent():
    configure_logging()
    configure_logging()


def test_validate_url_empty_rejected():
    with pytest.raises(ValueError):
        validate_url("   ")


def test_to_object_id_helpers():
    oid = "a" * 24
    assert isinstance(news_models.to_object_id(oid), ObjectId)
    assert isinstance(user_models.to_object_id(oid), ObjectId)


def test_serialize_official_source_with_source_id():
    doc = {"_id": ObjectId(), "source_id": ObjectId(), "name": "WHO"}
    out = official_source_models.serialize_official_source(doc)
    assert out["id"]
    assert out["source_id"]
    assert out["name"] == "WHO"


def test_analytics_user_filter_empty():
    assert analytics_repository.user_filter(None) == {}
    assert analytics_repository.user_filter("") == {}


async def test_news_repository_find_by_id_and_user():
    doc = await news_repository.create_submission(
        {
            "submission_id": "TL-UNIT-FIND",
            "user_id": ObjectId(),
            "input_type": "text",
            "content": "x",
            "url": None,
            "title": None,
            "source_name": None,
            "language": "en",
            "status": "submitted",
            "verification_result": None,
        }
    )
    found = await news_repository.find_by_id_and_user(doc["_id"], doc["user_id"])
    assert found is not None
    other = await news_repository.find_by_id_and_user(doc["_id"], ObjectId())
    assert other is None


async def test_find_candidates_empty_and_short_keywords():
    assert await evidence_repository.find_candidates([]) == []
    assert await evidence_repository.find_candidates(["a", "bc"]) == []


async def test_insert_score_duplicate_returns_none():
    doc = {"submission_id": "TL-DUP-SCORE", "final_score": 50}
    assert await trust_score_repository.insert_score(doc) is not None
    assert await trust_score_repository.insert_score(dict(doc)) is None


async def test_insert_explanation_duplicate_returns_none():
    doc = {"submission_id": "TL-DUP-EXPL", "overall_result": "FAKE"}
    assert await explanation_repository.insert_explanation(doc) is not None
    assert await explanation_repository.insert_explanation(dict(doc)) is None


def test_is_approved_domain_rejects_invalid_urls():
    assert source_service.is_approved_domain("not-a-url") is False
    assert source_service.is_approved_domain("ftp://example.com/path") is False


def test_cosine_length_mismatch_returns_zero():
    assert similarity_service._cosine([1.0, 2.0], [1.0, 2.0, 3.0]) == 0.0


def test_compare_sentences_empty_text_falls_back():
    assert similarity_service.compare_sentences("", "some reference text") == 0.0


async def test_source_reliability_unknown_domains_zero():
    assert (
        await source_reliability_service.source_reliability(
            [{"source_domain": "totally-unknown-domain.example"}]
        )
        == 0.0
    )


def test_extract_claims_skips_non_factual_sentences():
    assert claim_service.extract_claims("quick brown fox jumps") == []
    assert claim_service._is_factual("quick brown fox jumps") is False


async def test_build_source_references_skips_missing_and_duplicate_domains():
    items = [
        {"source_domain": "who.int", "source_name": "WHO"},
        {"source_domain": "who.int", "source_name": "WHO"},
        {"source_name": "No domain"},
    ]
    refs = await evidence_explanation_service.build_source_references(items)
    assert len(refs) == 1
    assert refs[0]["domain"] == "who.int"
