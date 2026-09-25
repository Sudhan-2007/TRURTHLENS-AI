from bson import ObjectId

from ..db import get_feedback_collection
from ..models.news import utcnow
from ..schemas.feedback import FeedbackCreate


async def save_feedback(user_id: str | None, feedback: FeedbackCreate) -> dict:
    collection = get_feedback_collection()
    doc = feedback.model_dump()
    doc["user_id"] = ObjectId(user_id) if user_id else None
    doc["created_at"] = utcnow()

    result = await collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


async def get_feedback_stats() -> dict:
    collection = get_feedback_collection()
    total = await collection.count_documents({})
    if total == 0:
        return {"total_feedback": 0, "average_rating": 0.0}

    pipeline = [{"$group": {"_id": None, "avgRating": {"$avg": "$rating"}}}]
    cursor = collection.aggregate(pipeline)
    result = await cursor.to_list(length=1)

    avg = round(result[0]["avgRating"], 2) if result else 0.0
    return {"total_feedback": total, "average_rating": avg}
