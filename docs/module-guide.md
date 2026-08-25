# Module guide

For each sub-module: a short theory primer (~5 min to deliver), the step list the mob follows,
the expected artifact, and common failure modes + how to recover. Written after all eight
solution branches were built and proven, so the failure modes below aren't guesses — most of them
actually happened once while building the reference branches, and were caught (usually by a
second `/code-review` pass) before they shipped. Where that's true, it's called out explicitly —
it's better material than a hypothetical.

---

## M1 — Foundations

**Theory primer (5 min):** `CLAUDE.md` is standing context — every session, human or agent, reads
it automatically. Writing it well once saves re-explaining business context every session after.
A test strategy written *before any test exists* is a different kind of artifact than one written
after: it sets a target the later modules can be checked against, not just described. (M4 checked
its own pyramid table against reality and found the "System" tier's promised second use case
didn't actually exist — a strategy document is worth writing precisely so that kind of gap is
visible instead of silently absorbed.)

**Steps:**
1. Read `docs/business-context.md`, `quality-characteristics.md`, `slis.md` together as a mob —
   don't skip straight to asking the agent to summarize them.
2. Ask the agent to draft `CLAUDE.md` v1: who this serves (priority order), the quality bar, the
   SLI table, working agreements, stack conventions. Distilled from the docs just read, not
   generic boilerplate — check for that specifically.
3. Ask the agent to draft `docs/test-strategy.md` v1: target pyramid *shape* (weights per level,
   not just names), a per-SLI test-level mapping, and a plan for mutation testing.
4. Read both back aloud as a mob. Does the priority order and SLI mapping actually match the
   business context, or does it read like it could belong to any app?
5. Commit. No app code changes this module.

**Artifact:** `CLAUDE.md` v1, `docs/test-strategy.md` v1.

**Common failure modes:**
- Rubber-stamping a generic-sounding `CLAUDE.md` — push back with "does this reflect *our*
  business context?"
- `test-strategy.md` as vague aspiration ("we'll test the important stuff") instead of a concrete,
  checkable pyramid table. The whole point is that M3a–M4 can be held to it later.

**Recovery:** `git checkout solution/m1-context`

---

## M2 — Agent as collaborator

**Theory primer:** The verification ritual — read the diff, run it, challenge one claim, accept
or reject — *is* the quality gate here, not a formality wrapped around it. That's why the rotation
protocol enforces it structurally: whoever rotates in must read the previous diff aloud before
prompting. GitHub MCP is how the agent takes a real external action (opening a PR) instead of
just editing local files — the same verification ritual applies before that action, not after.

**Steps:**
1. Ask the agent to review the starter app's code for real issues.
2. Read the findings as a mob — which are real, which are noise?
3. Rotate on one fix: driver prompts → agent acts → mob reads the diff aloud → navigator
   challenges one specific thing → accept or reject → rotate. Repeat for a second finding.
