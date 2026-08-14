from ai_engine.preprocessing.text import clean_text, tokenize_text, validate_length


def test_clean_text_collapses_whitespace():
    assert clean_text("  Hello\tworld\n there  ") == "Hello world there"


def test_clean_text_empty_and_none():
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_clean_text_strips():
    assert clean_text("   padded   ") == "padded"


def test_tokenize_text_lowercases_and_splits():
    assert tokenize_text("Hello, World!") == ["hello", "world"]


def test_validate_length_bounds():
    assert validate_length("x" * 20) is True
    assert validate_length("x" * 10000) is True
    assert validate_length("x" * 19) is False
    assert validate_length("x" * 10001) is False
