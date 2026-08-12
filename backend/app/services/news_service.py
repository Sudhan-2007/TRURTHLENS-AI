from bson import ObjectId
from fastapi import HTTPException, status

from ..models.news import generate_submission_id, utcnow
from ..repositories import news_repository
from ..schemas.news import InputType, NewsStatus


async def create_submission(user: dict, input_type: str, content: str | None = None, url: str | None = None) -> dict:
    now = utcnow()
    doc = {
        "submission_id": generate_submission_id(),
        "user_id": ObjectId(user["_id"]),
        "input_type": input_type,
        "content": content,
        "url": url,
        "title": None,
        "source_name": None,
        "language": "en",
        "status": NewsStatus.SUBMITTED.value,
        "verification_result": None,
        "created_at": now,
        "updated_at": now,
    }
    return await news_repository.create_submission(doc)


async def get_submission(submission_id: str, user: dict) -> dict:
    doc = await news_repository.find_by_submission_id(submission_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
        )
    if str(doc["user_id"]) != str(user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this submission",
        )
    return doc


async def list_submissions(user: dict, limit: int = 20, skip: int = 0) -> list[dict]:
    return await news_repository.list_user_submissions(
        ObjectId(user["_id"]), limit=limit, skip=skip
    )


async def delete_submission(submission_id: str, user: dict) -> None:
    doc = await news_repository.find_by_submission_id(submission_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
        )
    if str(doc["user_id"]) != str(user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this submission",
        )
    await news_repository.delete_by_id_and_user(doc["_id"], ObjectId(user["_id"]))
