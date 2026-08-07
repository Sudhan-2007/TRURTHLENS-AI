from ..repositories import news_repository
from ..schemas.news import NewsStatus


async def run_pipeline(submission_id: str) -> None:
    """Phase 3 placeholder. Phase 4 will plug in the real AI analysis here."""
    await news_repository.update_status(submission_id, NewsStatus.PROCESSING.value)

    try:
        result = await analyze(submission_id)
        await news_repository.update_status(
            submission_id,
            NewsStatus.COMPLETED.value,
            verification_result=result,
        )
    except Exception:
        await news_repository.update_status(submission_id, NewsStatus.FAILED.value)
        raise


async def analyze(submission_id: str) -> dict:
    """Stub for the AI verification engine (implemented in Phase 4)."""
    return {
        "verdict": None,
        "confidence": None,
        "summary": "AI analysis pipeline connected. Full analysis arrives in Phase 4.",
    }
