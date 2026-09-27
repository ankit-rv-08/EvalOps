"""Unit tests for scoring functions."""

from app.eval.scorer import score_exact_match, score_contains, score_semantic_similarity, semantic_similarity_raw, get_scorer


def test_exact_match_same_string():
    assert score_exact_match("4", "4") == 1.0


def test_exact_match_case_insensitive():
    assert score_exact_match("Paris", "paris") == 1.0


def test_exact_match_strips_whitespace():
    assert score_exact_match("  hello  ", "hello") == 1.0


def test_exact_match_different():
    assert score_exact_match("4", "5") == 0.0


def test_exact_match_none_input():
    assert score_exact_match(None, "4") == 0.0


def test_contains_positive():
    assert score_contains("The answer is 4", "4") == 1.0


def test_contains_negative():
    assert score_contains("The answer is 5", "4") == 0.0


def test_contains_case_insensitive():
    assert score_contains("PARIS is the capital", "paris") == 1.0


def test_get_scorer_exact_match():
    scorer = get_scorer("exact_match")
    assert scorer("4", "4") == 1.0


def test_get_scorer_contains():
    scorer = get_scorer("contains")
    assert scorer("The answer is 4", "4") == 1.0


def test_get_scorer_unknown():
    import pytest
    with pytest.raises(ValueError):
        get_scorer("made_up_method")


def test_semantic_similarity_empty_strings():
    assert semantic_similarity_raw("", "test") == 0.0
    assert semantic_similarity_raw("test", "") == 0.0


def test_semantic_similarity_none():
    assert semantic_similarity_raw(None, "test") == 0.0
    assert semantic_similarity_raw("test", None) == 0.0


def test_get_scorer_semantic():
    scorer = get_scorer("semantic_similarity")
    # This would normally call the API, but we're just testing the function lookup
    assert scorer == score_semantic_similarity
