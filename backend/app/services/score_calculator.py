WEIGHTS = {
    "ai_assessment": 0.30,
    "official_verification": 0.35,
    "evidence_quality": 0.20,
    "source_reliability": 0.10,
    "semantic_similarity": 0.05,
}

VERIFICATION_MAPPING = {
    "SUPPORTED": 100.0,
    "PARTIALLY_SUPPORTED": 60.0,
    "UNVERIFIED": 40.0,
    "CONTRADICTED": 0.0,
}

SCORE_VERSION = "1.0"


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    if value is None:
        return low
    return max(low, min(high, value))


def ai_assessment(prediction: dict | None) -> float:
    if not prediction:
        return 0.0
    verdict = prediction.get("prediction")
    confidence = prediction.get("confidence")
    if verdict not in ("REAL", "FAKE") or confidence is None:
        return 0.0
    if verdict == "REAL":
        return round(clamp(confidence * 100.0), 2)
    return round(clamp((1.0 - confidence) * 100.0), 2)


def verification_score(verification: dict | None) -> float:
    if not verification:
        return 0.0
    status = verification.get("verification_status")
    return round(clamp(VERIFICATION_MAPPING.get(status, 0.0)), 2)


def final_score(components: dict) -> int:
    total = 0.0
    for name, weight in WEIGHTS.items():
        value = components.get(name, 0.0)
        if value is None:
            value = 0.0
        total += clamp(value) * weight
    return int(round(total))


def trust_level(score: int) -> str:
    if score >= 80:
        return "HIGH"
    if score >= 60:
        return "MEDIUM"
    if score >= 40:
        return "LOW"
    return "VERY_LOW"
