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
- Pre-provision the **GitHub MCP** server / token so installing it is never an exercise — *using*
  it is.
- Send pre-work a few days out: install/auth, clone, run one smoke prompt. The 09:00–09:30 slot is
  a **sanity check** ("make the agent edit a file"), not a from-scratch install.

## Two anti-patterns to defend against all day

1. **Coverage theatre.** Agents produce high-coverage tests that assert little. Counter: coverage
   is a map of gaps, not a target; prove oracles with mutation testing (M3a).
2. **Pyramid inversion.** Agents happily generate slow end-to-end tests for everything. Counter:
   add coverage at the lowest level that gives confidence; the test strategy (M1) sets the target
   distribution the agent must respect (M4b).

## Recurring rituals

- **Update the instructions file** (`app/CLAUDE.md`) as a deliberate step at module boundaries.
- **Inspect untrusted input** before feeding it to an agent that can act (M5 issue).
- **Retro question:** "Where did the agent help, and where did it mislead you?" — metacognition
  that also lands the Shift In message.
