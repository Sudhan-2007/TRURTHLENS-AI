def serialize_evidence(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    if doc.get("source_id") is not None:
        doc["source_id"] = str(doc["source_id"])
    if doc.get("submission_id") is not None:
        doc["submission_id"] = str(doc["submission_id"])
    return doc
