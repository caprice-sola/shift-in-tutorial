# snip

A tiny URL shortener — the **starter application** for the Shift In tutorial. Past M3b: unit +
API tests, mutation testing (`docs/mutation-testing-notes.md`), a `Stop` hook that keeps Claude
Code from ending a turn while the suite is red (the shift-left → Shift In pivot), and CI
(`.github/workflows/ci.yml`) running that same suite plus an SLI-derived gate on every push. System
tests (Robot Framework, M4) still come later.

## Run it

```bash
pip install -e .
uvicorn snip.main:app --reload --app-dir src
```

- Interactive docs: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

## Run the tests

```bash
pip install -e ".[test]"
pytest tests/unit tests/api                   # fast suite - what the Stop hook runs
pytest tests/gates -s                         # SLI 1 gate: redirect p95 latency, real server
pytest --cov=snip --cov-report=term-missing   # coverage: a map of gaps, not a target
mutmut run && mutmut results                  # mutation testing on shortener.py
```

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/links` | Create a short link from `{ "url": "..." }` |
| GET | `/api/links` | List links |
| GET | `/api/links/{code}/stats` | Click stats for a code |
| GET | `/{code}` | Follow a short link (redirect) |

## Where to look

- `docs/business-context.md`, `docs/quality-characteristics.md`, `docs/slis.md` — what "good" means.
- `docs/test-strategy.md` — the target test pyramid and per-SLI test-level mapping.
- `src/snip/` — the implementation.
- `tests/unit/`, `tests/api/` — unit tests and thin route-wiring tests. System tests land in M4.
- `tests/gates/` — the SLI 1 (redirect latency) CI gate. Not part of the pyramid, not run by the
  Stop hook; CI runs it on every push.
