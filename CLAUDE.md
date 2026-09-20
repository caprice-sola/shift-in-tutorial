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

## The code

A tiny FastAPI URL shortener, ~130 lines across four modules:

- [shortener.py](src/snip/shortener.py) — code generation, resolve, click increment. Covered by
  the guardrail above.
- [store.py](src/snip/store.py) — one module-level `store = Store()` wrapping a dict. In-memory
  and non-persistent: nothing survives a restart, and state carries between tests unless they
  reset it.
- [main.py](src/snip/main.py) — the four routes. [models.py](src/snip/models.py) — the pydantic
  request/response shapes.
- [tests/](tests/) — empty on purpose, and [pyproject.toml](pyproject.toml) lists no test tooling.
  pytest isn't available until someone adds it.

Run it via **Run it** in the [README](README.md), which also lists the endpoints. Activate `.venv`
first — bare `pip` and `uvicorn` don't exist otherwise, which is what "command not found" there
means. `.venv-1` isn't the venv the README sets up; ignore it.
