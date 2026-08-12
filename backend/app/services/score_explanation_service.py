_LEVEL_REASON = {
    "HIGH": (
        "The claim is supported by multiple trusted sources and the retrieved "
        "evidence is strongly related to the submitted content."
    ),
    "MEDIUM": (
        "Some supporting evidence exists, but it is not strong enough for a "
        "high confidence conclusion."
    ),
    "LOW": "Evidence is limited or inconclusive, so the claim cannot be strongly endorsed.",
    "VERY_LOW": "Trusted evidence conflicts with the claim or indicates low credibility.",
}

_DISCLAIMER = (
    "This is an evidence-based indicator and not absolute proof that a claim "
    "is true or false."
)


def explain_trust_score(score: dict) -> str:
    level = score.get("trust_level", "VERY_LOW")
    final = int(score.get("final_score", 0))
    reason = _LEVEL_REASON.get(level, "")
    return f"The trust score is {level} ({final}/100). {reason} {_DISCLAIMER}"
