import logging

from ..repositories import news_repository
from ..schemas.news import NewsStatus
from . import ai_service

logger = logging.getLogger("truthlens.pipeline")


async def run_pipeline(submission_id: str) -> None:
    """Run the AI detection pipeline for a submitted piece of news."""
    await news_repository.update_status(submission_id, NewsStatus.PROCESSING.value)

    try:
        submission = await news_repository.find_by_submission_id(submission_id)
        if submission is None:
            return

        if submission.get("input_type") == "account":
            result = ai_service.analyze_account(submission["url"])
        else:
            # If a URL is provided, extract content and verify source
            # Load article content if provided, otherwise empty string
            content = (submission.get("content") or "").strip()
            url_verified = False
            if submission.get("url"):
                try:
                    url_verified = ai_service.verify_url(submission["url"])
                except Exception:  # noqa: BLE001
                    url_verified = False

                if not content:
                    content = await ai_service.extract_text_from_url(submission["url"])

            result = ai_service.analyze_text(content)
            # Append URL verification flag to result
            result["url_verified"] = url_verified

        await ai_service.save_prediction(submission, result)
        await news_repository.update_status(
            submission_id,
            NewsStatus.COMPLETED.value,
            verification_result=result,
        )
    except Exception:
        logger.exception("pipeline failed submission=%s", submission_id)
        await news_repository.update_status(submission_id, NewsStatus.FAILED.value)
        raise
