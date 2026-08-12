from ..models.news import utcnow
from ..repositories import evidence_repository, source_repository


async def store_evidence(submission_id: str, evidence_items: list[dict]) -> None:
    if not evidence_items:
        return
    existing = await evidence_repository.find_by_submission_id(submission_id)
    seen = {(e["claim"], e["source_url"]) for e in existing}
    docs = []
    for item in evidence_items:
        key = (item["claim"], item["source_url"])
        if key in seen:
            continue
        seen.add(key)
        docs.append(
            {
                "submission_id": submission_id,
                "claim": item["claim"],
                "source_id": item.get("source_id"),
                "source_name": item["source_name"],
                "source_domain": item["source_domain"],
                "source_url": item["source_url"],
                "source_title": item.get("source_title"),
                "publication_date": item.get("publication_date"),
                "evidence_summary": item["evidence_summary"],
                "similarity_score": item["similarity_score"],
                "evidence_status": item["evidence_status"],
                "retrieved_at": utcnow(),
            }
        )
    await evidence_repository.insert_many(docs)


async def _join_sources(candidates: list[dict]) -> list[dict]:
    domains = {c.get("source_domain") for c in candidates if c.get("source_domain")}
    sources = {}
    for domain in domains:
        source = await source_repository.find_by_domain(domain)
        if source is not None:
            sources[domain] = source
    for candidate in candidates:
        candidate["source"] = sources.get(candidate.get("source_domain"))
    return candidates


async def search_internal(claims: list[dict], limit: int = 20) -> list[dict]:
    keywords: list[str] = []
    for claim in claims:
        keywords.extend(claim.get("keywords", []))
    candidates = await evidence_repository.find_candidates(keywords, limit=limit)
    return await _join_sources(candidates)
