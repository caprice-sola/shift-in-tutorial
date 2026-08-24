# snip

A tiny URL shortener — the **starter application** for the Shift In tutorial. Past M3a: a unit
test suite exists, backed by mutation testing (`docs/mutation-testing-notes.md`), and a `Stop`
hook (`.claude/hooks/run_tests.py`) keeps Claude Code from ending its turn while the suite is red
— the shift-left → Shift In pivot. CI (M3b) and system tests (M4) still come later.

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
pytest                              # unit + API tests
pytest --cov=snip --cov-report=term-missing   # coverage: a map of gaps, not a target
mutmut run && mutmut results        # mutation testing on shortener.py
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
