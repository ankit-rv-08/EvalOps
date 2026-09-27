""" Scoring functions for eval runs.  v0.1 supports exact-match only. Semantic similarity (pgvector) and LLM-as-judge come in v0.2. """

from typing import Literal

ScoringMethod = Literal["exact_match", "contains"]


def score_exact_match(output: str, expected: str) -> float:
    """
    Return 1.0 if output equals expected (case-insensitive, stripped), else 0.0.
    """
    if output is None or expected is None:
        return 0.0
    return 1.0 if output.strip().lower() == expected.strip().lower() else 0.0


def score_contains(output: str, expected: str) -> float:
    """
    Return 1.0 if `expected` appears as a substring in `output` (case-insensitive).
    Useful when the LLM is expected to include a keyword rather than echo it exactly.
    """
    if output is None or expected is None:
        return 0.0
    return 1.0 if expected.strip().lower() in output.strip().lower() else 0.0


def get_scorer(method: ScoringMethod):
    """Return the scoring function for the given method name."""
    if method == "exact_match":
        return score_exact_match
    if method == "contains":
        return score_contains
    raise ValueError(f"Unknown scoring method: {method}")