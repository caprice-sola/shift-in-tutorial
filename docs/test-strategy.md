# snip — test strategy (v1)

No tests exist yet in `start`. This is the target shape we hold ourselves to as we add them,
starting in M3a. Revisit this doc whenever the pyramid weights or SLI mapping stop matching
reality.

## Target test pyramid

| Level | What it covers | Tooling | Target weight |
|---|---|---|---|
| **Unit** | Pure logic in `shortener.py`/`store.py`: code generation, resolve, click increment, URL validation rules — no HTTP, no process. | pytest | **~55%** of tests |
| **Integration / API** | Request → response through the FastAPI app (`TestClient`): status codes, response schemas, redirect `Location` header, 404 behaviour, validation error contracts. | pytest + FastAPI `TestClient` | **~35%** of tests |
| **System / E2E** | Black-box against a running app: full create → follow → stats flows, exactly as a real client would do it. | Robot Framework | **~10%** of tests |

Rationale for the shape, from `docs/quality-characteristics.md` and `docs/slis.md`:

- **Maintainability is priority 5**, so the base of the pyramid stays cheap, fast unit tests —
  most logic bugs should be caught there, not by spinning up the app.
- **The redirect/follow path dominates traffic**, so *within each level*, resolve/redirect
  scenarios get written and reviewed before create scenarios — the pyramid's shape is standard,
  but its fill order isn't.
- System/E2E stays the thinnest layer on purpose: it's the most expensive and slowest to run, so
  it's reserved for the flows that only make sense end-to-end (e.g. click count actually
  incrementing after a real follow).

## SLI → test level mapping

| # | SLI | Target | Proven at | How |
|---|-----|--------|-----------|-----|
| 1 | Redirect latency | p95 < 50ms | **Performance check** (non-functional, own lane — see below) | Timed repeated calls to `GET /{code}`; not a pass/fail unit assertion. |
| 2 | Redirect availability | ≥ 99.9% valid redirect or correct 404 | **Integration** (404 contract) + **System** (uptime-shaped flow) | Integration test asserts unknown code → clean 404, not a 500; system test exercises the full path repeatedly. |
| 3 | Resolve correctness | 100% exact URL | **Unit** (`resolve()` returns the stored URL) + **Integration** (redirect `Location` header matches) | Two levels because the bug could live in either the lookup logic or the HTTP layer wiring. |
| 4 | Create validation | 100% invalid/unsafe URLs rejected | **Unit** (validation rules, one case per rejected pattern) + **Integration** (endpoint returns the right 4xx) | Unit tests carry the bulk of the cases (schemes, malformed input); integration confirms the contract at the boundary. |
| 5 | Stats accuracy | clicks == actual follows | **Unit** (increment logic) + **System** (create → follow N times → stats == N) | Unit proves the increment is correct in isolation; system proves nothing between the follow and the stats read drops a count. |

Per `docs/slis.md`, M4 weights system coverage toward SLIs 1–3 (the redirect hot path) — that's
already reflected above: SLIs 1–3 each have a system or dedicated non-functional check, while
SLI 4 (create) leans on unit tests alone plus one integration contract test.

### Performance check (SLI 1)

Latency isn't a correctness assertion, so it doesn't fit the pyramid above — it's a separate
lane that runs against `GET /{code}` and fails the build if p95 exceeds 50ms. This becomes the
CI latency gate referenced for M3b in `docs/slis.md`.

## Proving the tests actually assert something: break it on purpose

A test that never fails is worthless — it may not be exercising the assertion it claims to. For
every test written against an SLI-critical path (SLIs 1–5 above), before it's considered done we
introduce the matching mutant below, confirm the test **fails red**, then revert and confirm it's
green again. This check happens once at authoring time and is spot-checked in PR review per the
Definition of Done ("tests exist... and pass in CI") — it is not itself an automated CI step in
v1.

| SLI | Mutant to inject | Expected result |
|---|---|---|
| 3 — Resolve correctness | Make `resolve()` return a different stored record's URL (or a hardcoded string) instead of the one for `code`. | Unit + integration tests for resolve must fail. |
| 5 — Stats accuracy | Remove the `clicks += 1` in `resolve()`, or increment it twice. | Unit test on increment and the system create→follow→stats test must fail. |
| 4 — Create validation | Invert a validation rule (e.g. accept `javascript:` scheme, or accept a malformed URL). | The unit test for that specific rejected case must fail. |
| 2 — Redirect availability | Make the unknown-code path raise/return 500 instead of 404. | The integration 404-contract test must fail. |
| 1 — Redirect latency | Add an artificial `sleep()` in the hot path. | The performance check must fail the p95 gate. |

If a mutant doesn't turn a test red, the test isn't proving the SLI — it needs a stronger
assertion (e.g. checking the actual URL/count value, not just a status code) before it counts
toward Definition of Done.

## Out of scope for v1

- **CI gating** — `docs/slis.md` places the first SLI-as-CI-gate at M3b (latency or resolve
  correctness are the easy first choices). Until then, tests run locally/on-demand, not blocking.
- **Automated mutation testing tooling** — the table above is a manual authoring-time discipline,
  not a mutation-testing library wired into CI. Revisit if the manual check proves unreliable.
