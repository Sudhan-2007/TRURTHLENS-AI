from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..middleware.auth import get_optional_user
from ..repositories import feedback_repository, news_repository
from ..schemas.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

class StatsResponse(BaseModel):
    total_feedback: int
    average_rating: float

@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback: FeedbackCreate,
    user: dict | None = Depends(get_optional_user),
):
    submission = await news_repository.find_by_submission_id(feedback.submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )
        
    user_id = str(user["_id"]) if user else None
    
    doc = await feedback_repository.save_feedback(user_id, feedback)
    
    return FeedbackResponse(
        id=str(doc["_id"]),
        submission_id=doc["submission_id"],
        rating=doc["rating"],
        comments=doc.get("comments"),
        alternative_sources=doc.get("alternative_sources"),
        user_id=str(doc["user_id"]) if doc.get("user_id") else None,
        created_at=doc["created_at"]
    )

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    return await feedback_repository.get_feedback_stats()
