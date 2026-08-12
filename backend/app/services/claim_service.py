import re

_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "so", "for",
    "of", "on", "in", "at", "by", "to", "with", "from", "as", "is", "are",
    "was", "were", "be", "been", "being", "has", "have", "had", "do", "does",
    "did", "will", "would", "can", "could", "should", "may", "might", "must",
    "not", "no", "nor", "only", "just", "very", "too", "more", "most", "less",
    "least", "this", "that", "these", "those", "it", "its", "he", "she", "they",
    "them", "their", "we", "us", "our", "you", "your", "i", "me", "my", "his",
    "her", "hers", "who", "whom", "which", "what", "when", "where", "why", "how",
    "about", "after", "before", "during", "between", "under", "over", "into",
    "onto", "said", "says", "according", "accordingly", "one", "two", "new",
}

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_NUMBER = re.compile(r"\d+(?:[.,]\d+)*%?")
_CAPITALIZED = re.compile(r"\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,}){0,2}\b")
_WORD = re.compile(r"[A-Za-z]{3,}")
_CLAIM_STOP = re.compile(
    r"\b(according to|reports|reported|reportedly|sources say|officials say|"
    r"experts say|studies show|research shows|news says|we can confirm)\b",
    re.IGNORECASE,
)


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    parts = [p.strip() for p in _SENTENCE_SPLIT.split(text)]
    return [p for p in parts if len(p) >= 6]


def _is_factual(sentence: str) -> bool:
    if _NUMBER.search(sentence):
        return True
    if _CAPITALIZED.findall(sentence):
        return True
    words = _WORD.findall(sentence)
    return len(words) >= 5


def _topics(sentence: str) -> list[str]:
    topics = []
    for match in _CAPITALIZED.findall(sentence):
        if not _CLAIM_STOP.search(match):
            topics.append(match)
    return topics[:6]


def _dates(sentence: str) -> list[str]:
    return re.findall(r"\b(?:19|20)\d{2}\b", sentence)


def _numbers(sentence: str) -> list[str]:
    return [m for m in _NUMBER.findall(sentence)]


def generate_keywords(text: str) -> list[str]:
    tokens = [t for t in _WORD.findall(text.lower()) if t not in _STOPWORDS]
    unique = list(dict.fromkeys(tokens))
    return unique[:12]


def extract_claims(text: str) -> list[dict]:
    claims = []
    for sentence in split_sentences(text):
        if not _is_factual(sentence):
            continue
        claims.append(
            {
                "text": sentence,
                "entities": _topics(sentence),
                "dates": _dates(sentence),
                "numbers": _numbers(sentence),
                "keywords": generate_keywords(sentence),
            }
        )
    return claims[:5]
