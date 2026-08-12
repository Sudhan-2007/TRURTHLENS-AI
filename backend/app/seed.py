from bson import ObjectId

from .db import get_verification_evidence_collection
from .models.news import utcnow
from .repositories import source_repository

DEFAULT_SOURCES = [
    {
        "name": "Centers for Disease Control and Prevention",
        "domain": "cdc.gov",
        "category": "Health",
        "country": "US",
        "source_type": "official",
        "trust_level": "high",
        "verification_method": "domain_verified",
    },
    {
        "name": "U.S. Food and Drug Administration",
        "domain": "fda.gov",
        "category": "Health",
        "country": "US",
        "source_type": "official",
        "trust_level": "high",
        "verification_method": "domain_verified",
    },
    {
        "name": "World Health Organization",
        "domain": "who.int",
        "category": "Health",
        "country": "Global",
        "source_type": "official",
        "trust_level": "high",
        "verification_method": "manual",
    },
    {
        "name": "NASA",
        "domain": "nasa.gov",
        "category": "Science",
        "country": "US",
        "source_type": "official",
        "trust_level": "high",
        "verification_method": "domain_verified",
    },
    {
        "name": "National Oceanic and Atmospheric Administration",
        "domain": "noaa.gov",
        "category": "Science",
        "country": "US",
        "source_type": "official",
        "trust_level": "high",
        "verification_method": "domain_verified",
    },
    {
        "name": "Bureau of Labor Statistics",
        "domain": "bls.gov",
        "category": "Economy",
        "country": "US",
        "source_type": "official",
        "trust_level": "high",
        "verification_method": "domain_verified",
    },
    {
        "name": "The White House",
        "domain": "whitehouse.gov",
        "category": "Government",
        "country": "US",
        "source_type": "official",
        "trust_level": "high",
        "verification_method": "domain_verified",
    },
    {
        "name": "United Nations",
        "domain": "un.org",
        "category": "International",
        "country": "Global",
        "source_type": "official",
        "trust_level": "high",
        "verification_method": "manual",
    },
    {
        "name": "PolitiFact",
        "domain": "politifact.com",
        "category": "Fact Check",
        "country": "US",
        "source_type": "fact_check",
        "trust_level": "high",
        "verification_method": "manual",
    },
    {
        "name": "Snopes",
        "domain": "snopes.com",
        "category": "Fact Check",
        "country": "US",
        "source_type": "fact_check",
        "trust_level": "high",
        "verification_method": "manual",
    },
    {
        "name": "FactCheck.org",
        "domain": "factcheck.org",
        "category": "Fact Check",
        "country": "US",
        "source_type": "fact_check",
        "trust_level": "high",
        "verification_method": "manual",
    },
    {
        "name": "Reuters",
        "domain": "reuters.com",
        "category": "News",
        "country": "Global",
        "source_type": "reputable_news",
        "trust_level": "medium",
        "verification_method": "manual",
    },
    {
        "name": "The Associated Press",
        "domain": "apnews.com",
        "category": "News",
        "country": "US",
        "source_type": "reputable_news",
        "trust_level": "medium",
        "verification_method": "manual",
    },
    {
        "name": "BBC News",
        "domain": "bbc.com",
        "category": "News",
        "country": "Global",
        "source_type": "reputable_news",
        "trust_level": "medium",
        "verification_method": "manual",
    },
]

