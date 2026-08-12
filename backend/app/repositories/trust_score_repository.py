from pymongo.errors import DuplicateKeyError

from ..db import get_trust_scores_collection


async def find_by_submission_id(submission_id: str) -> dict | None:
    return await get_trust_scores_collection().find_one(
        {"submission_id": submission_id}
    )


async def insert_score(doc: dict) -> dict | None:
    try:
        result = await get_trust_scores_collection().insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc
    except DuplicateKeyError:
        return None
