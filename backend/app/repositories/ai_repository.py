from ..db import get_ai_predictions_collection


async def find_by_submission_id(submission_id: str) -> dict | None:
    return await get_ai_predictions_collection().find_one(
        {"submission_id": submission_id}
    )
