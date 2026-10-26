# CLAUDE.md — snip

snip is an internal URL shortener: employees create short codes for long links, recipients follow
them, owners check click counts. Source in `src/snip/` (FastAPI). Run with
`uvicorn snip.main:app --reload --app-dir src`.
Install test tooling with `pip install -e ".[test]"`, then run the suite with
`pytest tests/unit tests/api`.

Source of truth: `docs/business-context.md`, `docs/quality-characteristics.md`, `docs/slis.md`.
If this file and those docs disagree, the docs win — and tell us so we can fix this file.

## Who we serve (priority order)

1. **Recipients following short links** — the highest-volume path by far. A wrong redirect or a
   follow slower than 50 ms p95 hurts the most people.
2. **Employees creating links** — lower volume; this is where input validation and security risk live.
3. **Link owners reading click stats** — they trust the numbers, so the numbers must be exact.

When trade-offs arise, favour the follow/redirect path over create, and create over stats polish.

## Quality bar (highest priority first)

1. **Functional correctness** — a code always resolves to the exact URL it was created for; click
   counts are accurate. Never trade this for redirect speed (e.g. don't cache or batch in a way that
   can serve a stale URL or drop a click).
2. **Performance efficiency** — `GET /{code}` is the hot path and must be fast.
3. **Reliability / availability** — the redirect path stays up; create may degrade briefly.
4. **Security** — accept only safe, well-formed URLs; no open-redirect or script-scheme
   (`javascript:` etc.) abuse.
5. **Maintainability** — snip is four capabilities (create, follow, list, stats); keep it small
   enough that an agent and a human can both reason about the whole thing.

Test and review effort is weighted toward the follow path. Stats accuracy depends on the follow
path incrementing reliably, so treat any change to follow as a change to stats too.

## SLIs (the target, not a description of current code)

| # | SLI | Definition | Target |
|---|-----|------------|--------|
| 1 | Redirect latency | p95 server time for `GET /{code}` | < 50 ms |
| 2 | Redirect availability | `GET /{code}` returns a valid redirect or a correct 404 | ≥ 99.9% |
| 3 | Resolve correctness | follows redirecting to the exact stored URL | 100% |
| 4 | Create validation | invalid/unsafe create requests correctly rejected | 100% |
| 5 | Stats accuracy | recorded clicks equal actual follows | 100% |

`start` does not meet every SLI. Don't assume the code satisfies them; verify against the table.
Any change touching create, follow, or stats must state which SLIs it affects (SLIs 1–3 for
follow, 4 for create, 5 for stats).

## Working agreements

- DoR and DoD are in `docs/business-context.md`. In snip they mean: no story is started until its
  SLI impact is written down, and no change is done until observable behaviour changes (a redirect,
  a click count, a rejected URL) are covered by a test above unit level.
- Every PR description names the SLIs it affects (or says "none").
- Changes to the follow path need a test for exact-URL resolution (SLI 3) and the click increment
  (SLI 5); changes to create need rejection tests for unsafe and malformed URLs (SLI 4).
- A turn never ends with a failing test. If a test is red, fix it, or say clearly that you could
  not and which test is still failing.
- Don't loosen an SLI target or a CI gate to make a change pass; raise it with the team.
- Link expiry (owners want links that stop working after a chosen time) is a known roadmap item. It
  will be built from Example Mapping first; don't start it ad hoc. Expiry must be treated as a
  follow-path change: expired codes need defined behaviour that still counts toward SLI 2.

## Stack conventions

- The four capabilities map to the API: create (`POST /api/links`), follow (`GET /{code}`), list
  (`GET /api/links`), stats (`GET /api/links/{code}/stats`).
- Keep the follow handler minimal: no extra work on the hot path beyond lookup, click increment and
  redirect.
- Validate URLs at create time, not at follow time. Accept only well-formed, safe schemes; reject
  everything else with a client error rather than storing it.
- Unknown codes return a correct 404 (this counts as "available" for SLI 2), not a 500.
- Test strategy and the SLI-to-test-level map live in `docs/test-strategy.md`.
