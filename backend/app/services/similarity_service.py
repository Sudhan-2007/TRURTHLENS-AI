import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

_vectorizer: TfidfVectorizer | None = None


def _get_vectorizer() -> TfidfVectorizer:
    global _vectorizer
    if _vectorizer is None:
        _vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_features=50000,
            stop_words="english",
        )
    return _vectorizer


def _fit(texts: list[str]) -> list[list[float]]:
    vectorizer = _get_vectorizer()
    matrix = vectorizer.fit_transform(texts)
    return matrix.toarray().tolist()


def _cosine(vec_a: list[float], vec_b: list[float]) -> float:
    if len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    if dot == 0.0:
        return 0.0
    na = sum(a * a for a in vec_a) ** 0.5
    nb = sum(b * b for b in vec_b) ** 0.5
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def compare(text_a: str, text_b: str) -> float:
    vectors = _fit([text_a, text_b])
    return _cosine(vectors[0], vectors[1])


def compare_sentences(text: str, reference: str) -> float:
    """Compare each sentence of text against reference and return the best score."""
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    if not sentences:
        return compare(text, reference)
    best = 0.0
    for sentence in sentences:
        score = compare(sentence, reference)
        if score > best:
            best = score
    return best
