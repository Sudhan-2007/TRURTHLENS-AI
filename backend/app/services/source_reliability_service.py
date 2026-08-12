from ..repositories import source_repository
from .score_calculator import clamp

_TRUST_TO_SCORE = {"high": 100.0, "medium": 80.0, "low": 60.0}


async def source_reliability(evidence_items: list[dict]) -> float:
    domains = {i.get("source_domain") for i in evidence_items if i.get("source_domain")}
    if not domains:
        return 0.0

    scores = []
    for domain in domains:
        source = await source_repository.find_by_domain(domain)
        if source is None:
            continue
        trust_level = source.get("trust_level", "high")
        scores.append(_TRUST_TO_SCORE.get(trust_level, 60.0))

    if not scores:
        return 0.0
    return round(clamp(sum(scores) / len(scores)), 2)
