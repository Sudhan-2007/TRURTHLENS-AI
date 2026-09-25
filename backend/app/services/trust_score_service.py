from urllib.parse import urlparse

from ..models.news import utcnow
from ..repositories import trust_score_repository
from . import (
    evidence_score_service,
    score_calculator,
    source_reliability_service,
)

_LEVEL_REASON = {
    "HIGH": "The claim is supported by trusted official sources with strongly related evidence.",
    "MEDIUM": "Some supporting evidence exists, but additional verification may be useful.",
    "LOW": "Evidence is limited or inconclusive.",
    "VERY_LOW": "Trusted evidence conflicts with the claim or indicates low credibility.",
}

_DISCLAIMER = (
    "This is an evidence-based system indicator and not absolute proof that "
    "a claim is true or false."
)


def _explain(components: dict, final: int, level: str) -> str:
    reason = _LEVEL_REASON.get(level, "")
    details = (
        f"Component scores - AI assessment {components['ai_assessment']:.0f}, "
        f"official verification {components['official_verification']:.0f}, "
        f"evidence quality {components['evidence_quality']:.0f}, "
        f"source reliability {components['source_reliability']:.0f}, "
        f"semantic similarity {components['semantic_similarity']:.0f}."
    )
    return f"{level} trust score ({final}/100). {reason} {details} {_DISCLAIMER}"


async def calculate_trust_score(
    submission: dict, prediction: dict, verification: dict, evidence_items: list[dict]
) -> dict:
    sub_domain = None
    if submission.get("url"):
        sub_domain = urlparse(submission["url"]).netloc.lower()

    components = {
        "ai_assessment": score_calculator.ai_assessment(prediction),
        "official_verification": score_calculator.verification_score(verification),
        "evidence_quality": await evidence_score_service.evidence_quality(
            verification, evidence_items
        ),
        "source_reliability": await source_reliability_service.source_reliability(
            evidence_items, submission_domain=sub_domain
        ),
        "semantic_similarity": evidence_score_service.semantic_similarity(verification),
    }

    final = score_calculator.final_score(components)
    level = score_calculator.trust_level(final)

    doc = {
        "submission_id": submission["submission_id"],
        "user_id": submission["user_id"],
        "ai_score": components["ai_assessment"],
        "verification_score": components["official_verification"],
        "evidence_score": components["evidence_quality"],
        "source_reliability_score": components["source_reliability"],
        "similarity_score": components["semantic_similarity"],
        "final_score": final,
        "trust_level": level,
        "score_version": score_calculator.SCORE_VERSION,
        "explanation": _explain(components, final, level),
        "created_at": utcnow(),
    }

    stored = await trust_score_repository.insert_score(doc)
    if stored is not None:
        return stored
    existing = await trust_score_repository.find_by_submission_id(
        submission["submission_id"]
    )
    return existing if existing is not None else doc
