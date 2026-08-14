from datetime import UTC, datetime

from bson import ObjectId


def utcnow() -> datetime:
    return datetime.now(UTC)


def serialize_user(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    doc.pop("password_hash", None)
    return doc


def to_object_id(value: str) -> ObjectId:
    return ObjectId(value)
