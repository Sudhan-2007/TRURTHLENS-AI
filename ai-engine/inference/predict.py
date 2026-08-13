"""Model-agnostic fake-news prediction service."""
import time

import joblib

from ..config import (
    BASELINE_MODEL_PATH,
    BASELINE_VECTORIZER_PATH,
    CLASS_LABELS,
    DISTILBERT_MODEL_DIR,
    MODEL_BACKEND,
)
from ..preprocessing.text import clean_text


class FakeNewsPredictor:
    def __init__(self, backend: str = MODEL_BACKEND):
        self.backend = backend
        self._baseline = None
        self._transformer = None

    def _load_baseline(self):
        if self._baseline is None:
            self._baseline = {
                "vectorizer": joblib.load(BASELINE_VECTORIZER_PATH),
                "model": joblib.load(BASELINE_MODEL_PATH),
            }
        return self._baseline

    def _load_transformer(self):
        if self._transformer is None:
            try:
                import torch  # noqa: F401
            except ImportError:
                raise RuntimeError("PyTorch is not installed; cannot use distilbert backend")
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            try:
                self._transformer = {
                    "tokenizer": AutoTokenizer.from_pretrained(str(DISTILBERT_MODEL_DIR)),
                    "model": AutoModelForSequenceClassification.from_pretrained(
                        str(DISTILBERT_MODEL_DIR)
                    ),
                }
            except OSError as exc:
                raise RuntimeError(
                    f"DistilBERT model not found at {DISTILBERT_MODEL_DIR}; "
                    "falling back to baseline backend"
                ) from exc
        return self._transformer

    def _predict_baseline(self, text: str) -> tuple[str, float]:
        assets = self._load_baseline()
        vec = assets["vectorizer"].transform([text])
        proba = assets["model"].predict_proba(vec)[0]
        idx = int(proba.argmax())
        confidence = float(proba[idx])
        return CLASS_LABELS[idx], confidence

    def _predict_transformer(self, text: str) -> tuple[str, float]:
        import torch

        assets = self._load_transformer()
        inputs = assets["tokenizer"](
            text, truncation=True, max_length=256, return_tensors="pt"
        )
        with torch.no_grad():
            logits = assets["model"](**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0].numpy()
        idx = int(probs.argmax())
        return CLASS_LABELS[idx], float(probs[idx])

    def predict(self, text: str, model_version: str = "1.0.0") -> dict:
        start = time.perf_counter()
        cleaned = clean_text(text)
        if not cleaned:
            raise ValueError("Empty input after preprocessing")

        backend = self.backend
        if backend == "distilbert":
            try:
                prediction, confidence = self._predict_transformer(cleaned)
            except RuntimeError:
                backend = "baseline"
                prediction, confidence = self._predict_baseline(cleaned)
        else:
            prediction, confidence = self._predict_baseline(cleaned)

        return {
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "model_name": "DistilBERT" if backend == "distilbert" else "TF-IDF+LogisticRegression",
            "model_version": model_version,
            "processing_time_ms": int((time.perf_counter() - start) * 1000),
        }
