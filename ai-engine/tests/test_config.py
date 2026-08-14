from ai_engine.config import (
    CLASS_LABELS,
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
    NUM_LABELS,
    TEXT_MAX_LENGTH,
    TEXT_MIN_LENGTH,
)


def test_class_labels():
    assert CLASS_LABELS == ["REAL", "FAKE"]


def test_num_labels():
    assert NUM_LABELS == 2


def test_confidence_thresholds_ordering():
    assert CONFIDENCE_HIGH > CONFIDENCE_MEDIUM


def test_text_length_limits():
    assert TEXT_MIN_LENGTH == 20
    assert TEXT_MAX_LENGTH == 10000
    assert TEXT_MAX_LENGTH > TEXT_MIN_LENGTH
