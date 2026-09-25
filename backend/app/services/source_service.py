from urllib.parse import urlparse

from ..models.news import utcnow
from ..repositories import source_repository
from ..schemas.verification import SourceStatus

_APPROVED_DOMAINS: set[str] = set()

DEFAULT_TRUSTED_DOMAINS: set[str] = {
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "bbc.co.uk",
    "pib.gov.in",
    "afp.com",
    "bloomberg.com",
    "thehindu.com",
    "indianexpress.com",
    "timesofindia.indiatimes.com",
    "ndtv.com",
    "nytimes.com",
    "wsj.com",
    "washingtonpost.com",
    "cbsnews.com",
    "nbcnews.com",
    "cnn.com",
    "npr.org",
    "factcheck.org",
    "snopes.com",
    "fullfact.org",
    "altnews.in",
    "politifact.com",
}


def set_approved_domains(domains: list[str]) -> None:
    _APPROVED_DOMAINS.clear()
    _APPROVED_DOMAINS.update(d.lower() for d in domains)


def is_approved_domain(url: str) -> bool:
    if not url:
        return False
    if "://" not in url:
        url = "https://" + url
    parsed = urlparse(url)
    domain = parsed.hostname
    if not domain:
        return False
    domain = domain.lower()
    if domain.endswith((".gov", ".edu", ".gov.in", ".gov.uk", ".mil")):
        return True
    all_approved = _APPROVED_DOMAINS | DEFAULT_TRUSTED_DOMAINS
    for approved in all_approved:
        if domain == approved or domain.endswith("." + approved):
            return True
    return False


async def register_source(payload) -> dict:
    domain = payload.domain.lower()
    existing = await source_repository.find_by_domain(domain)
    if existing is not None:
        return existing
    now = utcnow()
    doc = {
        "name": payload.name,
        "domain": domain,
        "category": payload.category,
        "country": payload.country,
        "source_type": payload.source_type.value,
        "trust_level": payload.trust_level.value,
        "status": SourceStatus.TRUSTED.value,
        "verification_method": payload.verification_method.value,
        "last_checked": now,
        "created_at": now,
        "updated_at": now,
    }
    return await source_repository.create_source(doc)


async def refresh_approved_domains() -> None:
    trusted = await source_repository.list_sources(status=SourceStatus.TRUSTED.value)
    set_approved_domains([s["domain"] for s in trusted])
