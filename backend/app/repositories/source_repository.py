from bson import ObjectId

from ..db import get_official_sources_collection


async def create_source(doc: dict) -> dict:
    result = await get_official_sources_collection().insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


async def find_by_domain(domain: str) -> dict | None:
    return await get_official_sources_collection().find_one(
        {"domain": domain.lower()}
    )


async def find_by_id(source_id: str) -> dict | None:
    try:
        oid = ObjectId(source_id)
    except Exception:
        return None
    return await get_official_sources_collection().find_one({"_id": oid})


async def list_sources(
    status: str | None = None, source_type: str | None = None
) -> list[dict]:
    query: dict = {}
    if status:
        query["status"] = status
    if source_type:
        query["source_type"] = source_type
    cursor = get_official_sources_collection().find(query).sort("name", 1)
    return [doc async for doc in cursor]


async def count_sources(status: str | None = None) -> int:
    query = {"status": status} if status else {}
    return await get_official_sources_collection().count_documents(query)
