def serialize_prediction(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    if doc.get("user_id") is not None:
        doc["user_id"] = str(doc["user_id"])
    # Preserve new fields if they exist
    for field in ["url_verified", "search_results", "synthesized_answer"]:
        if field in doc:
            # ensure JSON‑serialisable (search_results already dict list, synthesized_answer string)
            doc[field] = doc[field]
    return doc
