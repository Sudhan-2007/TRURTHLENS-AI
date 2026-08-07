from collections import defaultdict
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status

from .auth import get_current_user

_buckets: dict[str, list[float]] = defaultdict(list)

SUBMIT_LIMIT = 10
SUBMIT_WINDOW_SECONDS = 60


def clear_rate_limit_buckets() -> None:
    _buckets.clear()


async def rate_limit_submit(user: dict = Depends(get_current_user)) -> dict:
    now = datetime.now(timezone.utc).timestamp()
    user_id = str(user["_id"])
    bucket = _buckets[user_id]
    bucket[:] = [ts for ts in bucket if now - ts < SUBMIT_WINDOW_SECONDS]
    if len(bucket) >= SUBMIT_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )
    bucket.append(now)
    return user
