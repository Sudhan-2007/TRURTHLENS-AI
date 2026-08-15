from datetime import datetime

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    submission_id: str = Field(..., description="The ID of the news submission being reviewed.")
    rating: int = Field(..., ge=1, le=5, description="User rating from 1 to 5 stars.")
    comments: str | None = Field(None, description="Optional user comments explaining the rating.")
    alternative_sources: list[str] | None = Field(None, description="Optional list of alternative source URLs provided by the user.")

class FeedbackResponse(FeedbackCreate):
    id: str
    user_id: str | None
    created_at: datetime
