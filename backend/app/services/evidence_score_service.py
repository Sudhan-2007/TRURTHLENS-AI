from .score_calculator import clamp


def semantic_similarity(verification: dict | None) -> float:
    if not verification:
        return 0.0
    average = verification.get("average_similarity")
    if average is None:
        return 0.0
    return round(clamp(float(average) * 100.0), 2)


async def evidence_quality(
    verification: dict | None, evidence_items: list[dict]
) -> float:
    if not evidence_items:
        return 0.0

    average = None
    if verification and verification.get("average_similarity") is not None:
        average = float(verification["average_similarity"])
    else:
        scores = [float(i.get("similarity_score") or 0.0) for i in evidence_items]
        if scores:
            average = sum(scores) / len(scores)

    similarity = clamp((average or 0.0) * 100.0)
    count_component = clamp(min(len(evidence_items) / 2.0, 1.0) * 100.0)
    return round(0.7 * similarity + 0.3 * count_component, 2)
