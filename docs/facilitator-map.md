# Facilitator map

Full day, **09:00–17:00**. 480 minutes = 360 net teaching + 60 lunch + 2×30 breaks.
Format: small **mobs of 3** around one machine, **Claude Code** as the reference implementation.

## Clock

| Time | Sub-module | Maps to | Resync branch |
|---|---|---|---|
| 09:00–09:30 | Setup & orientation | — | `start` |
| 09:30–10:00 | **M1** Foundations | Ex1 | `solution/m1-context` |
| 10:00–10:45 | **M2** Agent as collaborator | Ex2 | `solution/m2-review` |
| 10:45–11:15 | Break | | |
| 11:15–12:00 | **M3a** Unit tests + the loop hook | Ex3 | `solution/m3a-unit-hook` |
| 12:00–12:30 | **M3b** CI pipeline | Ex4 | `solution/m3b-ci` |
| 12:30–13:30 | Lunch | | |
| 13:30–14:10 | **M4a** API tests via skill | Ex5 | `solution/m4a-api` |
| 14:10–14:45 | **M4b** System tests via subagent | Ex6 + Ex7 | `solution/m4b-system` |
| 14:45–15:15 | Break | | |
| 15:15–15:50 | **M5a** Story refinement (Example Mapping) | Ex8 pt1 | `solution/m5a-bdd` |
| 15:50–16:30 | **M5b** Feature build, QA in the loop | Ex8 pt2 | `solution/m5b-feature` |
| 16:30–17:00 | Retro & wrap | — | — |

Each `solution/*` branch is also the **start** of the next sub-module, so a stuck mob checks out
the previous branch and rejoins. Do a checkpoint walk at every break and at lunch.

## Per sub-module: objective · artifact · Copilot delta

**M1 Foundations** — *Turn business context + DoR/DoD + SLIs into standing agent context and a
shared test strategy.* Artifact: `app/CLAUDE.md` v1, `app/docs/test-strategy.md` v1.
Copilot: same content split across `.github/copilot-instructions.md` + scoped `*.instructions.md`.

**M2 Agent as collaborator** — *Run AI code review, verify the diff as a mob, open a PR via
GitHub MCP.* Artifact: first reviewed PR. Introduce the rotation-as-verification ritual here.
Copilot: GitHub + Playwright MCP are enabled by default; for Claude you point at a pre-provisioned server.

**M3a Unit tests + loop hook** — *Generate units, expose weak oracles with mutation testing, run
tests inside the agent loop.* Artifact: `tests/unit/`, `Stop` hook in `.claude/settings.json`.
**This is the shift-left → Shift In pivot.** Copilot: hooks exist (e.g. `preToolUse`), configured differently.

**M3b CI pipeline** — *Gate every commit in CI with one SLI check.* Artifact:
`.github/workflows/ci.yml`. Copilot: identical GitHub Actions.

**M4a API tests via skill** — *Author a skill for contract/property testing.* Artifact:
`.claude/skills/api-testing/`, `tests/api/` (Schemathesis). Copilot: Agent Skills + a "write tests" custom agent.

**M4b System tests via subagent** — *Delegate Robot Framework suites at the right pyramid level;
add a slow CI stage.* Artifact: system-test subagent, `tests/system/`, `app/CLAUDE.md` v2.
Copilot: custom-agent profile with its own MCP; Robot is tool-agnostic.

**M5a Story refinement** — *Refine AC + scenarios via Example Mapping with a BDD agent that asks
questions.* Artifact: enhanced AC + BDD scenarios. Run the 5-min injection-awareness beat on the
pre-prepared issue. Copilot: custom agent / prompt file.

**M5b Feature build** — *Build the feature with QA embedded in the loop; green CI; PR opened.*
Artifact: feature + generated tests + PR. Copilot: drive via Copilot CLI/IDE; mention the cloud
agent's autonomous issue→PR path as a retro contrast (don't run it live — it hides the loop).

## Dependencies (for cutting modules)

Cleanly droppable: M3b, M4a, M4b, M5a. **M5b depends on M4 (skills/subagents) and M3b (CI)**; if
those are cut, use the lite M5b below that relies only on M1 + M3a outputs.

## Half-day cuts (reuse the same branches)

- **3h (09:00–12:00):** Setup 20 → M1 30 → M2 40 → break 20 → M3a 50 → retro 20. Ends on the
  Shift In pivot; retro previews M4/M5 as "what scaling looks like."
- **3.5h (09:00–12:30):** As above through M3a, then **lite M5b** (40): small issue, ~5-min
  Example Mapping, agent builds, the loop hook runs unit tests, PR opened → 15-min retro.
