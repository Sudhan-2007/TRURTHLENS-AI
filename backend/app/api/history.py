from fastapi import APIRouter, Depends, Query

from ..middleware.auth import get_current_user
from ..services import history_service

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=dict)
async def list_history(
    search: str | None = Query(default=None, max_length=200),
    prediction: str | None = None,
    verification_status: str | None = None,
    trust_level: str | None = None,
    sort: str = "created_desc",
    limit: int = Query(default=20, ge=1, le=50),
    skip: int = Query(default=0, ge=0),
    user: dict = Depends(get_current_user),
):
    return await history_service.list_history(
        user,
        search=search,
        prediction=prediction,
        verification_status=verification_status,
        trust_level=trust_level,
        sort=sort,
        limit=limit,
        skip=skip,
    )


@router.get("/{submission_id}", response_model=dict)
async def get_history_detail(
    submission_id: str,
    user: dict = Depends(get_current_user),
):
    return await history_service.get_history_detail(submission_id, user)
