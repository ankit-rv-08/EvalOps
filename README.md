# EvalOps

**LLM evaluation harness — run test suites against any model, measure accuracy/latency/cost, block deploys on regression.**

FastAPI • Groq • PostgreSQL • SQLAlchemy • sentence-transformers • GitHub Actions

---

## What it does

EvalOps is CI/CD for AI features. Just like unit tests catch bugs before deploy, EvalOps catches AI regressions before they hit users.

1. You define a test suite (JSON: input + expected output)
2. EvalOps runs each case against any LLM endpoint
3. It scores: exact match, contains, semantic similarity, latency, cost
4. Results persist to PostgreSQL
5. GitHub Action blocks the deploy if accuracy drops below threshold

---

## Status

- [x] FastAPI scaffold + PostgreSQL/SQLAlchemy
- [x] Exact-match + contains scoring
- [x] Semantic similarity scoring (local MiniLM embeddings)
- [x] Groq integration (GPT-OSS-120B)
- [x] `POST /api/evaluate` endpoint
- [x] `GET /api/runs` and `GET /api/runs/{id}` endpoints
- [x] Per-case cost + latency tracking
- [x] GitHub Action for CI/CD
- [ ] LLM-as-judge scoring
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

**`GET /api/runs`**

List recent eval runs (summary view):

```json
{
  "total": 1,
  "runs": [
    {
      "run_id": 1,
      "suite_name": "test-1",
      "model": "openai/gpt-oss-120b",
      "total_cases": 1,
      "passed": 1,
      "accuracy": 1.0,
      "created_at": "2026-09-27T06:51:39.061389"
    }
  ]
}
```

**`GET /api/runs/{run_id}`**

Fetch a single run with full per-case breakdown:

```json
{
  "run_id": 1,
  "suite_name": "test-1",
  "model": "openai/gpt-oss-120b",
  "total_cases": 1,
  "passed": 1,
  "accuracy": 1.0,
  "per_case": [...]
}
```

---

## CI/CD Integration

EvalOps is designed to run in CI. Drop the workflow from `examples/client-workflow.yml` into your repo, set `EVALOPS_URL` as a secret, and your PRs will block when LLM quality regresses.

**Self-demo:** See `.github/workflows/eval.yml` — EvalOps tests itself on every PR.

```
Pull request opened
│
▼
GitHub Actions runs .github/workflows/eval.yml
│
▼
Starts EvalOps, hits /api/evaluate with examples/demo-suite.json
│
▼
Checks accuracy against threshold (0.7)
│
▼
Pass → merge allowed
Fail → PR blocked
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

## GitHub Actions Integration

EvalOps includes a GitHub Action that automatically runs eval suites on PRs and blocks deploys if accuracy drops below threshold.

### Self-Test Workflow

The `.github/workflows/eval.yml` workflow runs a demo suite on every PR to main:

```yaml
name: EvalOps CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Start EvalOps API
        run: |
          python3 -m venv .venv
          source .venv/bin/activate
          pip install -r requirements.txt
          echo "GROQ_API_KEY=${{ secrets.GROQ_API_KEY }}" >> .env
          nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &
          sleep 15
      - name: Run eval suite
        run: |
          RESPONSE=$(curl -s -X POST http://localhost:8000/api/evaluate \
            -H "Content-Type: application/json" \
            -d @examples/demo-suite.json)
          # Check if accuracy >= threshold
```

### Using EvalOps in Your Repo

To use EvalOps in your own repository:

1. Add `EVALOPS_URL` to your repo secrets (e.g., `https://evalops.onrender.com`)
2. Create your test suite as `eval-suite.json` in your repo root
3. Add the workflow from `examples/client-workflow.yml` to `.github/workflows/eval.yml`

See `examples/client-workflow.yml` for a complete example.

---

## License

MIT.
