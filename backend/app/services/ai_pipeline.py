from ..models.news import utcnow
from ..repositories import news_repository
from ..schemas.news import NewsStatus
from . import ai_service


async def run_pipeline(submission_id: str) -> None:
    """Run the AI detection pipeline for a submitted piece of news."""
    await news_repository.update_status(submission_id, NewsStatus.PROCESSING.value)

    try:
        submission = await news_repository.find_by_submission_id(submission_id)
        if submission is None:
            return

        content = (submission.get("content") or "").strip()
        if not content and submission.get("url"):
            content = await ai_service.extract_text_from_url(submission["url"])

        result = ai_service.analyze_text(content)
        result["analyzed_at"] = utcnow().isoformat()

        await ai_service.save_prediction(submission, result)
        await news_repository.update_status(
            submission_id,
            NewsStatus.COMPLETED.value,
            verification_result=result,
        )
    except Exception:
        await news_repository.update_status(submission_id, NewsStatus.FAILED.value)
        raise
