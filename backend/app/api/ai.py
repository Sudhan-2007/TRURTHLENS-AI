from fastapi import APIRouter, Depends, HTTPException, status

from ..middleware.auth import get_current_user
from ..middleware.rate_limit import rate_limit_submit
from ..models.ai_prediction import serialize_prediction
from ..repositories import ai_repository, news_repository
from ..schemas.news import NewsStatus
from ..services import ai_pipeline, ai_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/model-info")
async def model_info():
    return ai_service.get_model_info()


async def _owned_submission(submission_id: str, user: dict) -> dict:
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


@router.post("/detect/{submission_id}", response_model=dict)
async def run_detection(
    submission_id: str,
    user: dict = Depends(rate_limit_submit),
):
    await _owned_submission(submission_id, user)

    submission = await news_repository.find_by_submission_id(submission_id)
    if submission["status"] != NewsStatus.COMPLETED.value:
        await ai_pipeline.run_pipeline(submission_id)

    prediction = await ai_repository.find_by_submission_id(submission_id)
    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI detection produced no result",
        )
    return serialize_prediction(prediction)


@router.get("/prediction/{submission_id}", response_model=dict)
async def get_prediction(
    submission_id: str,
    user: dict = Depends(get_current_user),
):
    await _owned_submission(submission_id, user)

    prediction = await ai_repository.find_by_submission_id(submission_id)
    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No prediction has been generated yet",
        )
    return serialize_prediction(prediction)
