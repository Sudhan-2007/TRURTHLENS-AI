from datetime import UTC, datetime, timedelta

from bson import ObjectId

from ..db import (
    get_ai_predictions_collection,
    get_news_collection,
    get_official_sources_collection,
    get_trust_scores_collection,
    get_users_collection,
    get_verification_results_collection,
)


def user_filter(user_id: str | None) -> dict:
    if not user_id:
        return {}
    return {"user_id": ObjectId(user_id)}


async def count_users() -> int:
    return await get_users_collection().count_documents({})


async def count_active_users() -> int:
    ids = await get_news_collection().distinct("user_id")
    return len(ids)


async def count_news(query: dict) -> int:
    return await get_news_collection().count_documents(query)


async def count_news_status(status: str, query: dict) -> int:
    return await get_news_collection().count_documents({**query, "status": status})


async def count_verification_status(status: str, query: dict) -> int:
    return await get_verification_results_collection().count_documents(
        {**query, "verification_status": status}
    )


async def count_prediction(prediction: str, query: dict) -> int:
    return await get_ai_predictions_collection().count_documents(
        {**query, "prediction": prediction}
    )


async def count_sources() -> int:
    return await get_official_sources_collection().count_documents({})


async def average_trust_score(query: dict) -> float:
    cursor = get_trust_scores_collection().aggregate(
        [
            {"$match": query},
            {"$group": {"_id": None, "avg": {"$avg": "$final_score"}}},
        ]
    )
    docs = await cursor.to_list(length=1)
    if not docs:
        return 0.0
    return round(float(docs[0]["avg"]), 2)


async def _distribution(collection, field: str, query: dict) -> list[dict]:
    cursor = collection.aggregate(
        [
            {"$match": query},
            {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
        ]
    )
    docs = await cursor.to_list(length=100000)
    return [{"value": d["_id"], "count": d["count"]} for d in docs]


async def verification_distribution(query: dict) -> list[dict]:
    return await _distribution(
        get_verification_results_collection(), "verification_status", query
    )


async def trust_distribution(query: dict) -> list[dict]:
    return await _distribution(get_trust_scores_collection(), "trust_level", query)


async def prediction_distribution(query: dict) -> list[dict]:
    return await _distribution(get_ai_predictions_collection(), "prediction", query)


_FORMATS = {
    "daily": "%Y-%m-%d",
    "weekly": "%G-W%V",
    "monthly": "%Y-%m",
}


async def _trend_counts(collection, query: dict, period: str) -> list[dict]:
    fmt = _FORMATS[period]
    cursor = collection.aggregate(
        [
            {"$match": query},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": fmt,
                            "date": "$created_at",
                            "timezone": "UTC",
                        }
                    },
                    "count": {"$sum": 1},
                }
            },
        ]
    )
    docs = await cursor.to_list(length=100000)
    return [{"period": d["_id"], "count": d["count"]} for d in docs]


def _fill_periods(rows: list[dict], period: str) -> list[dict]:
    today = datetime.now(UTC).date()
    counts = {row["period"]: row["count"] for row in rows}

    if period == "daily":
        labels = [
            (today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(13, -1, -1)
        ]
    elif period == "weekly":
        year, week, _ = today.isocalendar()
        current = (
            datetime.strptime(f"{year}-W{week:02d}-1", "%G-W%V-%u")
            .replace(tzinfo=UTC)
            .date()
        )
        labels = [
            f"{y}-W{w:02d}"
            for y, w, _ in [
                (current - timedelta(weeks=i)).isocalendar() for i in range(7, -1, -1)
            ]
        ]
    else:
        month = today.replace(day=1)
        labels = []
        for i in range(5, -1, -1):
            labels.append(month.strftime("%Y-%m"))
            month = (month.replace(day=1) - timedelta(days=1)).replace(day=1)
        labels.reverse()

    return [{"period": label, "count": counts.get(label, 0)} for label in labels]


async def verification_trend(query: dict, period: str) -> list[dict]:
    rows = await _trend_counts(get_verification_results_collection(), query, period)
    return _fill_periods(rows, period)
