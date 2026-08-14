from fastapi import APIRouter, Depends, HTTPException, status

from ..middleware.auth import get_current_user, require_admin
from ..middleware.rate_limit import rate_limit_submit
from ..models.evidence import serialize_evidence
from ..models.official_source import serialize_official_source
from ..repositories import (
    evidence_repository,
    news_repository,
    source_repository,
    verification_repository,
)
from ..schemas.news import NewsStatus
from ..schemas.verification import SourceRegister
from ..services import ai_pipeline, source_service, verification_service

router = APIRouter(prefix="/api/verification", tags=["verification"])
sources_router = APIRouter(prefix="/api/sources", tags=["sources"])


async def _owned_completed_submission(submission_id: str, user: dict) -> dict:
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
async def verify_submission(
    submission_id: str,
    user: dict = Depends(rate_limit_submit),
):
    await _owned_completed_submission(submission_id, user)

    submission = await news_repository.find_by_submission_id(submission_id)
    if submission["status"] != NewsStatus.COMPLETED.value:
        await ai_pipeline.run_pipeline(submission_id)
        submission = await news_repository.find_by_submission_id(submission_id)

    prediction = submission.get("verification_result")
    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI detection produced no result for verification",
        )

    content = (submission.get("content") or "").strip()
    result = await verification_service.verify_submission(
        submission, prediction, content
    )
    result["id"] = str(result.pop("_id")) if result.get("_id") else None
    if result.get("user_id") is not None:
        result["user_id"] = str(result["user_id"])
    return result


@router.get("/{submission_id}", response_model=dict)
async def get_verification(
    submission_id: str,
    user: dict = Depends(get_current_user),
):
    await _owned_completed_submission(submission_id, user)

    result = await verification_repository.find_by_submission_id(submission_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verification result has been generated yet",
        )
    result["id"] = str(result.pop("_id"))
    if result.get("user_id") is not None:
        result["user_id"] = str(result["user_id"])
    return result


@router.get("/{submission_id}/evidence", response_model=dict)
async def get_evidence(
    submission_id: str,
    user: dict = Depends(get_current_user),
):
    await _owned_completed_submission(submission_id, user)

    items = await evidence_repository.find_by_submission_id(submission_id)
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No evidence has been collected for this submission",
        )
    serialized = [serialize_evidence(item) for item in items]
    return {
        "submission_id": submission_id,
        "count": len(serialized),
        "evidence": serialized,
    }


@sources_router.get("", response_model=dict)
async def list_sources(user: dict = Depends(get_current_user)):
    sources = await source_repository.list_sources()
    serialized = [serialize_official_source(source) for source in sources]
    return {"count": len(serialized), "sources": serialized}


@sources_router.post("", response_model=dict)
async def register_source(
    payload: SourceRegister,
    user: dict = Depends(require_admin),
):
    source = await source_service.register_source(payload)
    await source_service.refresh_approved_domains()
    return serialize_official_source(source)
