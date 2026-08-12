from ..repositories import source_repository

LABELS = {
    "SUPPORTED": {
        "label": "Supported",
        "meaning": "Trusted evidence provides substantial support for the claim.",
    },
    "CONTRADICTED": {
        "label": "Contradicted",
        "meaning": "Trusted evidence conflicts with the claim.",
    },
    "PARTIALLY_SUPPORTED": {
        "label": "Partially Supported",
        "meaning": (
            "Some parts of the claim are supported while other parts are "
            "uncertain or conflicting."
        ),
    },
    "UNVERIFIED": {
        "label": "Unverified",
        "meaning": "Sufficient reliable evidence was not found.",
    },
}


def evidence_label(status: str) -> str:
    return LABELS.get(status, LABELS["UNVERIFIED"])["label"]


def evidence_meaning(status: str) -> str:
    return LABELS.get(status, LABELS["UNVERIFIED"])["meaning"]


async def build_evidence_summary(evidence_items: list[dict]) -> list[dict]:
    summary: list[dict] = []
    for item in evidence_items:
        status = item.get("evidence_status", "UNVERIFIED")
        summary.append(
            {
                "claim": item.get("claim"),
                "status": status,
                "label": evidence_label(status),
                "meaning": evidence_meaning(status),
                "similarity_score": item.get("similarity_score"),
                "evidence_summary": item.get("evidence_summary"),
                "source_name": item.get("source_name"),
                "source_domain": item.get("source_domain"),
                "source_url": item.get("source_url"),
                "source_title": item.get("source_title"),
                "publication_date": item.get("publication_date"),
            }
        )
    return summary


async def build_source_references(evidence_items: list[dict]) -> list[dict]:
    references: list[dict] = []
    seen: set[str] = set()
    for item in evidence_items:
        domain = item.get("source_domain")
        if not domain or domain in seen:
            continue
        seen.add(domain)
        source = await source_repository.find_by_domain(domain)
        references.append(
            {
                "name": item.get("source_name") or (source or {}).get("name"),
                "domain": domain,
                "url": item.get("source_url"),
                "title": item.get("source_title"),
                "trust_level": (source or {}).get(
                    "trust_level", item.get("trust_level", "high")
                ),
                "category": (source or {}).get("category"),
                "publication_date": item.get("publication_date"),
            }
        )
    return references
