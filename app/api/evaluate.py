""" POST /api/evaluate

Accepts a test suite, runs it, logs the result to PostgreSQL, and returns aggregates + per-case breakdown. """

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db, EvalRun
from app.eval.runner import run_suite

router = APIRouter()

class TestCase(BaseModel):
    id: str
    input: str
    expected: str

class TestSuite(BaseModel):
    suite_name: str
    model: str = "openai/gpt-oss-120b"
    scoring: str = "exact_match"
    threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    cases: list[TestCase]

@router.post("/api/evaluate")
def evaluate(suite: TestSuite, db: Session = Depends(get_db)):
    """Run an eval suite and persist the result."""
    if not suite.cases:
        raise HTTPException(status_code=400, detail="Suite must have at least one case")

    result = run_suite(suite.model_dump())

    # Persist to DB
    run = EvalRun(
        suite_name=result["suite_name"],
        model=result["model"],
        total_cases=result["total_cases"],
        passed=result["passed"],
        failed=result["failed"],
        accuracy=result["accuracy"],
        avg_latency_ms=result["avg_latency_ms"],
        total_cost_usd=result["total_cost_usd"],
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    result["run_id"] = run.id
    result["created_at"] = run.created_at.isoformat()
    result["threshold"] = suite.threshold
    result["passed_threshold"] = result["accuracy"] >= suite.threshold

    return result