def serialize_trust_score(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    if doc.get("user_id") is not None:
        doc["user_id"] = str(doc["user_id"])
    return doc
