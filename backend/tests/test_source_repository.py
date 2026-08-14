from app.db import get_official_sources_collection
from app.repositories import source_repository


async def test_find_by_id_with_invalid_objectid_returns_none():
    assert await source_repository.find_by_id("not-an-objectid") is None


async def test_find_by_id_returns_document():
    doc = await get_official_sources_collection().find_one({"domain": "who.int"})
    found = await source_repository.find_by_id(str(doc["_id"]))
    assert found is not None
    assert found["domain"] == "who.int"


async def test_find_by_domain_lowercases_query():
    assert await source_repository.find_by_domain("WHO.INT") is not None
    assert await source_repository.find_by_domain("nonexistent.example") is None


async def test_list_sources_no_filters_returns_all_seeded():
    sources = await source_repository.list_sources()
    assert len(sources) >= 14


async def test_list_sources_filters_by_source_type():
    official = await source_repository.list_sources(source_type="official")
    assert len(official) == 8
    assert all(s["source_type"] == "official" for s in official)


async def test_list_sources_filters_by_status_and_type():
    sources = await source_repository.list_sources(
        status="trusted", source_type="fact_check"
    )
    assert isinstance(sources, list)
    assert all(s.get("status") == "trusted" for s in sources)


async def test_count_sources_total_and_filtered():
    assert await source_repository.count_sources() >= 14
    assert await source_repository.count_sources(status="trusted") == 14
    assert await source_repository.count_sources(status="banned") == 0
