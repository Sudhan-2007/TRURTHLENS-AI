import re

# Transformer models can use contextual information from punctuation and
# stopwords, so we intentionally do NOT strip stopwords or punctuation here.

_WS_RE = re.compile(r"\s+")
_TOKEN_RE = re.compile(r"\b\w+\b")


def clean_text(text: str) -> str:
    """Remove unnecessary whitespace, normalize text and handle special characters."""
    if not text:
        return ""
    text = text.strip()
    text = text.replace("\r", " ").replace("\n", " ")
    text = text.replace("\t", " ")
    text = _WS_RE.sub(" ", text)
    return text


def normalize_text(text: str) -> str:
    """Normalize case while preserving content for transformer input."""
    return clean_text(text)


def tokenize_text(text: str) -> list[str]:
    """Return a list of lowercase word tokens."""
    return _TOKEN_RE.findall(clean_text(text).lower())


def validate_length(text: str) -> bool:
    length = len(clean_text(text))
    return 20 <= length <= 10000
