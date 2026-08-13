from pathlib import Path
import os

AI_ENGINE_ROOT = Path(__file__).resolve().parents[1]

DATASETS_DIR = AI_ENGINE_ROOT / "datasets"
MODELS_DIR = AI_ENGINE_ROOT / "models"
EVALUATION_DIR = AI_ENGINE_ROOT / "evaluation"
DEMO_DATASET_PATH = DATASETS_DIR / "demo_fake_news.csv"
LIAR_RAW_DIR = DATASETS_DIR / "raw" / "liar"
LIAR_TRAIN_PATH = DATASETS_DIR / "liar_binary_train.csv"
LIAR_TEST_PATH = DATASETS_DIR / "liar_binary_test.csv"

# Model backend: "baseline" (fast, works anywhere) or "distilbert".
# Override at runtime with the TRUTHLENS_MODEL_BACKEND environment variable.
MODEL_BACKEND = os.environ.get("TRUTHLENS_MODEL_BACKEND", "distilbert")

BASELINE_MODEL_DIR = MODELS_DIR / "baseline"
BASELINE_VECTORIZER_PATH = BASELINE_MODEL_DIR / "vectorizer.pkl"
BASELINE_MODEL_PATH = BASELINE_MODEL_DIR / "model.pkl"
BASELINE_METRICS_PATH = EVALUATION_DIR / "baseline_report.json"

# DistilBERT checkpoint location. Override at runtime with AI_MODEL_PATH so a
# deployment can point at a mounted/served model directory.
_distilbert_override = os.environ.get("AI_MODEL_PATH", "").strip()
DISTILBERT_MODEL_DIR = Path(_distilbert_override) if _distilbert_override else MODELS_DIR / "distilbert"
DISTILBERT_BASE_MODEL = "distilbert-base-uncased"
NUM_LABELS = 2
CLASS_LABELS = ["REAL", "FAKE"]

# Training defaults (tune on validation / hardware)
MAX_SEQUENCE_LENGTH = 256
TRAIN_EPOCHS = 3
TRAIN_BATCH_SIZE = 16
TRAIN_LEARNING_RATE = 2e-5
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.1

# Confidence policy (Phase 4 spec)
CONFIDENCE_HIGH = 0.80
CONFIDENCE_MEDIUM = 0.60

TEXT_MIN_LENGTH = 20
TEXT_MAX_LENGTH = 10000
