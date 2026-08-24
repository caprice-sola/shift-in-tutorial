# Module guide (TEMPLATE — author in backlog T9)

For each sub-module, fill in: a short theory primer (what & why, ~5 min to deliver), the step
list the mob follows, the expected artifact, and common failure modes + how to recover.
Do not write these until the solution branches are proven, so the steps match reality.

---

## M1 — Foundations
**Theory primer (5 min):** _TODO — the instructions file as living context; strategy as an executable artifact._
**Steps:** _TODO_
**Artifact:** `app/CLAUDE.md` v1, `app/docs/test-strategy.md` v1
**Recovery:** `git checkout solution/m1-context`

## M2 — Agent as collaborator
**Theory primer:** _TODO — verification ritual; MCP as the agent's hands._
**Steps:** _TODO_
**Artifact:** first reviewed PR
**Recovery:** `git checkout solution/m2-review`

## M3a — Unit tests + the loop hook
**Theory primer:** _TODO — coverage as a map; the oracle problem; the loop hook = Shift In pivot._
**Steps:** _TODO_
**Artifact:** `tests/unit/`, `Stop` hook
**Recovery:** `git checkout solution/m3a-unit-hook`

## M3b — CI pipeline
**Theory primer:** _TODO — fast in-loop feedback vs. the CI safety net; SLI gates._
**Steps:** _TODO_
**Artifact:** `.github/workflows/ci.yml`
**Recovery:** `git checkout solution/m3b-ci`

## M4 — System tests via subagent
**Theory primer:** _TODO — pyramid discipline when tests are cheap; delegating to a subagent._
**Steps:** _TODO_
**Artifact:** system-test subagent, `tests/system/`, `app/CLAUDE.md` v2
**Recovery:** `git checkout solution/m4-system`

## M5a — Story refinement (Example Mapping)
**Theory primer:** _TODO — skill vs subagent vs command; Example Mapping technique; agent-led
discovery; untrusted input._
**Steps:** _TODO_
**Artifact:** `.claude/skills/example-mapping/`, enhanced AC + BDD scenarios
**Recovery:** `git checkout solution/m5a-bdd`

## M5b — Feature build, QA in the loop
**Theory primer:** _TODO — the full Shift In loop; human as verifier._
**Steps:** _TODO_
**Artifact:** feature + generated tests + PR
**Recovery:** `git checkout solution/m5b-feature`
