# CLAUDE.md — snip

> Authored in **M1** from `docs/business-context.md`, `docs/quality-characteristics.md`, and
> `docs/slis.md`. Treat this as a **living artifact** — revisit and update it again in **M4**.

## Who this serves, in priority order

The **follow/redirect** path is the highest-volume traffic by far and is what these priorities
protect first:

1. **Recipients** — people following a short link. Every redirect must land on the exact URL the
   link was created for.
2. **Employees** — people creating short links for docs, chat, and slides. Lower volume than
   follows, but this is where input-validation and security risk concentrates.
3. **Link owners** — people checking click stats on links they created. Correctness here depends
   entirely on the follow path incrementing counts reliably.

## Quality bar (highest priority first)

1. **Functional correctness** — a short link always resolves to the exact URL it was created for;
   click counts are accurate.
2. **Performance efficiency** — following a link is the hot path and must be fast.
3. **Reliability / availability** — the redirect path must stay up; link creation can tolerate
   brief degradation.
4. **Security** — only safe, well-formed URLs are accepted; no open-redirect or script-scheme
   abuse.
5. **Maintainability** — small, well-tested codebase that an agent and a human can both reason
   about.

When trading off effort: weight tests and fixes toward **follow/redirect** first. **Create** is
lower volume but is where unsafe/invalid input has to be caught.

## SLIs (these define "good" — they drive what we test and what CI gates on)

| # | SLI | Definition | Target (SLO) |
|---|-----|------------|--------------|
| 1 | **Redirect latency** | p95 server time to answer `GET /{code}` | < 50 ms |
| 2 | **Redirect availability** | share of `GET /{code}` returning a valid redirect or a correct 404 | ≥ 99.9% |
| 3 | **Resolve correctness** | share of follows that redirect to the exact stored URL | 100% |
| 4 | **Create validation** | share of create requests with invalid/unsafe URLs that are correctly rejected | 100% |
| 5 | **Stats accuracy** | recorded clicks equal actual follows | 100% |

**Known gaps in the current (`start`) state — these are workshop material, not silent bugs to
patch in passing:**
- SLI 4 is not met: unsafe URLs are currently accepted on create.
- SLI 2 is not met: unknown codes raise errors instead of a correct 404.

Do not "fix" these outside the exercise they belong to (M2 code review surfaces them; later
milestones close them). If a task touches `create_link`/`resolve` in `src/snip/shortener.py`,
check whether closing one of these gaps is actually in scope before changing behavior there.

## Working agreements

**Definition of Ready:**
- The user story has a clear actor, action, and outcome.
- Acceptance criteria are testable and agreed by the Three Amigos.
- Impact on the SLIs above is understood before work starts.

**Definition of Done:**
- Code reviewed and merged via PR.
- Tests exist at the appropriate level(s) and pass in CI.
- SLI-affecting changes are reflected in the pipeline gates.
- Observable behaviour changes are covered by at least one higher-level test.

## Roadmap awareness

**Link expiry** (owners want links that stop working after a chosen time) is a known future
request, but it's the feature built live in **M5** via Example Mapping + an agent build. Don't
build it ahead of that exercise.

## snip (implementation)

A tiny FastAPI URL shortener. Source in `src/snip/`. Run with
`uvicorn snip.main:app --reload --app-dir src`. There are no tests yet.
