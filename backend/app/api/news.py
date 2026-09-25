from fastapi import APIRouter, BackgroundTasks, Depends, status

from ..middleware.auth import get_current_user
from ..middleware.rate_limit import rate_limit_submit
from ..models.news import serialize_news
from ..schemas.news import (
    NewsOut,
    NewsStatus,
    NewsSubmitAccount,
    NewsSubmitText,
    NewsSubmitUrl,
)
from ..services import ai_pipeline, news_service

router = APIRouter(prefix="/api/news", tags=["news"])


@router.post("/submit", status_code=status.HTTP_201_CREATED, response_model=dict)
async def submit_text(
    payload: NewsSubmitText,
    background_tasks: BackgroundTasks,
    user: dict = Depends(rate_limit_submit),
):
    submission = await news_service.create_submission(
        user, input_type="text", content=payload.content
    )
    background_tasks.add_task(ai_pipeline.run_pipeline, submission["submission_id"])
    return {
        "submission_id": submission["submission_id"],
        "status": NewsStatus.SUBMITTED.value,
        "message": "News submitted successfully",
    }


@router.post("/submit-url", status_code=status.HTTP_201_CREATED, response_model=dict)
async def submit_url(
    payload: NewsSubmitUrl,
    background_tasks: BackgroundTasks,
    user: dict = Depends(rate_limit_submit),
):
    submission = await news_service.create_submission(
        user, input_type="url", url=payload.url
    )
    background_tasks.add_task(ai_pipeline.run_pipeline, submission["submission_id"])
    return {
        "submission_id": submission["submission_id"],
        "status": NewsStatus.SUBMITTED.value,
        "message": "URL submitted successfully",
    }


@router.post(
    "/submit-account", status_code=status.HTTP_201_CREATED, response_model=dict
)
async def submit_account(
    payload: NewsSubmitAccount,
    background_tasks: BackgroundTasks,
    user: dict = Depends(rate_limit_submit),
):
    submission = await news_service.create_submission(
        user, input_type="account", url=payload.url
    )
    background_tasks.add_task(ai_pipeline.run_pipeline, submission["submission_id"])
    return {
        "submission_id": submission["submission_id"],
        "status": NewsStatus.SUBMITTED.value,
        "message": "Account URL submitted successfully",
    }


@router.get("/history", response_model=list[NewsOut])
async def list_history(
    limit: int = 20,
    skip: int = 0,
    user: dict = Depends(get_current_user),
):
    docs = await news_service.list_submissions(user, limit, skip)
    return [serialize_news(doc) for doc in docs]


@router.get("/{submission_id}", response_model=NewsOut)
async def get_submission(submission_id: str, user: dict = Depends(get_current_user)):
    doc = await news_service.get_submission(submission_id, user)
    return serialize_news(doc)


@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_submission(submission_id: str, user: dict = Depends(get_current_user)):
    await news_service.delete_submission(submission_id, user)
