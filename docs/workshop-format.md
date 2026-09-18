# Workshop format

## Mob programming, agent edition

Teams of **3 around one machine**, with Claude Code as the typist. Because the agent generates
the code, the valuable seat is the **verifier**, not the keyboard. We make that explicit by
turning the verification ritual into the rotation protocol:

> **Driver** writes the prompt → **agent acts** → the mob **reads the diff aloud together** →
> a **Navigator challenges one thing** → accept or reject → **rotate**.

The handoff *is* the quality gate. This is the human reproduction / verification gate in action.

## Rotation rules

- Rotate on **task boundary**, not a hard timer; soft ceiling ~8 minutes per turn.
- Whoever rotates **in** must read the previous diff aloud and state intent before prompting.
  (This is the cure for the "passive passenger" problem, which is worse when the screen scrolls
  on its own.)
- Over a 35–75 min module, 3 people get ~2–3 turns each — enough that nobody ossifies into the
  "prompt person."

## Setup (protect the first 30 minutes)

- Pre-provision **one facilitator laptop per mob**, already authenticated with Claude Code and the
  repo cloned. ~4–6 mobs means ~4–6 machines, not 15.
- Attendees bring their own GitHub account and their own Claude subscription — there's no shared
  facilitator-provisioned token to manage. Send pre-work asking each attendee to **install** the
  GitHub CLI (`cli.github.com`; `brew install gh` / `winget install --id GitHub.cli`) **and**
  authenticate it (`gh auth login`) before the day, and to confirm both with `gh --version` and
  `gh auth status`. Installing and authenticating is never a live exercise — *using* it is. (GitHub MCP is optional, not the default: its official remote
  server currently can't complete OAuth — a live upstream bug, confirmed via a real dry run, not a
  one-off setup mistake — so building the exercise's success around it live would be a single
  point of failure for every mob at once. `docs/github-cli-notes.md` on the solution branches
  documents the MCP path anyway, PAT workaround included, for a mob that wants to try it.)
- Send pre-work a few days out: install/auth, clone, run one smoke prompt. The 09:00–09:30 slot is
  a **sanity check** ("make the agent edit a file"), not a from-scratch install.
- Two setup facts the M3a `Stop` hook depends on, so settle them at 09:00 rather than at 11:30:
  start `claude` **from an activated virtualenv** (the hook calls `pytest` from `PATH` — with no
  venv active it blocks every turn with "couldn't run pytest"), and **accept the workspace-trust
  dialog** on first start — Claude Code holds back every settings-file hook until the folder is
  trusted, so a hook committed in `.claude/settings.json` silently does nothing before then.

## Two anti-patterns to defend against all day

1. **Coverage theatre.** Agents produce high-coverage tests that assert little. Counter: coverage
   is a map of gaps, not a target; prove oracles by breaking the code on purpose (M3a).
2. **Pyramid inversion.** Agents happily generate slow end-to-end tests for everything. Counter:
   add coverage at the lowest level that gives confidence; the test strategy (M1) sets the target
   distribution the agent must respect (M4).

## Recurring rituals

- **Update the instructions file** (`app/CLAUDE.md`) as a deliberate step at module boundaries.
- **Inspect untrusted input** before feeding it to an agent that can act (M5 issue).
- **Retro question:** "Where did the agent help, and where did it mislead you?" — metacognition
  that also lands the Shift In message.
