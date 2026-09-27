"""Core eval loop."""

import os
import time
from typing import Dict

from groq import Groq

from app.eval.scorer import get_scorer, semantic_similarity_raw

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

COST_PER_1M_INPUT = 0.15
COST_PER_1M_OUTPUT = 0.60


def estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    return (
        prompt_tokens / 1_000_000 * COST_PER_1M_INPUT
        + completion_tokens / 1_000_000 * COST_PER_1M_OUTPUT
    )


def run_case(
    case: Dict,
    model: str,
    scorer,
    threshold: float = 0.85,
    scoring_method: str = "exact_match",
) -> Dict:
    start = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": case["input"]}],
            temperature=0.0,
            max_tokens=200,
        )
        output = response.choices[0].message.content or ""
        prompt_tokens = response.usage.prompt_tokens if response.usage else 0
        completion_tokens = response.usage.completion_tokens if response.usage else 0
        error = None
    except Exception as e:
        output = ""
        prompt_tokens = 0
        completion_tokens = 0
        error = str(e)

    latency_ms = int((time.perf_counter() - start) * 1000)

    if error:
        score = 0.0
        raw_similarity = None
    elif scoring_method == "semantic_similarity":
        raw_similarity = semantic_similarity_raw(output, case["expected"])
        score = 1.0 if raw_similarity >= threshold else 0.0
    else:
        raw_similarity = None
        score = scorer(output, case["expected"])

    cost = estimate_cost(prompt_tokens, completion_tokens)

    return {
        "id": case.get("id", "unknown"),
        "input": case["input"],
        "expected": case["expected"],
        "output": output,
        "score": score,
        "raw_similarity": raw_similarity,
        "passed": score >= 1.0,
        "latency_ms": latency_ms,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cost_usd": cost,
        "error": error,
    }


def run_suite(suite: Dict) -> Dict:
    cases = suite["cases"]
    model = suite["model"]
    scoring_method = suite.get("scoring", "exact_match")
    threshold = suite.get("threshold", 0.85)
    scorer = get_scorer(scoring_method)

    results = [
        run_case(case, model, scorer, threshold=threshold, scoring_method=scoring_method)
        for case in cases
    ]

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    accuracy = passed / total if total > 0 else 0.0
    avg_latency = sum(r["latency_ms"] for r in results) / total if total > 0 else 0.0
    total_cost = sum(r["cost_usd"] for r in results)

    return {
        "suite_name": suite.get("suite_name", "unnamed"),
        "model": model,
        "scoring": scoring_method,
        "total_cases": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": round(accuracy, 4),
        "avg_latency_ms": round(avg_latency, 2),
        "total_cost_usd": round(total_cost, 6),
        "per_case": results,
    }
