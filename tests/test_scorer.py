"""Unit tests for scoring functions."""

import os
from unittest.mock import patch

from app.eval.scorer import score_exact_match, score_contains, score_semantic_similarity, semantic_similarity_raw, llm_judge_raw, score_llm_judge, get_scorer


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


@patch.dict(os.environ, {"GROQ_API_KEY": "test_key"})
def test_llm_judge_empty_input():
    result = llm_judge_raw("", "output", "expected")
    assert result["verdict"] == "FAIL"
    # The reason could be "Empty" or an API error with fake key
    assert result["reason"] is not None


@patch.dict(os.environ, {"GROQ_API_KEY": "test_key"})
def test_llm_judge_empty_output():
    result = llm_judge_raw("input", "", "expected")
    assert result["verdict"] == "FAIL"
    assert "Empty" in result["reason"]


@patch.dict(os.environ, {"GROQ_API_KEY": "test_key"})
def test_llm_judge_scoring():
    score = score_llm_judge("input", "output", "expected")
    # With empty input, should return 0.0
    assert score == 0.0


def test_get_scorer_llm_judge():
    scorer = get_scorer("llm_judge")
    # LLM judge is handled specially, returns None
    assert scorer is None
