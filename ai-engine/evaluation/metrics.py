"""Model evaluation utilities."""
import json

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from ..config import CLASS_LABELS


def evaluate_classification(y_true, y_score, y_pred=None, labels=None):
    """Compute standard metrics. y_score is the probability of the FAKE class."""
    y_true = np.asarray(y_true)
    if y_pred is None:
        y_pred = (np.asarray(y_score) >= 0.5).astype(int)

    report = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, labels=labels, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, labels=labels, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, labels=labels, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
        "roc_auc": float(roc_auc_score(y_true, y_score)),
    }
    return report


def save_report(report: dict, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(f"Saved evaluation report to {path}")
