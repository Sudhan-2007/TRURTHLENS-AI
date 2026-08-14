import pytest

from app.services.evidence_score_service import evidence_quality, semantic_similarity


def test_semantic_similarity_without_verification_is_zero():
    assert semantic_similarity(None) == 0.0


def test_semantic_similarity_without_average_is_zero():
    assert semantic_similarity({}) == 0.0
    assert semantic_similarity({"verification_status": "SUPPORTED"}) == 0.0


def test_semantic_similarity_returns_percentage():
    assert semantic_similarity({"average_similarity": 0.5}) == 50.0
    assert semantic_similarity({"average_similarity": 1.5}) == 100.0


async def test_evidence_quality_without_items_is_zero():
    assert await evidence_quality({}, []) == 0.0


async def test_evidence_quality_uses_verification_average():
    verification = {"average_similarity": 0.8}
    items = [{"similarity_score": 0.2}, {"similarity_score": 0.2}]
    assert await evidence_quality(verification, items) == pytest.approx(
        0.7 * 80.0 + 0.3 * 100.0
    )


async def test_evidence_quality_falls_back_to_item_scores():
    items = [{"similarity_score": 0.6}, {"similarity_score": 0.8}]
    score = await evidence_quality(None, items)
    assert score == pytest.approx(0.7 * 70.0 + 0.3 * 100.0)
