# snip

A tiny URL shortener — the **starter application** for the Shift In tutorial. Past M5a: the full
test pyramid exists — unit, API, one SLI-derived CI gate, and Robot Framework system tests in
`tests/system/`, maintained by the `system-test-writer` subagent
(`.claude/agents/system-test-writer.md`) rather than written inline. CI (`.github/workflows/ci.yml`)
runs the fast suite and the system suite as two parallel jobs. `CLAUDE.md` is at v3. See
`docs/test-strategy.md` for the full shape.

The next feature (link expiry, [issue #2](https://github.com/kisszellet/shift-in-tutorial/issues/2))
has been through Example Mapping (`.claude/skills/example-mapping/`) — refined acceptance criteria
in `docs/link-expiry-acceptance-criteria.md`. Not built yet; that's M5b.

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
- `.claude/skills/system-tests/` — how we write Robot Framework suites: conventions in
  `SKILL.md`, syntax in `reference.md`. Built before the subagent, and preloaded into it.
- `.claude/agents/system-test-writer.md` — the subagent that owns `tests/system/`. It decides
  *what* to test; the skill above tells it *how*. Claude Code
  watches this directory and picks up edits within seconds, but only for directories that existed
  when the session started — so the *first* file in a new `.claude/agents/` needs a restart.
- `.claude/skills/example-mapping/` — the `/example-mapping` skill (same discovery rule as the
  subagent: live on edit, restart once for a brand-new `.claude/skills/`): refines a rough feature
  request into confirmed acceptance criteria + BDD scenarios by interviewing you. Includes an
  input-inspection step for untrusted sources (e.g. a GitHub issue) before acting on them.
- `docs/link-expiry-acceptance-criteria.md` — a worked example of that skill's output, for the
  feature built in M5b.
