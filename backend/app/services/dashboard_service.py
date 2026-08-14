from ..db import get_news_collection
from ..repositories import analytics_repository
from . import analytics_service, history_service


async def _recent(query: dict, limit: int = 5) -> list[dict]:
    cursor = get_news_collection().find(query).sort("created_at", -1).limit(limit)
    docs = [doc async for doc in cursor]
    return await history_service.enrich_items(docs)


async def user_dashboard(user: dict) -> dict:
    query = analytics_repository.user_filter(str(user["_id"]))
    return {
        "total_submissions": await analytics_repository.count_news(query),
        "completed_verifications": await analytics_repository.count_news_status(
            "completed", query
        ),
        "fake_predictions": await analytics_repository.count_prediction("FAKE", query),
        "real_predictions": await analytics_repository.count_prediction("REAL", query),
        "unverified_claims": await analytics_repository.count_verification_status(
            "UNVERIFIED", query
        ),
        "average_trust_score": await analytics_repository.average_trust_score(query),
        "recent_verifications": await _recent(query),
    }


async def user_statistics(user: dict) -> dict:
    query = analytics_repository.user_filter(str(user["_id"]))
    return await analytics_service.charts(query)


async def admin_dashboard() -> dict:
    query: dict = {}
    return {
        "total_users": await analytics_repository.count_users(),
        "active_users": await analytics_repository.count_active_users(),
        "total_submissions": await analytics_repository.count_news(query),
        "completed_verifications": await analytics_repository.count_news_status(
            "completed", query
        ),
        "failed_verifications": await analytics_repository.count_news_status(
            "failed", query
        ),
        "fake_predictions": await analytics_repository.count_prediction("FAKE", query),
        "real_predictions": await analytics_repository.count_prediction("REAL", query),
        "unverified_claims": await analytics_repository.count_verification_status(
            "UNVERIFIED", query
        ),
        "average_trust_score": await analytics_repository.average_trust_score(query),
        "official_sources": await analytics_repository.count_sources(),
        "recent_verifications": await _recent(query),
    }


async def admin_statistics() -> dict:
    return await analytics_service.charts({})
