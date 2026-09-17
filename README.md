# snip

A tiny URL shortener — the **starter application** for the Shift In tutorial. Past M4: the full
test pyramid exists — unit, API, one SLI-derived CI gate, and now Robot Framework system tests in
`tests/system/`, maintained by the `system-test-writer` subagent
(`.claude/agents/system-test-writer.md`) rather than written inline. CI (`.github/workflows/ci.yml`)
runs the fast suite and the system suite as two parallel jobs. `CLAUDE.md` is at v2. See
`docs/test-strategy.md` for the full shape.

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e .
uvicorn snip.main:app --reload --app-dir src
```

`pip`/`uvicorn` as bare commands only exist once a virtualenv is active — if you see "command not
found" for either, that's what's missing, not a broken install.

- Interactive docs: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

## Run the tests

```bash
pip install -e ".[test]"
pytest tests/unit tests/api                   # fast suite - what the Stop hook runs
pytest tests/gates -s                         # SLI 1 gate: redirect p95 latency, real server
pytest --cov=snip --cov-report=term-missing   # coverage: a map of gaps, not a target
# oracle check: break a line in src/snip/shortener.py, re-run pytest, confirm it goes red

pip install -e ".[system]"
robot --outputdir robot-results tests/system/ # system tests, real server, real HTTP
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
- `tests/unit/`, `tests/api/` — unit tests and thin route-wiring tests.
- `tests/gates/` — the SLI 1 (redirect latency) CI gate. Not part of the pyramid, not run by the
  Stop hook; CI runs it on every push.
- `tests/system/` — Robot Framework system tests: the redirect hot path round trip. Maintained by
  the `system-test-writer` subagent, not written inline.
- `.claude/agents/system-test-writer.md` — the subagent that owns `tests/system/`.
