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
