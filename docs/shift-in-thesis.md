# The Shift In thesis

## From shift-left to Shift In

**Shift-left** moved testing and quality activities earlier in time. When humans wrote every
line of code, "earlier" was the right axis to optimise: catch defects in design and unit test
rather than in production.

An autonomous coding agent changes the geometry. Code, tests, and decisions no longer happen at
separate points on a timeline — they happen inside a single **generative loop** (reason → act →
observe → repeat) that runs continuously and faster than a human can supervise step by step.

If quality only lives *before* the loop (planning, refinement) or *after* it (CI, review), the
agent spends most of its working life unsupervised. **Shift In** is the move that follows
shift-left: embed quality engineering *inside* the agent's loop, so the agent generates, tests,
and gates its own work as it goes — and the human's role shifts from typist to **verifier**.

## What "inside the loop" looks like in practice

- **Hooks** that run the test suite before the agent is allowed to finish a turn — quality
  feedback arrives within the loop, not after a push.
- **Skills** that encode a repeatable team technique — like Example Mapping — so the agent runs
  it consistently instead of improvising each time.
- **Subagents** that own a quality concern (e.g. system testing) in isolated context.
- A **human reproduction / verification gate**: nothing is "done" until a human has confirmed it.
- **SLIs** that define what "good" means and become pipeline gates.

## Why it matters for this tutorial

Every module adds one piece of in-loop quality. The pivot is the moment in M3a when a hook first
runs tests inside the agent's loop: that is where shift-left becomes Shift In. By M5 the agent
builds a whole feature with quality embedded throughout, and the mob's job is to verify, not type.

## Related ideas in the author's work

Shift In sits alongside the 3-Pillar Balanced Quality Model (Proactive / Detective / Reactive QA),
Intent-Driven Testing, and the five-layer agentic execution model (Hook → ReAct loop → PR cycle →
CI/CD → DevOps loop). The tutorial is the hands-on, single-day distillation of that thesis.
