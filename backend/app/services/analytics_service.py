from ..repositories import analytics_repository
from ..schemas.dashboard import TrendPeriod

_VERIFICATION_STATUSES = [
    "SUPPORTED",
    "CONTRADICTED",
    "PARTIALLY_SUPPORTED",
    "UNVERIFIED",
]
_TRUST_LEVELS = ["HIGH", "MEDIUM", "LOW", "VERY_LOW"]
_PREDICTIONS = ["REAL", "FAKE"]


def _fill_distribution(rows: list[dict], keys: list[str]) -> list[dict]:
    counts = {row["value"]: row["count"] for row in rows}
    return [{"value": key, "count": counts.get(key, 0)} for key in keys]


async def verification_distribution(query: dict) -> list[dict]:
    rows = await analytics_repository.verification_distribution(query)
    return _fill_distribution(rows, _VERIFICATION_STATUSES)


async def trust_distribution(query: dict) -> list[dict]:
    rows = await analytics_repository.trust_distribution(query)
    return _fill_distribution(rows, _TRUST_LEVELS)


async def prediction_distribution(query: dict) -> list[dict]:
    rows = await analytics_repository.prediction_distribution(query)
    return _fill_distribution(rows, _PREDICTIONS)


async def verification_trend(query: dict) -> dict:
    return {
        TrendPeriod.DAILY.value: await analytics_repository.verification_trend(
            query, TrendPeriod.DAILY.value
        ),
        TrendPeriod.WEEKLY.value: await analytics_repository.verification_trend(
            query, TrendPeriod.WEEKLY.value
        ),
        TrendPeriod.MONTHLY.value: await analytics_repository.verification_trend(
            query, TrendPeriod.MONTHLY.value
        ),
    }


async def charts(query: dict) -> dict:
    return {
        "verification_distribution": await verification_distribution(query),
        "trust_score_distribution": await trust_distribution(query),
        "prediction_distribution": await prediction_distribution(query),
        "verification_trend": await verification_trend(query),
    }
