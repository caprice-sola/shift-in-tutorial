# CLAUDE.md — snip

> Authored in **M1**. Revisit in **M4** — and when you do, keep it a router: what "good" means for
> snip belongs in `docs/`, not copied back in here.

## Read before you work

| Open | Before you |
|---|---|
| [business-context.md](docs/business-context.md) | Add to snip's four capabilities — create, follow, list, stats — or change one, or judge whether a change is in scope. Also carries the DoR/DoD each change is held to. |
| [quality-characteristics.md](docs/quality-characteristics.md) | Decide whether follow/redirect work or create work gets the effort. It ranks snip's quality attributes and settles that conflict. |
| [slis.md](docs/slis.md) | Touch `GET /{code}` latency, unknown-code handling, the stored-URL round trip, create-time URL validation, or click counting — the five things snip measures and gates CI on. |
| [test-strategy.md](docs/test-strategy.md) | Write or restructure tests. Sets the target pyramid, maps each SLI to the level that proves it, and defines the mutant a new test must go red against before it counts as done. |

## Standing guardrails

**Don't change what `create_link` or `resolve` do in
[src/snip/shortener.py](src/snip/shortener.py) unless the task explicitly says to.** snip's
`start` state misses some of its own SLIs deliberately and those gaps are exercise material — the
module docstring says so too. Report what you spot there and leave it; the other modules are
ordinary code.

**Don't build link expiry** ahead of the exercise that builds it. The roadmap section of
[business-context.md](docs/business-context.md) says which one that is.

**The current milestone isn't inferable from this repo.** No branch name or commit tells you which
exercise is running, and the two guardrails above depend on it. Ask rather than guess.

**After changing behaviour in `src/snip/`, run the tests that cover it before calling the change
done** — see **Tests** below for how. A diff that looks right isn't the same as one that's been
run.

## The code

A tiny FastAPI URL shortener, ~130 lines across four modules:

- [shortener.py](src/snip/shortener.py) — code generation, resolve, click increment. Covered by
  the guardrail above.
- [store.py](src/snip/store.py) — one module-level `store = Store()` wrapping a dict. In-memory
  and non-persistent: nothing survives a restart, and state carries between tests unless they
  reset it — see **Tests** below for the pattern already in use.
- [main.py](src/snip/main.py) — the four routes. [models.py](src/snip/models.py) — the pydantic
  request/response shapes.

Run it via **Run it** in the [README](README.md), which also lists the endpoints. Activate `.venv`
first — bare `pip` and `uvicorn` don't exist otherwise, which is what "command not found" there
means. `.venv-1` isn't the venv the README sets up; ignore it.

## Tests

[test-strategy.md](docs/test-strategy.md) sets the target shape and the SLI-per-level mapping;
this is where that maps onto the actual repo:

- [tests/unit/](tests/unit/) — pure logic, no HTTP: `test_shortener.py`, `test_store.py`,
  `test_models.py`.
- [tests/api/](tests/api/) — FastAPI `TestClient`; this is what the doc calls the "Integration /
  API" level. `test_routes.py` asserts status code and response structure only — input-validation
  cases belong in `tests/unit/test_models.py` instead.
- No `tests/system/` yet — the doc's Robot Framework layer hasn't been started.

One-time setup: `pip install -e '.[test]'` (pytest, pytest-cov, httpx — httpx is what
`TestClient` needs under the hood). Run with `.venv/bin/pytest tests/`, or scope it to
`tests/unit` / `tests/api`.

Both directories share the same state trap as `store.py` above: because `store` is a singleton,
every test file resets it with an autouse fixture —
```python
@pytest.fixture(autouse=True)
def clear_store():
    store._links.clear()
    yield
    store._links.clear()
```
Copy this into any new test file that touches the store, or state leaks between tests in the same
run.
