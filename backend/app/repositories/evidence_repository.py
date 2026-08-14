from ..db import get_verification_evidence_collection


async def insert_many(docs: list[dict]) -> None:
    if not docs:
        return
    await get_verification_evidence_collection().insert_many(docs)


async def find_by_submission_id(submission_id: str) -> list[dict]:
    cursor = get_verification_evidence_collection().find(
        {"submission_id": submission_id}
    )
    return [doc async for doc in cursor]


async def find_candidates(keywords: list[str], limit: int = 20) -> list[dict]:
    if not keywords:
        return []
    terms = [k.lower() for k in keywords if len(k) >= 3]
    if not terms:
        return []
    or_clauses = [
        {"claim": {"$regex": re_escape(term), "$options": "i"}} for term in terms[:8]
    ]
    cursor = (
        get_verification_evidence_collection().find({"$or": or_clauses}).limit(limit)
    )
    return [doc async for doc in cursor]


def re_escape(term: str) -> str:
    import re

    return re.escape(term)
