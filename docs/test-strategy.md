# snip — test strategy (v1)

Status: **target**. No tests exist yet; this is what we will be held to. It derives from
`docs/business-context.md`, `docs/quality-characteristics.md` and `docs/slis.md`. Where they
change, this changes.

## Principles

- **Weight effort where the traffic is.** `GET /{code}` dominates traffic and carries SLIs 1–3, so
  it gets the most tests, at every level.
- **Correctness before speed.** Resolve correctness and stats accuracy are 100% targets. A single
  wrong redirect or miscounted click is a failure, not a percentage.
- **Create is where the security risk is.** Input validation (SLI 4) is tested exhaustively at the
  cheapest level that can prove it.
- **A green test must be able to fail.** SLIs 3, 4 and 5 are 100% targets, so a test that can't
  go red is worse than no test. See "Assertion strength" below.

## Target test pyramid

| Level | What it exercises | Weight | Focus |
|-------|-------------------|--------|-------|
| **Unit** (pytest) | Code generation, URL validation, store lookup/increment, in isolation | **~60%** | Validation rules (SLI 4), exact round-trip of stored URL (SLI 3), click increment (SLI 5) |
| **API / integration** (pytest + FastAPI `TestClient`, in-process) | Real routes, real store, no network | **~30%** | Create → follow → stats flows; status codes and `Location` header; 404 on unknown code |
| **System** (Robot Framework against a running `uvicorn`) | The deployed shape, over HTTP | **~10%** | Redirect hot path end to end (SLIs 1–3), latency gate (SLI 1), a few full user journeys |

Of the total, roughly **half the tests, at any level, should be about the follow path**; most of
the rest cover create validation. List and stats-read get thin coverage: one happy path each plus
the stats accuracy checks.

Rules of thumb:

- Prove each behaviour at the **lowest level that can really prove it**; add a higher-level test
  only for behaviour that is observable to a user (DoD: observable changes need at least one
  higher-level test).
- System tests are few and slow by design. Don't add one where an API test would do.
- No test depends on another test's data; each starts from a fresh store.

## SLI → test level that proves it

| # | SLI | Target | Proven at | How |
|---|-----|--------|-----------|-----|
| 1 | Redirect latency | p95 < 50 ms | **System** | Fire a fixed batch of follows at a running server, compute p95 server time, fail the run above 50 ms. **First CI gate candidate.** |
| 2 | Redirect availability | ≥ 99.9% valid redirect or correct 404 | **API**, backed by **System** | API tests: every follow of a known code gives a redirect and every unknown/odd code gives a 404, never a 5xx. System smoke repeats it over HTTP. The 99.9% itself is a production measure we can't prove in CI; CI proves there is no code path that returns an error. |
| 3 | Resolve correctness | 100% exact URL | **Unit** + **API** + **System** | Unit: stored URL round-trips byte for byte (query strings, fragments, unicode, trailing slashes). API: created URL equals `Location` header. System: one end-to-end journey. **Second CI gate candidate.** |
| 4 | Create validation | 100% rejected | **Unit** (exhaustive) + **API** (status code) | Unit: table of invalid/unsafe inputs (`javascript:`, `data:`, `file:`, empty, no scheme, malformed host, oversized). API: each is refused with a client error and nothing is stored. |
| 5 | Stats accuracy | 100% clicks = follows | **API** | Create, follow N times, assert stats report exactly N. Also: failed follows (404) don't count; clicks for one code don't leak into another. |

Gaps we accept for v1: no load or soak testing beyond the SLI 1 batch, and no production
monitoring of the availability ratio. Revisit when the pipeline exists (M3b).

## Assertion strength

Coverage shows a line ran, not that anything was checked. Every test, and every review of a test,
must pass these checks:

- **Exact, not approximate.** Assert `clicks == N`, never `>= 1` or "is truthy". Assert the full
  `Location` header equals the stored URL, not just that it is present.
- **Redirects check the target.** A follow test asserting only the status code (302/307) doesn't
  prove SLI 3; it must also assert `Location`.
- **Rejections check the side effect.** A create test for a bad URL asserts the client error *and*
  that nothing was stored (list is unchanged).
- **No mocking the thing under proof.** A test claiming resolve correctness or stats accuracy uses
  the real store, not a stub that returns the expected answer.
- **Every test has at least one assertion on the behaviour in its name,** and the expected value is
  written in the test, not recomputed using the code under test.
- **Watch it fail once.** When writing a test, run it against the code before the behaviour exists
  (or with the assertion's expected value deliberately wrong) and see it go red before trusting it
  green. Reviewers ask for this in the PR if it isn't obvious.

## Persistence and lifetime

The store (`src/snip/store.py`) is **in-memory and per-process**: links and click counts are lost on
restart, and each process has its own copy. v1 of this strategy tests snip as it is:

- SLIs 3 and 5 are proven **within a single process lifetime**. "100%" means that, not durability.
- Tests must not assume state survives a restart, and the system level starts a fresh `uvicorn` per
  run, so no state leaks between runs.
- Running more than one worker or instance would give each its own links, so a code created on one
  would 404 on another. This is an availability risk (SLI 2) and a correctness risk (SLI 3). It is
  not tested today; snip is assumed to run as one process.
- `docs/business-context.md` doesn't say whether links or counts must survive a restart. **Open
  question for the team:** if they must, persistence becomes a requirement. Add a restart test
  (create, follow, restart, follow again) at the system level and review SLIs 3 and 5 accordingly.

## Tooling (to be added from M3a)

pytest and pytest-cov for unit and API levels; Robot Framework for the system level. Coverage is a
**diagnostic, not a gate**: it shows what's untested, not whether the tests assert anything useful
(that's what "Assertion strength" is for).

## Open questions

- Must links and click counts survive a restart or run on more than one instance? (See
  "Persistence and lifetime".)
- Which SLI becomes the first CI gate (latency or correctness)? Decide in M3b.
- Where to run the latency batch in CI so the 50 ms threshold isn't flaky on shared runners.
