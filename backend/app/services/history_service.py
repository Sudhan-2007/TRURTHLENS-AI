import re

from bson import ObjectId
from fastapi import HTTPException, status

from ..db import (
    get_ai_predictions_collection,
    get_news_collection,
    get_trust_scores_collection,
    get_verification_results_collection,
)

MAX_LIMIT = 50

_ALLOWED_PREDICTIONS = {"REAL", "FAKE"}
_ALLOWED_STATUSES = {"SUPPORTED", "CONTRADICTED", "PARTIALLY_SUPPORTED", "UNVERIFIED"}
_ALLOWED_TRUST_LEVELS = {"HIGH", "MEDIUM", "LOW", "VERY_LOW"}
_ALLOWED_SORTS = {"created_desc", "created_asc"}


def _validate_params(prediction, verification_status, trust_level, sort) -> None:
    if prediction and prediction not in _ALLOWED_PREDICTIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid prediction filter '{prediction}'",
        )
    if verification_status and verification_status not in _ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid verification status filter '{verification_status}'",
        )
    if trust_level and trust_level not in _ALLOWED_TRUST_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid trust level filter '{trust_level}'",
        )
    if sort and sort not in _ALLOWED_SORTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort '{sort}'",
        )


async def _ids_with(collection, user: dict, extra: dict) -> list[str]:
    query = {**extra, "user_id": ObjectId(user["_id"])}
    cursor = collection.find(query, {"submission_id": 1})
    return [doc["submission_id"] async for doc in cursor]


async def _map_by_id(collection, submission_ids: list[str]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    if not submission_ids:
        return result
    cursor = collection.find({"submission_id": {"$in": submission_ids}})
    async for doc in cursor:
        result[doc["submission_id"]] = doc
    return result


async def enrich_items(docs: list[dict]) -> list[dict]:
    if not docs:
        return []
    ids = [doc["submission_id"] for doc in docs]
    ai = await _map_by_id(get_ai_predictions_collection(), ids)
    verification = await _map_by_id(get_verification_results_collection(), ids)
    trust = await _map_by_id(get_trust_scores_collection(), ids)

    items: list[dict] = []
    for doc in docs:
        items.append(
            {
                "submission_id": doc["submission_id"],
                "input_type": doc.get("input_type"),
                "content": doc.get("content"),
                "url": doc.get("url"),
                "title": doc.get("title"),
                "status": doc.get("status"),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at"),
                "ai_prediction": (ai.get(doc["submission_id"]) or {}).get("prediction"),
                "ai_confidence": (ai.get(doc["submission_id"]) or {}).get("confidence"),
                "verification_status": (
                    verification.get(doc["submission_id"]) or {}
                ).get("verification_status"),
                "verification_confidence": (
                    verification.get(doc["submission_id"]) or {}
                ).get("verification_confidence"),
                "trust_level": (trust.get(doc["submission_id"]) or {}).get(
                    "trust_level"
                ),
                "final_score": (trust.get(doc["submission_id"]) or {}).get(
                    "final_score"
                ),
            }
        )
    return items


async def list_history(
    user: dict,
    search: str | None = None,
    prediction: str | None = None,
    verification_status: str | None = None,
    trust_level: str | None = None,
    sort: str = "created_desc",
    limit: int = 20,
    skip: int = 0,
) -> dict:
    _validate_params(prediction, verification_status, trust_level, sort)
    limit = max(1, min(limit, MAX_LIMIT))
    skip = max(0, skip)

    query: dict = {"user_id": ObjectId(user["_id"])}

    if search and search.strip():
        pattern = re.escape(search.strip())
        query["$or"] = [
            {"content": {"$regex": pattern, "$options": "i"}},
            {"url": {"$regex": pattern, "$options": "i"}},
        ]

    if prediction:
        ids = await _ids_with(
            get_ai_predictions_collection(), user, {"prediction": prediction}
        )
        if not ids:
            return {"items": [], "total": 0, "limit": limit, "skip": skip}
        query["submission_id"] = {"$in": ids}

    if verification_status:
        ids = await _ids_with(
            get_verification_results_collection(),
            user,
            {"verification_status": verification_status},
        )
        if not ids:
            return {"items": [], "total": 0, "limit": limit, "skip": skip}
        query["submission_id"] = {"$in": ids}

    if trust_level:
        ids = await _ids_with(
            get_trust_scores_collection(), user, {"trust_level": trust_level}
        )
        if not ids:
            return {"items": [], "total": 0, "limit": limit, "skip": skip}
        query["submission_id"] = {"$in": ids}

    total = await get_news_collection().count_documents(query)
    direction = 1 if sort == "created_asc" else -1
    cursor = (
        get_news_collection()
        .find(query)
        .sort("created_at", direction)
        .skip(skip)
        .limit(limit)
    )
    docs = [doc async for doc in cursor]
    items = await enrich_items(docs)
    return {"items": items, "total": total, "limit": limit, "skip": skip}


async def get_history_detail(submission_id: str, user: dict) -> dict:
    doc = await get_news_collection().find_one({"submission_id": submission_id})
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
        )
    if str(doc["user_id"]) != str(user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this submission",
        )
    items = await enrich_items([doc])
    return items[0]
