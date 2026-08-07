from datetime import datetime, timezone
from secrets import token_hex

from bson import ObjectId


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def generate_submission_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"TL-{ts}-{token_hex(3).upper()}"


def serialize_news(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    if doc.get("user_id") is not None:
        doc["user_id"] = str(doc["user_id"])
    return doc


def to_object_id(value: str) -> ObjectId:
    return ObjectId(value)
