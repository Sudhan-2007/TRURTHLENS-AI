from ..models.news import utcnow
from ..repositories import explanation_repository
from . import (
    evidence_explanation_service,
    score_explanation_service,
    summary_service,
)

EXPLANATION_VERSION = "1.0"

_LIMITATIONS_BASE = [
    "AI predictions can contain errors.",
    "Source availability may change over time.",
    "An absence of evidence does not automatically prove a claim is false.",
    "The trust score is an evidence-based indicator and not absolute proof that a claim is true or false.",
]


def _ai_explanation(prediction: dict) -> str:
    prediction_value = prediction.get("prediction")
    confidence = float(prediction.get("confidence") or 0.0)
    model_name = prediction.get("model_name", "AI model")
    model_version = prediction.get("model_version", "unknown")
    label = (
        "consistent with credible reporting"
        if prediction_value == "REAL"
        else "potentially misleading"
    )
    return (
        f"The AI model ({model_name} v{model_version}) classified the submitted "
        f"text as {label} with {confidence:.0%} confidence. This is a model "
        "prediction, not a definitive judgment about the truth of the claim."
    )


def _verification_explanation(verification: dict) -> str:
    status = verification.get("verification_status", "UNVERIFIED")
    confidence = float(verification.get("verification_confidence") or 0.0)
    evidence_count = verification.get("evidence_count", 0)
    source_count = verification.get("official_source_count", 0)

    if status == "SUPPORTED":
        base = "An approved official source contains information that supports the submitted claim."
    elif status == "CONTRADICTED":
        base = "An approved official source contains information that conflicts with the submitted claim."
    elif status == "PARTIALLY_SUPPORTED":
        base = (
            "Some parts of the claim are supported by trusted evidence while "
            "other parts are uncertain or conflicting."
        )
    else:
        base = (
            "Sufficient reliable evidence matching the submitted claim was not found."
        )

    return (
        f"{base} This assessment is based on {evidence_count} matched evidence "
        f"record(s) from {source_count} trusted source(s), with "
        f"{confidence:.0%} confidence."
    )


def _limitations(verification: dict) -> list[str]:
    limitations = list(_LIMITATIONS_BASE)
    if verification.get("verification_status") == "UNVERIFIED":
        limitations.append(
            "Unverified claims have not been proven false; they simply lack confirmed evidence."
        )
    return limitations


async def generate_explanation(
    submission: dict,
    prediction: dict,
    verification: dict,
    trust_score: dict,
    evidence_items: list[dict],
) -> dict:
    evidence_summary = await evidence_explanation_service.build_evidence_summary(
        evidence_items
    )
    source_references = await evidence_explanation_service.build_source_references(
        evidence_items
    )

    doc = {
        "submission_id": submission["submission_id"],
        "user_id": submission["user_id"],
        "overall_result": summary_service.overall_result(
            prediction, verification, trust_score
        ),
        "ai_explanation": _ai_explanation(prediction),
        "verification_explanation": _verification_explanation(verification),
        "trust_score_explanation": score_explanation_service.explain_trust_score(
            trust_score
        ),
        "evidence_summary": evidence_summary,
        "source_references": source_references,
        "limitations": _limitations(verification),
        "explanation_version": EXPLANATION_VERSION,
        "created_at": utcnow(),
        "components": {
            "prediction": prediction.get("prediction"),
            "confidence": prediction.get("confidence"),
            "model_name": prediction.get("model_name"),
            "model_version": prediction.get("model_version"),
            "verification_status": verification.get("verification_status"),
            "verification_confidence": verification.get("verification_confidence"),
            "final_score": trust_score.get("final_score"),
            "trust_level": trust_score.get("trust_level"),
        },
    }

    stored = await explanation_repository.insert_explanation(doc)
    if stored is not None:
        return stored
    existing = await explanation_repository.find_by_submission_id(
        submission["submission_id"]
    )
    return existing if existing is not None else doc
