# Test strategy — snip (v1, authored in M1)

Written in M1, **before** any test existed, so tooling decisions in M3a/M4 have something to be
held accountable to. As of M3a, `tests/unit/` and `tests/api/` exist and follow the shape below —
see `docs/mutation-testing-notes.md` for what mutation testing found once they did.

## Guiding rule

Coverage is a map of gaps, not a target. Cover **SLI-relevant and business-critical paths first**,
at the **lowest level that gives confidence**. A system/end-to-end test is only justified when a
unit test cannot exercise the behaviour (e.g. real HTTP routing, redirect status codes).

## Target pyramid shape

| Level | Tool | Weight | What lives here |
|---|---|---|---|
| Unit | pytest (M3a) | Majority of tests | `shortener.py` and `store.py` logic in isolation: code generation, collision handling, validation, click counting, lookup-miss behaviour. |
| API / integration | pytest + FastAPI `TestClient` (M3a) | A thin layer | Route wiring: status codes, request/response shapes — one or two tests per endpoint, not per case. |
| System | Robot Framework, via subagent (M4) | Thinnest layer, weighted toward SLIs 1–3 | Full-process black-box checks on the redirect hot path (create → follow → stats round trip) and one or two cross-cutting flows. Not a restatement of the unit suite. |

If a mob is about to write a system test for something already provable at the unit level, that's
the pyramid-inversion anti-pattern — stop and push the coverage down instead.

## Per-SLI test mapping

| SLI | Primary level | Notes |
|---|---|---|
| Redirect latency (p95 < 50 ms) | System (M4) | Needs a real running process; a unit test can't measure server-side latency meaningfully. Candidate for an M3b CI gate if a lightweight check is feasible; otherwise stays a system-level concern. |
| Redirect availability (valid redirect or correct 404) | Unit | `resolve()` behaviour for known vs. unknown codes is a pure function test — no server needed. |
| Resolve correctness (exact URL match) | Unit | Create-then-resolve round trip on the store/shortener layer. |
| Create validation (unsafe/invalid URLs rejected) | Unit | Table-driven tests over valid/invalid/unsafe URL inputs against `create_link`. Highest-value suite in the app — this is where the one significant security risk lives. |
| Stats accuracy (clicks = follows) | Unit, plus one system check | Unit: click counter increments correctly per resolve call. System: one end-to-end "follow N times, check stats" flow, since it crosses the create/follow/stats boundary. |

## Mutation testing (M3a)

Run `mutmut` against `shortener.py` — it carries the highest-risk logic (validation, collision
handling, lookup). A green coverage report that still lets mutants survive means the tests assert
too little; treat a surviving mutant as a missing assertion, not a mutmut false positive, until
proven otherwise.

Results of the first real run: `docs/mutation-testing-notes.md`.

## Out of scope for this document

Load-testing infrastructure, persistence-layer testing (the store is in-memory by design), and the
link-expiry feature — that gets its own acceptance criteria via Example Mapping in M5a.

---
_v1 — M1. Revisit if M4's subagent finds the target distribution unworkable in practice; that's a
legitimate reason to change this document, not a reason to quietly ignore it._
