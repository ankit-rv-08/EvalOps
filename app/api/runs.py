"""
GET /api/runs — list past eval runs
GET /api/runs/{run_id} — fetch one run with per-case breakdown
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db, EvalRun, EvalCase

router = APIRouter()


@router.get("/api/runs")
def list_runs(limit: int = 20, db: Session = Depends(get_db)):
    """List recent eval runs, newest first."""
    runs = (
        db.query(EvalRun)
        .order_by(EvalRun.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "total": len(runs),
        "runs": [
            {
                "run_id": r.id,
                "suite_name": r.suite_name,
                "model": r.model,
                "total_cases": r.total_cases,
                "passed": r.passed,
                "failed": r.failed,
                "accuracy": r.accuracy,
                "avg_latency_ms": r.avg_latency_ms,
                "total_cost_usd": r.total_cost_usd,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in runs
        ],
    }


@router.get("/api/runs/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db)):
    """Fetch a single run with its full per-case breakdown."""
    run = db.query(EvalRun).filter(EvalRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    cases = db.query(EvalCase).filter(EvalCase.run_id == run_id).all()

    return {
        "run_id": run.id,
        "suite_name": run.suite_name,
        "model": run.model,
        "total_cases": run.total_cases,
        "passed": run.passed,
        "failed": run.failed,
        "accuracy": run.accuracy,
        "avg_latency_ms": run.avg_latency_ms,
        "total_cost_usd": run.total_cost_usd,
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "per_case": [
            {
                "case_id": c.case_id,
                "input": c.input,
                "expected": c.expected,
                "output": c.output,
                "score": c.score,
                "passed": c.passed,
                "latency_ms": c.latency_ms,
                "prompt_tokens": c.prompt_tokens,
                "completion_tokens": c.completion_tokens,
                "cost_usd": c.cost_usd,
                "error": c.error,
            }
            for c in cases
        ],
    }
