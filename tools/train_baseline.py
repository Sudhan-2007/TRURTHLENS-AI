"""Run the TF-IDF baseline training from the project root.

    python tools/train_baseline.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ai_loader  # noqa: E402

ai_loader.ensure_loaded()

from ai_engine.training.train_baseline import main  # noqa: E402

if __name__ == "__main__":
    main()
