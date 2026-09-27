""" Core eval loop.

Takes a list of test cases, runs each prompt against an LLM, scores the output, and returns per-case results plus aggregates. """

import os
import time
from typing import List, Dict

from groq import Groq

from app.eval.scorer import get_scorer

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Approximate cost per 1M tokens for gpt-oss-120b on Groq (free tier is $0,
# but we track the equivalent dollar value so the UI shows real numbers).
COST_PER_1M_INPUT = 0.15
COST_PER_1M_OUTPUT = 0.60

def estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate USD cost from token counts."""
    return (
        prompt_tokens / 1_000_000 * COST_PER_1M_INPUT
        + completion_tokens / 1_000_000 * COST_PER_1M_OUTPUT
    )

def run_case(case: Dict, model: str, scorer) -> Dict:
    """
    Run a single test case. Returns a dict with the output, score, latency,
    token counts, cost, and pass/fail status.
    """
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
    score = scorer(output, case["expected"]) if not error else 0.0
    cost = estimate_cost(prompt_tokens, completion_tokens)

    return {
        "id": case.get("id", "unknown"),
        "input": case["input"],
        "expected": case["expected"],
        "output": output,
        "score": score,
        "passed": score >= 1.0,
        "latency_ms": latency_ms,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cost_usd": cost,
        "error": error,
    }

def run_suite(suite: Dict) -> Dict:
    """
    Run a full test suite. Returns aggregates plus per-case results.
    """
    cases = suite["cases"]
    model = suite["model"]
    scoring_method = suite.get("scoring", "exact_match")
    scorer = get_scorer(scoring_method)

    results = [run_case(case, model, scorer) for case in cases]

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