"""
Scoring functions for eval runs.

v0.1: exact_match, contains
v0.2: semantic_similarity (local MiniLM embeddings)
v0.3: llm_judge (Groq GPT-OSS-120B acts as judge)
"""

import os
from typing import Literal

from groq import Groq

from app.eval.embeddings import embed, cosine_similarity

ScoringMethod = Literal["exact_match", "contains", "semantic_similarity", "llm_judge"]

_judge_client = None
JUDGE_MODEL = "openai/gpt-oss-120b"


def _get_judge_client():
    """Lazy-load the Groq client for LLM judge."""
    global _judge_client
    if _judge_client is None:
        _judge_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _judge_client

JUDGE_PROMPT = """You are an impartial judge evaluating whether an AI model's output correctly answers a given input.

INPUT (the question or task given to the model):
{input}

EXPECTED (the reference answer):
{expected}

ACTUAL OUTPUT (what the model produced):
{output}

Decide if the ACTUAL OUTPUT is a correct answer to the INPUT. It does not need to match EXPECTED word-for-word — it needs to be correct.

Reply in this exact format:
VERDICT: PASS
REASON: <one sentence explaining your decision>

or

VERDICT: FAIL
REASON: <one sentence explaining your decision>"""


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
    output: str, expected: str, threshold: float = 0.75
) -> float:
    raw = semantic_similarity_raw(output, expected)
    return 1.0 if raw >= threshold else 0.0


def llm_judge_raw(input_text: str, output: str, expected: str) -> dict:
    """
    Ask the judge model to evaluate the output.
    Returns {"verdict": "PASS"|"FAIL", "reason": str, "raw_response": str}.
    """
    if not output or not expected:
        return {"verdict": "FAIL", "reason": "Empty output or expected", "raw_response": ""}

    prompt = JUDGE_PROMPT.format(
        input=input_text, expected=expected, output=output
    )

    try:
        client = _get_judge_client()
        response = client.chat.completions.create(
            model=JUDGE_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=150,
        )
        raw = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[scorer] LLM judge failed: {e}")
        return {"verdict": "FAIL", "reason": f"Judge error: {e}", "raw_response": ""}

    verdict = "FAIL"
    reason = ""

    for line in raw.splitlines():
        line = line.strip()
        if line.upper().startswith("VERDICT:"):
            verdict = "PASS" if "PASS" in line.upper() else "FAIL"
        elif line.upper().startswith("REASON:"):
            reason = line.split(":", 1)[1].strip()

    return {"verdict": verdict, "reason": reason, "raw_response": raw}


def score_llm_judge(input_text: str, output: str, expected: str) -> float:
    result = llm_judge_raw(input_text, output, expected)
    return 1.0 if result["verdict"] == "PASS" else 0.0


def get_scorer(method: ScoringMethod):
    if method == "exact_match":
        return score_exact_match
    if method == "contains":
        return score_contains
    if method == "semantic_similarity":
        return score_semantic_similarity
    if method == "llm_judge":
        return None  # Handled specially in runner.py because it needs the input too
    raise ValueError(f"Unknown scoring method: {method}")
