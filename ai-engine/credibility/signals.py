"""Linguistic signals that indicate misinformation or sensational content."""
import re

SENSATIONAL_WORDS = {
    "shocking", "bombshell", "explosive", "outrage", "insane", "unbelievable",
    "mind-blowing", "secretly", "they don't want you to know", "hidden truth",
    "conspiracy", "cover-up", "wake up", "doctors hate", "cure", "miracle",
    "instantly", "eliminate", "never seen before", "you won't believe",
    "the truth about", "exposed", "banned", "censored", "trap", "scam",
    "urgent", "breaking", "alert", "warning", "viral",
}

EMOTIONAL_WORDS = {
    "shock", "horror", "fear", "panic", "terror", "fury", "anger", "outrage",
    "disgust", "disturbing", "terrifying", "heartbreaking", "incredible",
    "amazing", "astonishing", "ridiculous", "absurd", "nightmare", "disaster",
}

CLICKBAIT_PATTERNS = [
    r"you won't believe",
    r"you won't know",
    r"what happens next",
    r"the (?:one|secret|crazy) (?:trick|thing|reason)",
    r"they (?:don't|do not) want you to (?:know|see)",
    r"this is (?:what|how)",
    r"\b\d+ (?:ways|reasons|signs|tricks)",
    r"number \d+",
    r"shocking",
    r"secret",
]

# Domain suffixes that indicate an official/government source globally.
OFFICIAL_DOMAIN_SUFFIXES = (
    ".gov", ".gov.in", ".gov.uk", ".gov.au", ".gov.ca", ".gov.sg", ".gov.za", ".go.jp",
    ".edu", ".edu.in", ".edu.au", ".edu.sg",
    ".nic.in",
    ".mil",
    ".int",
)

ALL_CAPS_WORD_RE = re.compile(r"\b[A-Z]{3,}\b")
EXCLAMATION_RE = re.compile(r"!")
QUOTE_RE = re.compile(r"[\"']")
NUMBER_RE = re.compile(r"\d")


def analyze_signals(text: str) -> dict:
    tokens = re.findall(r"\b[\w']+\b", text.lower())
    total_words = len(tokens)
    words = set(tokens)
    text_lower = text.lower()

    sensational = words & SENSATIONAL_WORDS
    emotional = words & EMOTIONAL_WORDS

    all_caps_words = ALL_CAPS_WORD_RE.findall(text)
    all_caps_ratio = len(all_caps_words) / total_words if total_words else 0.0

    exclamations = EXCLAMATION_RE.findall(text)
    exclamation_density = len(exclamations) / total_words if total_words else 0.0

    quote_ratio = len(QUOTE_RE.findall(text)) / total_words if total_words else 0.0

    clickbait = any(re.search(p, text_lower) for p in CLICKBAIT_PATTERNS)

    return {
        "sensational_words": sorted(sensational),
        "sensational_count": len(sensational),
        "emotional_words": sorted(emotional),
        "emotional_count": len(emotional),
        "all_caps_ratio": round(all_caps_ratio, 4),
        "exclamation_density": round(exclamation_density, 4),
        "quote_ratio": round(quote_ratio, 4),
        "clickbait": clickbait,
        "word_count": total_words,
        "has_numbers": bool(NUMBER_RE.search(text)),
    }


def credibility_score(text: str) -> float:
    """Return a 0.0–1.0 credibility score for *text*.

    A higher score means the language looks more credible (clean, professional).
    A lower score means the language looks sensational/clickbaity (typical of
    misinformation).  This score is used by the verdict-correction algorithm to
    decide how much to trust the ML model vs. official-source evidence.
    """
    signals = analyze_signals(text)

    # Start at 1.0 (fully credible) and deduct for red-flag signals.
    score = 1.0

    # Sensational words  (each one is a -0.08 penalty, up to -0.40)
    score -= min(signals["sensational_count"] * 0.08, 0.40)

    # Emotional words  (each one is -0.05, up to -0.25)
    score -= min(signals["emotional_count"] * 0.05, 0.25)

    # ALL-CAPS ratio  (0.10 ratio → -0.15)
    score -= min(signals["all_caps_ratio"] * 1.5, 0.20)

    # Exclamation density  (0.05 density → -0.15)
    score -= min(signals["exclamation_density"] * 3.0, 0.20)

    # Clickbait pattern detected → -0.15
    if signals["clickbait"]:
        score -= 0.15

    # Very short text is harder to judge → slight penalty
    if signals["word_count"] < 30:
        score -= 0.05

    return round(max(0.0, min(1.0, score)), 4)


def is_official_domain(domain: str) -> bool:
    """Return True if *domain* ends with a known government/official suffix."""
    domain = domain.lower().rstrip(".")
    for suffix in OFFICIAL_DOMAIN_SUFFIXES:
        if domain.endswith(suffix):
            return True
    return False