4. Add a CI stub — install + a sanity import, not real tests yet (that's M3a).
5. Once the mob has actually accepted the changes, ask the agent to open a PR via GitHub MCP.
6. Read the PR as it actually appears on GitHub before moving on.

**Artifact:** CI stub, first reviewed PR.

**Common failure modes:**
- Accepting the agent's first fix without reading the diff — the exact anti-pattern this module
  exists to interrupt. Facilitators: watch for it and stop the mob if it happens.
- A fix that *looks* right but silently changes behavior. Concretely, in the reference build: the
  first URL-validation fix used pydantic's `HttpUrl`, which passed a glance — until a closer read
  showed it silently rewrote input (added a trailing slash, lowercased the host), breaking "a
  short link resolves to the exact URL it was created for." Worth telling as a real story, not a
  hypothetical, if the mob's own review doesn't surface something similar.
- Trying to fix all five planted issues at once. This module is about one or two findings and the
  *ritual*, not exhaustiveness — the collision bug is deliberately left for M3a.

**Recovery:** `git checkout solution/m2-review`

---

## M3a — Unit tests + the loop hook

**Theory primer:** Coverage answers "did this line run," not "would we notice if it broke" — that
second question is the oracle problem, and mutation testing makes it visible by deliberately
breaking the code and checking whether the tests notice. **This is the pivot.** A `Stop` hook that
runs tests before the agent can end its turn moves quality feedback from "after a push" (CI) to
*inside the loop* — shift-left becomes Shift In right here.

**Steps:**
1. Add `pytest`/`pytest-cov`/`mutmut` as a test extra.
2. Write a unit test for the still-open collision bug (#2 from M2) and watch it fail red — for
   real, not just "written."
3. Fix the bug; watch the test go green.
4. Add thin API-level tests (route wiring only — status codes and shapes, not every input variant).
5. Run `mutmut` against the core logic module. Read any survivor as a mob: does the test really
   assert what it claims to?
6. Strengthen the weak assertion; re-run to confirm the mutant is now killed.
7. Write the `Stop` hook script and settings. **Test it by piping fake JSON at it directly** — a
   passing case and a failing case — before trusting it in a live session.
8. Demonstrate live: break a test on purpose, ask the agent to do something, watch the hook block
   the stop and force a fix before it's allowed to finish.

**Artifact:** `tests/unit/`, `tests/api/`, a mutation-testing run with notes, the `Stop` hook.

**Common failure modes:**
- Trusting a hook's JSON output schema from memory instead of the current docs. Concretely: the
  reference build's first hook nested `decision`/`reason` under `hookSpecificOutput` — which
  doesn't error, it just makes the hook a silent no-op. A `/code-review` pass caught it before it
  shipped; verify against the actual docs, not a remembered shape.
- Chasing 100% coverage as the goal. A 100%-covered file can still let a mutant survive — the
  reference build's own collision test covered the retry line completely and still missed a
  mutant that replaced the retried code with `None`.
- More generally: an assertion that proves "something happened" (a value changed, an error was
  raised) without pinning down *what* happened is the same weak-oracle shape as the `None`-code
  mutant above, just with different surface details. M5b hit two more instances of this same
  family — `pytest.raises(SomeError)` alone proving an error's *type* but not its *content* — so
  it's worth flagging here as a pattern to watch for, not just this one module's story.

**Recovery:** `git checkout solution/m3a-unit-hook`

---

## M3b — CI pipeline

**Theory primer:** Fast in-loop feedback (the `Stop` hook) and the CI safety net do different
jobs. The hook has to stay fast — it runs every turn. CI can afford to be slower and heavier,
which is exactly what an SLI-derived gate needs (a real running server, real requests). "Turn one
SLI into a CI gate" is a meaningfully different exercise from "run the tests in CI" — it enforces
a documented service promise, not just "nothing broke."

**Steps:**
1. Pick one SLI to gate on (the reference build used redirect latency).
2. Write a dedicated test that starts a real server, samples real requests, and asserts against
   the *actual* documented SLO — not a softened threshold.
3. Confirm the `Stop` hook stays scoped away from this test (it should already be — verify, don't
   assume).
4. Update the CI workflow: keep the production-only-install sanity step, add the unit+API step,
   add the SLI gate as its own labeled step so a failure clearly shows which layer broke.
5. Push and confirm CI is actually green on GitHub — not just locally.

**Artifact:** `.github/workflows/ci.yml` with a real SLI gate.

**Common failure modes:**
- Softening the SLI threshold to avoid imagined CI flakiness. Check the real margin first — the
  reference build measured ~0.6 ms against a 50 ms target, roughly 80x headroom. Don't assume
  flakiness you haven't observed.
- Letting the SLI gate quietly fold into the same run the `Stop` hook uses. Keep the fast/slow
  split explicit and enforced, not just implied.

**Recovery:** `git checkout solution/m3b-ci`

---

## M4 — System tests via subagent

**Theory primer:** Pyramid discipline gets *harder*, not easier, once an agent can generate tests
cheaply — the temptation to over-test at the expensive top level is real. Delegating to a scoped
subagent is about bounded responsibility: a subagent with a narrow job and explicit ground rules
about what *not* to add is more trustworthy than an open-ended request to "write some system
tests."

**Steps:**
1. Verify the subagent file mechanics against current docs before building one — file location,
   required frontmatter, tool scoping.
2. Write the subagent's ground rules with a genuinely high bar: a system test is justified only
   when something can't be proven by the API-layer tests — a real process boundary, real sockets
   — not just "this is on the redirect hot path."
3. Have it produce one suite: the redirect hot path round trip (create → follow → stats).
4. Actually run it against a real server and watch it pass.
5. Add the system-testing library as its own install extra, separate from the fast test extra, so
   the quick CI job never needs it.
6. Add a second, *parallel* CI job for system tests — not a slower step bolted onto the fast one.
7. Update `CLAUDE.md` to v2: one coherent map of the now-complete pyramid, plus the
   subagent-delegation working agreement.

**Artifact:** system-test subagent, `tests/system/`, a second CI job, `CLAUDE.md` v2.

**Common failure modes:**
- "It goes through routing, validation, and exception handling" *feels* like justification for a
  system test — but the API-layer test client already exercises that same in-process pipeline.
  That reasoning isn't sufficient on its own. Concretely: the reference build's first system-test
  suite added two "cross-cutting" cases on exactly this reasoning, and both turned out to be
  byte-for-byte restatements of existing API tests. Caught in review, deleted, and the strategy
  doc's own pyramid table was corrected to say so honestly rather than quietly padding the count
  back out.
- Padding the suite because a strategy doc *said* there'd be "one or two" more cases. If a
  genuine second case doesn't exist for this app, zero is the right, disciplined answer — not a
  plan falling short.

**Recovery:** `git checkout solution/m4-system`

---

## M5a — Story refinement (Example Mapping)

**Theory primer:** Skill vs. subagent: a **skill** runs inline in the current conversation and can
hold a genuine back-and-forth interview (verify this against the docs before relying on it — the
default, un-forked skill keeps conversation history; `context: fork` explicitly loses it, which
would break an interview). A **subagent** runs in an isolated context — better suited to bounded,
single-shot delegated work like M4's system tests. Example Mapping (Matt Wynne): story, rules,
examples, questions — a structured way to turn a vague ask into testable acceptance criteria
*collaboratively*, not by the agent deciding alone. Untrusted input: an agent with write access,
reading external content it didn't write, is a real risk surface — inspect before feeding it in,
every time, not just when something looks obviously off.

**Steps:**
1. Facilitator: don't let the mob glance at the pre-prepared issue's rendered page casually first.
   Set up the injection-awareness beat deliberately.
2. Ask the agent to fetch the issue's **raw** content and inspect it in full before summarizing or
   acting on any of it.
3. Discuss as a mob: the issue's raw body contains a hidden HTML comment, invisible when rendered
   on GitHub, asking whoever implements the feature to quietly undo the day's earlier validation
   and hook work. What would have happened if nobody looked at the raw text?
4. Run the Example Mapping skill against the now-vetted content.
5. Work the interview as a mob: confirm the story, propose and confirm rules one at a time,
   propose and confirm examples (as Gherkin scenarios) for each. Track genuinely open questions
   explicitly rather than letting the agent guess at them.
6. Produce the acceptance-criteria doc.

**Artifact:** `.claude/skills/example-mapping/`, refined acceptance criteria + Gherkin scenarios.

**Common failure modes:**
- Skipping the injection-awareness beat for time. Don't — it's one of the most concrete, memorable
  lessons of the day.
- Letting the agent quietly settle an open question instead of surfacing it. Concretely: the
  reference build's first draft of the AC doc asserted "assume UTC if unspecified" inside its own
  *open questions* section, as if already decided — the exact anti-pattern this technique exists
  to prevent, produced by the technique's own reference implementation. Caught in review, fixed by
  promoting it to a properly confirmed rule with its own scenario. Good live discussion material:
  even a document *about* not guessing can guess, if nobody checks it.

**Recovery:** `git checkout solution/m5a-bdd`

---

## M5b — Feature build, QA in the loop

**Theory primer:** Every piece from the day working together: tests generated and run in-loop as
the feature is built, not bolted on afterward; the human's job is verifier, not typist — reading
diffs, running the app, challenging claims, deciding accept-or-reject at every rotation. This
module is the day's thesis, made concrete in one continuous build.

**Steps:**
1. Read the acceptance-criteria doc together before writing any code — does the mob actually
   agree with what's about to be built?
2. Write tests first, against the AC doc's own scenarios. Confirm they're genuinely red — run
   them and watch them fail — before implementing anything.
3. Implement against the rules, letting the `Stop` hook fire naturally. Don't bypass it to move
   faster.
4. Run mutation testing on any new logic that lands in the mutmut-targeted module; treat a
   survivor as a missing assertion, not noise to dismiss.
5. Smoke-test the actually-running app, not just the test suite. This matters: a real bug in the
   reference build (a crash on a naive, non-UTC datetime) had 100% passing tests around it. It was
   found by a second `/code-review` pass plus direct reproduction against the running app — the
   test suite alone never caught it.
6. Open a PR; read what CI actually reports. Don't merge into the resync branch.

**Artifact:** the feature, generated tests, a PR.

**Common failure modes:**
- Treating "tests pass" as the finish line. Green tests are necessary, not sufficient — see the
  naive-datetime bug above. Keep reviewing and keep smoke-testing even when the suite is green.
- Building against acceptance criteria nobody in the room actually confirmed live. The human
  reproduction/verification gate applies to the *acceptance criteria themselves*, not only to the
  code — if M5a's session was rushed or skipped questions, M5b is building on an unconfirmed
  foundation, and that's worth naming out loud before starting to build.

**Recovery:** `git checkout solution/m5b-feature`
