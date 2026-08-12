from ..db import get_verification_results_collection


async def upsert_result(doc: dict) -> None:
    await get_verification_results_collection().update_one(
        {"submission_id": doc["submission_id"]},
        {"$set": doc},
        upsert=True,
    )


async def find_by_submission_id(submission_id: str) -> dict | None:
    return await get_verification_results_collection().find_one(
        {"submission_id": submission_id}
    )
