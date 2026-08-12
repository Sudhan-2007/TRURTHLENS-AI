def serialize_official_source(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    if doc.get("source_id") is not None:
        doc["source_id"] = str(doc["source_id"])
    return doc
