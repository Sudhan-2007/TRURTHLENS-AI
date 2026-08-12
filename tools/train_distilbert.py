"""Run DistilBERT fine-tuning from the project root.

    python tools/train_distilbert.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ai_loader  # noqa: E402

ai_loader.ensure_loaded()

from ai_engine.training.train_distilbert import main  # noqa: E402

if __name__ == "__main__":
    main()
