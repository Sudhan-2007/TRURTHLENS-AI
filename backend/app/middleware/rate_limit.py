from collections import defaultdict
from datetime import UTC, datetime

from fastapi import Depends, HTTPException, status

from .auth import get_current_user

_buckets: dict[str, list[float]] = defaultdict(list)

SUBMIT_LIMIT = 10
SUBMIT_WINDOW_SECONDS = 60

ANALYTICS_LIMIT = 30
ANALYTICS_WINDOW_SECONDS = 60


def clear_rate_limit_buckets() -> None:
    _buckets.clear()


def _check(user: dict, limit: int, window: int) -> None:
    now = datetime.now(UTC).timestamp()
    user_id = str(user["_id"])
    bucket = _buckets[user_id]
    bucket[:] = [ts for ts in bucket if now - ts < window]
    if len(bucket) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )
    bucket.append(now)


async def rate_limit_submit(user: dict = Depends(get_current_user)) -> dict:
    _check(user, SUBMIT_LIMIT, SUBMIT_WINDOW_SECONDS)
    return user


async def rate_limit_analytics(user: dict = Depends(get_current_user)) -> dict:
    _check(user, ANALYTICS_LIMIT, ANALYTICS_WINDOW_SECONDS)
    return user
