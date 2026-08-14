import pytest

from ai_engine.inference.predict import FakeNewsPredictor


@pytest.mark.parametrize("backend", ["baseline", "distilbert"])
def test_model_info(backend):
    info = FakeNewsPredictor(backend=backend).model_info
    assert info["backend"] == backend
    assert info["model_name"]
    assert info["model_version"] == "1.0.0"


def test_predict_empty_input_raises():
    predictor = FakeNewsPredictor(backend="baseline")
    with pytest.raises(ValueError):
        predictor.predict("   ")


def test_predict_structure(monkeypatch):
    predictor = FakeNewsPredictor(backend="baseline")
    monkeypatch.setattr(predictor, "_predict_baseline", lambda text: ("REAL", 0.8734))
    result = predictor.predict("This is a sufficiently long sample news article text.")
    assert result["prediction"] == "REAL"
    assert result["confidence"] == 0.8734
    assert result["model_name"] == "TF-IDF+LogisticRegression"
    assert result["model_version"] == "1.0.0"
    assert result["processing_time_ms"] >= 0


def test_predict_rounds_confidence(monkeypatch):
    predictor = FakeNewsPredictor(backend="baseline")
    monkeypatch.setattr(predictor, "_predict_baseline", lambda text: ("FAKE", 0.77777))
    result = predictor.predict("Another sufficiently long sample news article text here.")
    assert result["confidence"] == 0.7778