DEFAULT_EVIDENCE = [
    {
        "claim": "Vaccines cause autism.",
        "evidence_summary": "Multiple large studies involving millions of children have found no link between vaccines and autism.",
        "evidence_status": "CONTRADICTED",
        "source_domain": "cdc.gov",
        "source_name": "Centers for Disease Control and Prevention",
        "source_url": "https://www.cdc.gov/vaccinesafety/concerns/autism.html",
        "source_title": "Vaccine Safety: Vaccines Do Not Cause Autism",
        "publication_date": None,
    },
    {
        "claim": "Global average temperatures have increased by more than one degree Fahrenheit since the late 19th century.",
        "evidence_summary": "NASA and NOAA analyses confirm the planet's average surface temperature has risen about 2 degrees Fahrenheit since 1880.",
        "evidence_status": "SUPPORTED",
        "source_domain": "nasa.gov",
        "source_name": "NASA",
        "source_url": "https://climate.nasa.gov/vital-signs/global-temperature/",
        "source_title": "Global Temperature",
        "publication_date": None,
    },
    {
        "claim": "The influenza vaccine guarantees you cannot get the flu.",
        "evidence_summary": "Flu vaccination is the best protection but does not guarantee immunity; effectiveness varies by season and strain.",
        "evidence_status": "PARTIALLY_SUPPORTED",
        "source_domain": "cdc.gov",
        "source_name": "Centers for Disease Control and Prevention",
        "source_url": "https://www.cdc.gov/flu/vaccines-work/burden.html",
        "source_title": "Vaccine Effectiveness: How Well Do the Flu Vaccines Work?",
        "publication_date": None,
    },
    {
        "claim": "The national unemployment rate in the United States fell below four percent.",
        "evidence_summary": "BLS data show the U.S. unemployment rate dropped below four percent in several recent years.",
        "evidence_status": "SUPPORTED",
        "source_domain": "bls.gov",
        "source_name": "Bureau of Labor Statistics",
        "source_url": "https://www.bls.gov/cps/",
        "source_title": "Labor Force Statistics",
        "publication_date": None,
    },
    {
        "claim": "The 2020 presidential election was stolen through widespread voter fraud.",
        "evidence_summary": "Federal and state election officials, courts, and audits found no evidence of widespread voter fraud that would change the outcome.",
        "evidence_status": "CONTRADICTED",
        "source_domain": "politifact.com",
        "source_name": "PolitiFact",
        "source_url": "https://www.politifact.com/article/2020/nov/20/our-committing-pants-fire-votes-are-rigged-republi/",
        "source_title": "No evidence of widespread voter fraud",
        "publication_date": None,
    },
    {
        "claim": "Earth is flat.",
        "evidence_summary": "Satellite imagery and direct observation confirm Earth is a round planet.",
        "evidence_status": "CONTRADICTED",
        "source_domain": "nasa.gov",
        "source_name": "NASA",
        "source_url": "https://science.nasa.gov/earth/",
        "source_title": "Earth Information Center",
        "publication_date": None,
    },
    {
        "claim": "Sea levels are rising at an accelerating rate.",
        "evidence_summary": "NOAA records show global sea level has risen about eight to nine inches since 1880 and the rate is accelerating.",
        "evidence_status": "SUPPORTED",
        "source_domain": "noaa.gov",
        "source_name": "National Oceanic and Atmospheric Administration",
        "source_url": "https://oceanservice.noaa.gov/facts/sealevel.html",
        "source_title": "Is sea level rising?",
        "publication_date": None,
    },
    {
        "claim": "The coronavirus was created in a laboratory by humans.",
        "evidence_summary": "WHO reports the virus likely has a natural animal origin; there is no scientific consensus that it was engineered.",
        "evidence_status": "CONTRADICTED",
        "source_domain": "who.int",
        "source_name": "World Health Organization",
        "source_url": "https://www.who.int/health-topics/coronavirus",
        "source_title": "Coronavirus disease (COVID-19)",
        "publication_date": None,
    },
    {
        "claim": "The national debt of the United States exceeds thirty trillion dollars.",
        "evidence_summary": "Treasury data reported by Reuters show the U.S. national debt passed thirty trillion dollars in early 2022.",
        "evidence_status": "SUPPORTED",
        "source_domain": "reuters.com",
        "source_name": "Reuters",
        "source_url": "https://www.reuters.com/business/us-national-debt-tops-30-trillion/",
        "source_title": "U.S. national debt tops $30 trillion",
        "publication_date": None,
    },
]

_EVIDENCE_DOMAINS = {d["domain"] for d in DEFAULT_SOURCES}


async def seed_default_sources() -> None:
    for source in DEFAULT_SOURCES:
        domain = source["domain"]
        if await source_repository.find_by_domain(domain) is not None:
            continue
        now = utcnow()
        doc = dict(source)
        doc.update(
            {
                "status": "trusted",
                "last_checked": now,
                "created_at": now,
                "updated_at": now,
            }
        )
        await source_repository.create_source(doc)


async def seed_default_evidence() -> None:
    collection = get_verification_evidence_collection()
    for entry in DEFAULT_EVIDENCE:
        existing = await collection.find_one(
            {"source_url": entry["source_url"], "claim": entry["claim"]}
        )
        if existing is not None:
            continue
        source = await source_repository.find_by_domain(entry["source_domain"])
        source_id: ObjectId | None = None
        if source is not None:
            source_id = source["_id"]
        doc = dict(entry)
        doc["source_id"] = source_id
        doc["source_domain"] = entry["source_domain"]
        doc["retrieved_at"] = utcnow()
        await collection.insert_one(doc)


async def seed_all() -> None:
    await seed_default_sources()
    await seed_default_evidence()
