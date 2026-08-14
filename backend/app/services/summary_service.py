def overall_result(ai_prediction: dict, verification: dict, trust_score: dict) -> str:
    status = verification.get("verification_status", "UNVERIFIED")

    if status == "SUPPORTED":
        return "Trusted official evidence substantially supports the submitted claim."
    if status == "CONTRADICTED":
        return (
            "The claim requires caution because trusted evidence conflicts with "
            "important parts of the submitted content."
        )
    if status == "PARTIALLY_SUPPORTED":
        return (
            "The claim is only partially supported: some parts are backed by "
            "trusted evidence while other parts remain uncertain or conflicting."
        )
    return (
        "Sufficient trusted evidence was not found to confirm or refute the "
        "submitted claim. This does not mean the claim is false."
    )
