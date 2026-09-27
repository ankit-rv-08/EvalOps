# EvalOps

**LLM evaluation harness — run test suites against any model, measure accuracy/latency/cost, block deploys on regression.**

FastAPI • Groq • PostgreSQL • SQLAlchemy • Python

---

## What it does

EvalOps is CI/CD for AI features. Just like unit tests catch bugs before deploy, EvalOps catches AI regressions before they hit users.

1. You define a test suite (JSON: input + expected output)
2. EvalOps runs each case against any LLM endpoint
3. It scores: exact match, latency, cost
4. Results persist to PostgreSQL
5. GitHub Action blocks the deploy if accuracy drops below threshold

---

## Status

- [x] FastAPI scaffold + PostgreSQL/SQLAlchemy
- [x] Exact-match + contains scoring
- [x] Groq integration (GPT-OSS-120B)
- [x] `POST /api/evaluate` endpoint
- [x] Per-case cost + latency tracking
- [ ] Semantic similarity scoring (pgvector)
- [ ] LLM-as-judge scoring
- [ ] GitHub Action for CI/CD
- [ ] Next.js dashboard
- [ ] Production deploy (Render + Vercel)

---

## API

**`GET /health`**

```json
{"status": "ok", "service": "evalops"}
```

**`POST /api/evaluate`**

Request:
```json
{
  "suite_name": "test-1",
  "model": "openai/gpt-oss-120b",
  "scoring": "exact_match",
  "threshold": 0.85,
  "cases": [
    {"id": "c1", "input": "What is 2+2? Reply with just the number.", "expected": "4"}
  ]
}
```

Response:
```json
{
  "suite_name": "test-1",
  "model": "openai/gpt-oss-120b",
  "total_cases": 1,
  "passed": 1,
  "accuracy": 1.0,
  "avg_latency_ms": 763.0,
  "total_cost_usd": 0.000037,
  "run_id": 1,
  "passed_threshold": true,
  "per_case": [...]
}
```

---

## Local setup

```bash
git clone https://github.com/ankit-rv-08/EvalOps.git
cd EvalOps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your GROQ_API_KEY
uvicorn app.main:app --reload --port 8000
```

---

## License

MIT.
