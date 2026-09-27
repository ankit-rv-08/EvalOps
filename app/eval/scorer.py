"""
Scoring functions for eval runs.

v0.1: exact_match, contains
v0.2: semantic_similarity (local MiniLM embeddings)
"""

from typing import Literal

from app.eval.embeddings import embed, cosine_similarity

ScoringMethod = Literal["exact_match", "contains", "semantic_similarity"]


def score_exact_match(output: str, expected: str) -> float:
    if output is None or expected is None:
        return 0.0
    return 1.0 if output.strip().lower() == expected.strip().lower() else 0.0


def score_contains(output: str, expected: str) -> float:
    if output is None or expected is None:
        return 0.0
    return 1.0 if expected.strip().lower() in output.strip().lower() else 0.0


def semantic_similarity_raw(output: str, expected: str) -> float:
    """Return the raw cosine similarity between output and expected."""
    if not output or not expected:
        return 0.0
    try:
        out_vec = embed(output)
        exp_vec = embed(expected)
        return cosine_similarity(out_vec, exp_vec)
    except Exception as e:
        print(f"[scorer] semantic similarity failed: {e}")
        return 0.0


def score_semantic_similarity(
    output: str, expected: str, threshold: float = 0.85
) -> float:
    """Return 1.0 if cosine similarity >= threshold, else 0.0."""
    raw = semantic_similarity_raw(output, expected)
    return 1.0 if raw >= threshold else 0.0


def get_scorer(method: ScoringMethod):
    if method == "exact_match":
        return score_exact_match
    if method == "contains":
        return score_contains
    if method == "semantic_similarity":
        return score_semantic_similarity
    raise ValueError(f"Unknown scoring method: {method}")
