"""Bootstrap for importing the ai-engine package.

The on-disk directory is 'ai-engine', which is not a valid Python identifier,
so it is registered under the valid package name 'ai_engine' with its __path__
pointing at the ai-engine directory. Relative imports inside ai-engine resolve
through this package, letting both the backend and training scripts share the
same code.
"""
import sys
import types

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_AI_ENGINE = _ROOT / "ai-engine"


def ensure_loaded():
    if "ai_engine" in sys.modules:
        return sys.modules["ai_engine"]
    # The ai-engine directory is NOT added to sys.path, otherwise the local
    # 'datasets' folder would shadow the third-party 'datasets' package. The
    # package is registered in sys.modules instead, so its __path__ is used.
    pkg = types.ModuleType("ai_engine")
    pkg.__path__ = [str(_AI_ENGINE)]
    pkg.__package__ = "ai_engine"
    sys.modules["ai_engine"] = pkg
    return pkg
