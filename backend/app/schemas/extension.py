from pydantic import BaseModel


class QuickVerifyRequest(BaseModel):
    url: str | None = None
    text: str | None = None


class QuickVerifyResponse(BaseModel):
    score: float | None
    classification: str
    confidence: float
    evidence_count: int
    summary: str
