"""Bridge between the FastAPI backend and the ai-engine package.

The ai-engine directory lives at the repo root and is imported under the valid
package name 'ai_engine' via tools/ai_loader.py. Model files are loaded lazily so
the API can start even if the models have not been trained yet.
"""

import json
import os
import re
import sys
from pathlib import Path

import httpx

from ..config import settings

if settings.AI_MODEL_PATH:
    os.environ.setdefault("AI_MODEL_PATH", settings.AI_MODEL_PATH)

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_TOOLS = _PROJECT_ROOT / "tools"

if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import ai_loader

ai_loader.ensure_loaded()

from ai_engine.config import (
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
    MODEL_BACKEND,
    TEXT_MAX_LENGTH,
    TEXT_MIN_LENGTH,
)
from ai_engine.inference.predict import FakeNewsPredictor

from ..db import get_ai_predictions_collection
from ..models.news import utcnow
from ..monitoring import metrics

_predictor: FakeNewsPredictor | None = None

MODEL_VERSION = "1.0.0"


def _get_predictor() -> FakeNewsPredictor:
    global _predictor
    if _predictor is None:
        _predictor = FakeNewsPredictor(backend=MODEL_BACKEND)
        info = _predictor.model_info if hasattr(_predictor, "model_info") else {}
        metrics.record_ai_model_info(
            info.get("model_name", "unknown"),
            info.get("model_version", "unknown"),
            info.get("backend", MODEL_BACKEND),
        )
    return _predictor


def preload_model() -> None:
    """Preload the AI model into memory."""
    _get_predictor()


def model_available() -> dict:
    """Return model availability/version info without triggering a full load."""
    from ai_engine.config import DISTILBERT_MODEL_DIR

    return {
        "loaded": _predictor is not None,
        "backend": MODEL_BACKEND,
        "distilbert_trained": (DISTILBERT_MODEL_DIR / "config.json").exists(),
        "model_version": MODEL_VERSION,
    }


def _summary(verdict: str, confidence: float, model_name: str) -> str:
    if verdict == "REAL":
        return (
            f"The model classified this text as REAL with {confidence:.0%} confidence "
            f"using {model_name}. It found the language consistent with credible reporting."
        )
    return (
        f"The model classified this text as FAKE with {confidence:.0%} confidence "
        f"using {model_name}. It found language patterns typical of misinformation."
    )


def confidence_level(confidence: float) -> str:
    """Map a confidence value to the policy levels from the Phase 4 spec."""
    if confidence >= CONFIDENCE_HIGH:
        return "high"
    if confidence >= CONFIDENCE_MEDIUM:
        return "medium"
    return "low"


def analyze_text(text: str) -> dict:
    cleaned = (text or "").strip()
    if len(cleaned) < TEXT_MIN_LENGTH:
        raise ValueError(
            f"Content must be at least {TEXT_MIN_LENGTH} characters long to analyze"
        )
    try:
        result = _get_predictor().predict(cleaned, model_version=MODEL_VERSION)
    except Exception:
        metrics.record_ai_error()
        raise
    low_confidence = confidence_level(result["confidence"]) == "low"
    metrics.record_ai_inference(
        prediction=result["prediction"],
        model_name=result["model_name"],
        model_version=result["model_version"],
        duration_ms=result["processing_time_ms"],
        low_confidence=low_confidence,
        backend=MODEL_BACKEND,
    )
    return {
        "verdict": result["prediction"],
        "confidence": result["confidence"],
        "confidence_level": confidence_level(result["confidence"]),
        "model_name": result["model_name"],
        "model_version": result["model_version"],
        "processing_time_ms": result["processing_time_ms"],
        "summary": _summary(
            result["prediction"], result["confidence"], result["model_name"]
        ),
    }


async def extract_text_from_url(url: str) -> str:
    headers = {"User-Agent": "TruthLens-AI/1.0 (+research)"}
    async with httpx.AsyncClient(
        timeout=15.0, follow_redirects=True, headers=headers
    ) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        html = resp.text

    html = re.sub(
        r"<script[\s\S]*?</script>|<style[\s\S]*?</style>",
        " ",
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(r"<[^>]+>", " ", html)
    html = re.sub(r"&nbsp;|&#160;", " ", html, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", html).strip()
    return text[:TEXT_MAX_LENGTH]


async def save_prediction(submission: dict, result: dict) -> None:
    await get_ai_predictions_collection().update_one(
        {"submission_id": submission["submission_id"]},
        {
            "$set": {
                "user_id": submission["user_id"],
                "input_type": submission.get("input_type"),
                "prediction": result["verdict"],
                "confidence": result["confidence"],
                "confidence_level": result["confidence_level"],
                "model_name": result["model_name"],
                "model_version": result["model_version"],
                "processing_time_ms": result["processing_time_ms"],
                "created_at": utcnow(),
            }
        },
        upsert=True,
    )


def _load_report(path: Path) -> dict | None:
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def get_model_info() -> dict:
    from ai_engine.config import (
        BASELINE_METRICS_PATH,
        DISTILBERT_MODEL_DIR,
        EVALUATION_DIR,
        MODEL_BACKEND,
    )

    return {
        "active_backend": MODEL_BACKEND,
        "labels": ["REAL", "FAKE"],
        "baseline_report": _load_report(BASELINE_METRICS_PATH),
        "distilbert_report": _load_report(EVALUATION_DIR / "distilbert_report.json"),
        "distilbert_trained": (DISTILBERT_MODEL_DIR / "config.json").exists(),
    }
