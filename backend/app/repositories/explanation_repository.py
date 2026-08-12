from pymongo.errors import DuplicateKeyError

from ..db import get_ai_explanations_collection


async def find_by_submission_id(submission_id: str) -> dict | None:
    return await get_ai_explanations_collection().find_one(
        {"submission_id": submission_id}
    )


async def insert_explanation(doc: dict) -> dict | None:
    try:
        result = await get_ai_explanations_collection().insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc
    except DuplicateKeyError:
        return None
