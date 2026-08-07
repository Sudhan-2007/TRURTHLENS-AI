from datetime import datetime, timezone

from bson import ObjectId

from ..db import get_news_collection


async def create_submission(doc: dict) -> dict:
    result = await get_news_collection().insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


async def find_by_submission_id(submission_id: str) -> dict | None:
    return await get_news_collection().find_one({"submission_id": submission_id})


async def find_by_id_and_user(doc_id: ObjectId, user_id: ObjectId) -> dict | None:
    return await get_news_collection().find_one({"_id": doc_id, "user_id": user_id})


async def update_status(
    submission_id: str, status: str, **extra
) -> None:
    update = {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}}
    if extra:
        update["$set"].update(extra)
    await get_news_collection().update_one(
        {"submission_id": submission_id}, update
    )


async def delete_by_id_and_user(doc_id: ObjectId, user_id: ObjectId) -> bool:
    result = await get_news_collection().delete_one({"_id": doc_id, "user_id": user_id})
    return result.deleted_count > 0


async def list_user_submissions(
    user_id: ObjectId, limit: int = 20, skip: int = 0
) -> list[dict]:
    cursor = (
        get_news_collection()
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    return [doc async for doc in cursor]
