# CLAUDE.md — snip

snip is an internal URL-shortening service. Teams paste long links into chat, docs, and slides;
snip turns them into short codes and counts how often each is followed. Full context:
`docs/business-context.md`, `docs/quality-characteristics.md`, `docs/slis.md`.

## Who this serves, in priority order

1. **Recipients following a short link** — by far the highest-volume path. This is the redirect
   (`GET /{code}`) and it must stay fast and available.
2. **Employees creating links** — lower volume, but the only place unsafe input enters the system.
3. **Link owners checking stats** — low volume, low risk.

## Quality bar (ISO 25010 priority order — see `docs/quality-characteristics.md`)

1. Functional correctness — a short link always resolves to the exact URL it was created for.
2. Performance — the redirect path is the hot path; keep it fast.
3. Reliability/availability — the redirect path must stay up; creation can tolerate brief degradation.
4. Security — only safe, well-formed URLs are accepted. No open-redirect or script-scheme
   (`javascript:`, etc.) abuse.
5. Maintainability — small, well-tested codebase an agent and a human can both reason about.

## SLIs — full table in `docs/slis.md`. These define "good" and drive what gets tested and gated.

| SLI | Target |
|---|---|
| Redirect latency (p95, `GET /{code}`) | < 50 ms |
| Redirect availability (valid redirect or correct 404) | ≥ 99.9% |
| Resolve correctness (redirects to exact stored URL) | 100% |
| Create validation (unsafe/invalid URLs correctly rejected) | 100% |
| Stats accuracy (recorded clicks = actual follows) | 100% |

Any change touching `resolve`, `create_link`, or the store must be checked against this table
before it's called done. An unhandled lookup, a silently overwritten code, or an unvalidated URL
are SLI violations, not style issues.

## Working agreements for whoever (human or agent) touches this code

- **Coverage is a map of gaps, not a score.** Test the SLI-relevant and business-critical paths
  first (resolve/redirect, create validation). Don't chase a percentage.
- **Keep the pyramid upright.** Add coverage at the lowest level that gives confidence. See
  `docs/test-strategy.md` for the target distribution — don't add a system/end-to-end test for
  something a unit test already covers.
- **A turn never ends with a failing test.** Run `pytest tests/unit tests/api` before you finish.
  If something is red, fix it — or say plainly that you could not and why. Don't narrow a test or
  delete an assertion to get to green.
- **DoD (excerpt — full version in `docs/business-context.md`):** reviewed and merged via PR;
  tests exist at the appropriate level(s) and pass in CI; SLI-affecting changes are reflected in
  pipeline gates; observable behaviour changes are covered by at least one higher-level test.

## Stack & conventions

- Python 3.11+, FastAPI, in-memory store (`store.py` — not persistent; that's intentional).
- Run: `pip install -e .` then `uvicorn snip.main:app --reload --app-dir src`.
- Source: `src/snip/`. Tests: `tests/unit/`, `tests/api/` — see `docs/test-strategy.md` for the
  target shape and `docs/oracle-notes.md` for what breaking the code on purpose found.
- A `Stop` hook (`.claude/hooks/run_tests.py`) runs `tests/unit`+`tests/api` before Claude Code
  ends a turn — don't remove or bypass it to get a stop through faster.
- CI (`.github/workflows/ci.yml`) runs that same suite on every push, plus `tests/gates/` — one
  SLI-derived gate (redirect latency, docs/slis.md SLI 1), kept out of the Stop hook because it's
  slower than an in-loop check should be.

---
_v2 — M3a. v1 (M1) covered business context, quality characteristics, and SLIs. This pass adds the
test commands and one working agreement: a turn never ends with a failing test. That agreement was
written here **before** the `Stop` hook existed, on purpose — an instruction the agent may or may
not follow, and then the same rule enforced by the harness. Subagents don't exist yet; the
system-test tier and the full pyramid map arrive in v3 (M4)._
