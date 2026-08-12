"""Build the binary LIAR dataset from raw TSV files.

    python tools/build_liar.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ai_loader  # noqa: E402

ai_loader.ensure_loaded()

from ai_engine.datasets.build_liar import build  # noqa: E402

if __name__ == "__main__":
    build()
