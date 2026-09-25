from urllib.parse import urlparse

from ..models.news import utcnow
from ..repositories import verification_repository
from ..schemas.verification import VerificationStatus
from . import claim_service, evidence_service, similarity_service, source_service

SIMILARITY_CONFIRM = 0.55
SIMILARITY_PARTIAL = 0.30
MAX_CLAIMS = 3
MAX_EVIDENCE = 8

_TRUST_FACTOR = {"high": 1.0, "medium": 0.85, "low": 0.7}


async def verify_claims(claims: list[str]) -> dict:
    # Stateless verification for quick check
    candidates = await evidence_service.search_internal([{"text": c} for c in claims])
    return {
        "evidence_count": len(candidates),
        "verification_status": "Unverified"
        if not candidates
        else "Partially Supported",
    }


def _classify_evidence(claim_text: str, evidence: dict) -> dict | None:
    similarity = round(
        similarity_service.compare_sentences(claim_text, evidence["claim"]), 4
    )
    if similarity >= SIMILARITY_CONFIRM:
        status = evidence["evidence_status"]
    elif similarity >= SIMILARITY_PARTIAL:
        status = VerificationStatus.PARTIALLY_SUPPORTED.value
    else:
        return None

    source = evidence.get("source")
    return {
        "claim": claim_text,
        "source_id": evidence.get("source_id"),
        "source_name": (source or {}).get("name", evidence.get("source_name", "")),
        "source_domain": (source or {}).get(
            "domain", evidence.get("source_domain", "")
        ),
        "source_url": evidence.get("source_url"),
        "source_title": evidence.get("source_title"),
        "evidence_summary": evidence.get("evidence_summary"),
        "publication_date": evidence.get("publication_date"),
        "similarity_score": similarity,
        "evidence_status": status,
        "trust_level": (source or {}).get("trust_level", "high"),
    }


def _aggregate_status(items: list[dict]) -> str:
    contradicted = any(
        i["evidence_status"] == VerificationStatus.CONTRADICTED.value for i in items
    )
    supported = any(
        i["evidence_status"] == VerificationStatus.SUPPORTED.value for i in items
    )
    partial = any(
        i["evidence_status"] == VerificationStatus.PARTIALLY_SUPPORTED.value
        for i in items
    )

    if contradicted and supported:
        return VerificationStatus.PARTIALLY_SUPPORTED.value
    if contradicted:
        return VerificationStatus.CONTRADICTED.value
    if supported:
        return VerificationStatus.SUPPORTED.value
    if partial:
        return VerificationStatus.PARTIALLY_SUPPORTED.value
    return VerificationStatus.UNVERIFIED.value


def _verification_confidence(items: list[dict], status: str) -> float:
    if not items:
        return 0.0
    weighted = 0.0
    total_weight = 0.0
    for item in items:
        weight = _TRUST_FACTOR.get(item.get("trust_level", "high"), 0.9)
        weighted += item["similarity_score"] * weight
        total_weight += weight
    base = weighted / total_weight if total_weight else 0.0
    if (
        status == VerificationStatus.SUPPORTED.value
        or status == VerificationStatus.CONTRADICTED.value
    ):
        base = max(base, 0.60)
    elif status == VerificationStatus.PARTIALLY_SUPPORTED.value:
        base = min(max(base, 0.40), 0.75)
    else:
        base = min(base, 0.40)
    return round(base, 4)


async def verify_submission(submission: dict, prediction: dict, content: str) -> dict:
    claims = claim_service.extract_claims(content)[:MAX_CLAIMS]
    candidates = await evidence_service.search_internal(claims)

    items: list[dict] = []
    for claim in claims:
        for candidate in candidates:
            match = _classify_evidence(claim["text"], candidate)
            if match is not None:
                items.append(match)

    items = items[:MAX_EVIDENCE]

    status = _aggregate_status(items)
    confidence = _verification_confidence(items, status)
    official_sources = {
        item["source_domain"] for item in items if item.get("source_domain")
    }

    # Check submitted URL for official domain source
    sub_url = submission.get("url")
    if sub_url:
        sub_domain = urlparse(sub_url).netloc.lower()
        if source_service.is_approved_domain(sub_domain):
            official_sources.add(sub_domain)
            if status == VerificationStatus.UNVERIFIED.value:
                status = VerificationStatus.SUPPORTED.value
                confidence = max(confidence, 0.90)

    # Check search results from prediction
    search_results = prediction.get("search_results") if prediction else []
    if search_results:
        found_approved = False
        for sr in search_results:
            sr_url = sr.get("url", "")
            sr_domain = urlparse(sr_url).netloc.lower() if sr_url else ""
            if sr_domain and source_service.is_approved_domain(sr_domain):
                official_sources.add(sr_domain)
                found_approved = True
        if found_approved and status == VerificationStatus.UNVERIFIED.value:
            status = VerificationStatus.SUPPORTED.value
            confidence = max(confidence, 0.85)

    result = {
        "submission_id": submission["submission_id"],
        "user_id": submission["user_id"],
        "verification_status": status,
        "verification_confidence": confidence,
        "evidence_count": len(items),
        "official_source_count": len(official_sources),
        "average_similarity": round(
            sum(i["similarity_score"] for i in items) / len(items), 4
        )
        if items
        else 0.0,
        "sources": sorted(official_sources),
        "created_at": utcnow(),
    }

    await evidence_service.store_evidence(submission["submission_id"], items)
    await verification_repository.upsert_result(result)
    return result
