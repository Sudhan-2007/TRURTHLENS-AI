"""Performance smoke tests for Phase 9 quality gates.

Thresholds are deliberately generous to stay stable on CI but catch
pathological regressions (e.g. accidental blocking/serialization).
"""

import asyncio
import time

from app.db import get_news_collection

from .conftest import auth_headers, register_user
from .test_news import submit_text

SUPPORTED_TEXT = (
    "Global average temperatures have increased by more than one degree Fahrenheit "
    "since the late 19th century. Scientists at NASA have confirmed the planet is "
    "getting warmer every decade."
)


def _elapsed(start: float) -> float:
    return time.perf_counter() - start


async def _wait_completed(sid: str, timeout: float = 15.0) -> dict:
    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        doc = await get_news_collection().find_one({"submission_id": sid})
        if doc and doc.get("status") in ("completed", "failed"):
            return doc
        await asyncio.sleep(0.2)
    raise AssertionError(f"submission {sid} did not finish within {timeout}s")


async def test_health_endpoint_fast(client):
    start = time.perf_counter()
    res = await client.get("/api/health")
    assert res.status_code == 200
    assert _elapsed(start) < 0.5


async def test_auth_flow_fast(client):
    start = time.perf_counter()
    res = await register_user(client)
    assert res.status_code == 201
    headers = await auth_headers(client)
    assert headers
    assert _elapsed(start) < 2.0


async def test_submit_pipeline_within_budget(client):
    await register_user(client)
    headers = await auth_headers(client)
    start = time.perf_counter()
    res = await submit_text(client, headers, content=SUPPORTED_TEXT)
    assert res.status_code == 201
    sid = res.json()["submission_id"]
    doc = await _wait_completed(sid)
    assert doc["status"] == "completed"
    assert _elapsed(start) < 15.0


async def test_history_query_fast(client):
    await register_user(client)
    headers = await auth_headers(client)
    for _ in range(3):
        await submit_text(client, headers, content=SUPPORTED_TEXT)
    start = time.perf_counter()
    res = await client.get("/api/history", headers=headers)
    assert res.status_code == 200
    assert res.json()["total"] == 3
    assert _elapsed(start) < 1.0
