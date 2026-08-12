from fastapi import APIRouter, Depends, HTTPException, status

from ..middleware.auth import get_current_user
from ..middleware.rate_limit import rate_limit_submit
from ..models.explanation import serialize_explanation
from ..repositories import (
    ai_repository,
    evidence_repository,
    explanation_repository,
    news_repository,
    trust_score_repository,
    verification_repository,
)
from ..schemas.news import NewsStatus
from ..services import (
    ai_pipeline,
    explanation_service,
    trust_score_service,
    verification_service,
)

router = APIRouter(prefix="/api/explanation", tags=["explanation"])


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
async def generate_explanation(
    submission_id: str,
    user: dict = Depends(rate_limit_submit),
):
    await _owned_submission(submission_id, user)

    existing = await explanation_repository.find_by_submission_id(submission_id)
    if existing is not None:
        return serialize_explanation(existing)

    submission = await news_repository.find_by_submission_id(submission_id)
    if submission["status"] != NewsStatus.COMPLETED.value:
        await ai_pipeline.run_pipeline(submission_id)
        submission = await news_repository.find_by_submission_id(submission_id)

    prediction = await ai_repository.find_by_submission_id(submission_id)
    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI detection produced no result for explanation",
        )

    verification = await verification_repository.find_by_submission_id(submission_id)
    if verification is None:
        content = (submission.get("content") or "").strip()
        verification = await verification_service.verify_submission(
            submission, prediction, content
        )

    evidence_items = await evidence_repository.find_by_submission_id(submission_id)

    trust_score = await trust_score_repository.find_by_submission_id(submission_id)
    if trust_score is None:
        trust_score = await trust_score_service.calculate_trust_score(
            submission, prediction, verification, evidence_items
        )

    explanation = await explanation_service.generate_explanation(
        submission, prediction, verification, trust_score, evidence_items
    )
    return serialize_explanation(explanation)


@router.get("/{submission_id}", response_model=dict)
async def get_explanation(
    submission_id: str,
    user: dict = Depends(get_current_user),
):
    await _owned_submission(submission_id, user)

    explanation = await explanation_repository.find_by_submission_id(submission_id)
    if explanation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No explanation has been generated for this submission",
        )
    return serialize_explanation(explanation)
