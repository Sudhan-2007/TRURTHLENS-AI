from app.schemas.explanation import ExplanationType
from app.schemas.history import HistorySort
from app.schemas.trust_score import TrustLevel


def test_response_schema_enums():
    assert [e.value for e in ExplanationType] == [
        "AI_EXPLANATION",
        "SOURCE_EXPLANATION",
        "EVIDENCE_EXPLANATION",
        "SCORE_EXPLANATION",
        "FINAL_SUMMARY",
    ]
    assert [e.value for e in HistorySort] == ["created_desc", "created_asc"]
    assert [e.value for e in TrustLevel] == ["HIGH", "MEDIUM", "LOW", "VERY_LOW"]
