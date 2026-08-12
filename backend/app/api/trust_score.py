from fastapi import APIRouter, Depends, HTTPException, status

from ..middleware.auth import get_current_user
from ..middleware.rate_limit import rate_limit_submit
from ..models.trust_score import serialize_trust_score
from ..repositories import (
    ai_repository,
    evidence_repository,
    news_repository,
    trust_score_repository,
    verification_repository,
)
from ..schemas.news import NewsStatus
from ..services import ai_pipeline, trust_score_service, verification_service

router = APIRouter(prefix="/api/trust-score", tags=["trust-score"])


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


@router.post("/{submission_id}", response_model=dict)
async def calculate_score(
    submission_id: str,
    user: dict = Depends(rate_limit_submit),
):
    await _owned_submission(submission_id, user)

    existing = await trust_score_repository.find_by_submission_id(submission_id)
    if existing is not None:
        return serialize_trust_score(existing)

    submission = await news_repository.find_by_submission_id(submission_id)
    if submission["status"] != NewsStatus.COMPLETED.value:
        await ai_pipeline.run_pipeline(submission_id)
        submission = await news_repository.find_by_submission_id(submission_id)

    prediction = await ai_repository.find_by_submission_id(submission_id)
    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI detection produced no result for scoring",
        )

    verification = await verification_repository.find_by_submission_id(submission_id)
    if verification is None:
        content = (submission.get("content") or "").strip()
        verification = await verification_service.verify_submission(
            submission, prediction, content
        )

    evidence_items = await evidence_repository.find_by_submission_id(submission_id)
    score = await trust_score_service.calculate_trust_score(
        submission, prediction, verification, evidence_items
    )
    return serialize_trust_score(score)


@router.get("/{submission_id}", response_model=dict)
async def get_score(
    submission_id: str,
    user: dict = Depends(get_current_user),
):
    await _owned_submission(submission_id, user)

    score = await trust_score_repository.find_by_submission_id(submission_id)
    if score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No trust score has been calculated for this submission",
        )
    return serialize_trust_score(score)
