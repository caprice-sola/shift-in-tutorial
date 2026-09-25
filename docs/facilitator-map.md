# Facilitator map

Full day, **09:00–17:00**. 480 minutes = 360 net teaching + 60 lunch + 2×30 breaks.
Format: small **mobs of 3** around one machine, **Claude Code** as the reference implementation.

## Clock

| Time | Sub-module | Maps to | Resync branch |
|---|---|---|---|
| 09:00–09:30 | Setup & orientation | — | `start` |
| 09:30–10:00 | **M1** Foundations | Ex1 | `solution/m1-context` |
| 10:00–10:40 | **M2** Agent as collaborator | Ex2 | `solution/m2-review` |
| 10:40–11:10 | Break | | |
| 11:10–12:00 | **M3a** Unit tests + the loop hook | Ex3 | `solution/m3a-unit-hook` |
| 12:00–12:30 | **M3b** CI pipeline | Ex4 | `solution/m3b-ci` |
| 12:30–13:30 | Lunch | | |
| 13:30–14:45 | **M4** System tests via subagent | Ex5 + Ex6 | `solution/m4-system` |
| 14:45–15:15 | Break | | |
| 15:15–15:50 | **M5a** Story refinement (Example Mapping) | Ex7 pt1 | `solution/m5a-bdd` |
| 15:50–16:30 | **M5b** Feature build, QA in the loop | Ex7 pt2 | `solution/m5b-feature` |
| 16:30–17:00 | Retro & wrap | — | — |

Each `solution/*` branch is also the **start** of the next sub-module, so a stuck mob checks out
the previous branch and rejoins. Do a checkpoint walk at every break and at lunch.

## Per sub-module: objective · artifact · Copilot delta

**M1 Foundations** — *Turn business context + DoR/DoD + SLIs into standing agent context and a
shared test strategy.* Artifact: `app/CLAUDE.md` v1, `app/docs/test-strategy.md` v1.
Copilot: same content split across `.github/copilot-instructions.md` + scoped `*.instructions.md`.

**M2 Agent as collaborator** — *Run AI code review, verify the diff as a mob, open a PR via
`gh` (each attendee's own `gh auth login`, done as pre-work).* Artifact: first reviewed PR.
No CI here — M2 is review and the verification ritual only; the pipeline starts in M3a.
Introduce the rotation-as-verification ritual here. GitHub MCP is the same "external actions"
category and worth a mention, but not the default: its official remote server currently can't
complete OAuth (a live upstream bug — see `docs/github-cli-notes.md` on the solution branches for
the workaround, if a mob wants to try it anyway). Copilot: GitHub + Playwright MCP are enabled by
default in its agent mode, if you want the contrast.

**M3a Unit tests + loop hook** — *Generate units, expose weak oracles by breaking the code by
hand, write the rule down, then enforce it.* Artifact: `tests/unit/`, **`CLAUDE.md` v2**, `Stop`
hook in `.claude/settings.json`. The order matters: the mob writes "a turn never ends with a
failing test" as an *instruction* first, watches how reliably it is followed, and only then adds
the hook — instruction and enforcement as two separate moves. No CI here; that is M3b.
**This is the shift-left → Shift In pivot.** Copilot: hooks exist (e.g. `preToolUse`), configured differently.

**M3b CI pipeline** — *Create the pipeline and gate every commit, including one SLI check.*
Artifact: `.github/workflows/ci.yml` — written complete here (install check, test run, SLI gate),
not upgraded from an earlier stub. Copilot: identical GitHub Actions.

**M4 A skill, then a subagent** — *Encode how to write a Robot suite as a skill, then delegate what
to test to a subagent that preloads it; add a slow CI stage.* Artifact:
`.claude/skills/system-tests/`, the system-test subagent, `tests/system/`, `app/CLAUDE.md` v3.
Install Robot Framework **first** — it used to be installed in M3b, after the first run needed it.
Ex 5 ~55 min, Ex 6 ~20.
**Order matters here:** `.claude/agents/` is a new directory, so Claude Code only discovers the
subagent after a **restart** — and a restart discards the conversation. So v3 is written *before*
the restart, which makes it the day's clearest demonstration of what standing context is for.
Copilot: custom-agent profile with its own MCP; Robot is tool-agnostic. `CLAUDE.md` reaches **v3**
here — the third and last deliberate pass (v1 M1, v2 M3a).

**M5a Story refinement** — *Refine AC + scenarios via Example Mapping, driven by a skill that
structures the interview.* Artifact: `.claude/skills/example-mapping/`, enhanced AC + BDD
scenarios. Run the 5-min injection-awareness beat on the pre-prepared issue.
Copilot: Agent Skills equivalent / prompt file.

**M5b Feature build** — *Build the feature with QA embedded in the loop; green CI; PR opened.*
Artifact: feature + generated tests + PR. Copilot: drive via Copilot CLI/IDE; mention the cloud
agent's autonomous issue→PR path as a retro contrast (don't run it live — it hides the loop).

## Dependencies (for cutting modules)

Cleanly droppable: M3b, M4, M5a. **M5b depends on M4 (subagent) and M5a (skill) and M3b (CI)**;
if those are cut, use the lite M5b below that relies only on M1 + M3a outputs.

## Half-day cuts (reuse the same branches)

- **3h (09:00–12:00):** Setup 20 → M1 30 → M2 40 → break 20 → M3a 50 → retro 20. Ends on the
  Shift In pivot; retro previews M4/M5 as "what scaling looks like."
- **3.5h (09:00–12:30):** As above through M3a, then **lite M5b** (40): small issue, ~5-min
  Example Mapping, agent builds, the loop hook runs unit tests, PR opened → 15-min retro.
