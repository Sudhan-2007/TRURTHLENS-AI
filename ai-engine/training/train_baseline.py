"""Train a fast TF-IDF + LogisticRegression baseline classifier.

Serves as the working default model and as the baseline comparison required by
the evaluation section of Phase 4. Fine-tuned DistilBERT (train_distilbert.py)
can be selected via config.MODEL_BACKEND once trained.
"""
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from ..config import (
    BASELINE_METRICS_PATH,
    BASELINE_MODEL_DIR,
    BASELINE_MODEL_PATH,
    BASELINE_VECTORIZER_PATH,
    LIAR_TEST_PATH,
    TEST_SIZE,
)
from ..datasets.prepare import default_train_path, load_dataset
from ..evaluation.metrics import evaluate_classification, save_report


def main():
    train_df = load_dataset(default_train_path())

    X_train = train_df["text"].tolist()
    y_train = train_df["label_id"].values

    if LIAR_TEST_PATH.exists():
        test_df = load_dataset(LIAR_TEST_PATH)
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X_train, y_train, test_size=TEST_SIZE, stratify=y_train, random_state=42
        )
        test_df = None

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=50000)
    X_train_vec = vectorizer.fit_transform(X_train)

    model = LogisticRegression(max_iter=2000, C=1.0)
    model.fit(X_train_vec, y_train)

    if test_df is not None:
        X_test, y_test = test_df["text"].tolist(), test_df["label_id"].values

    X_test_vec = vectorizer.transform(X_test)
    y_score = model.predict_proba(X_test_vec)[:, 1]
    report = evaluate_classification(y_test, y_score)
    report["dataset"] = "LIAR/PolitiFact" if LIAR_TEST_PATH.exists() else "demo"
    print(f"Baseline test metrics: {report}")

    BASELINE_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, BASELINE_VECTORIZER_PATH)
    joblib.dump(model, BASELINE_MODEL_PATH)
    save_report(report, BASELINE_METRICS_PATH)


if __name__ == "__main__":
    main()
