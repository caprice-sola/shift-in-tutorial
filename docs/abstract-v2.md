# Shift In: Making Your AI Coding Agent a Quality Engineer

**Full-day hands-on tutorial · ~6 hours · mob programming · bring your curiosity, we bring the repo**

## The opportunity

AI coding agents — GitHub Copilot, Claude Code — have already shown they can write, refactor, and test code at remarkable speed, and teams are seeing real value from them every day. The question is no longer whether they help, but how far we can take them. Today, most teams use the agent as a fast, capable assistant alongside their existing workflow. The bigger prize is to make it a full participant in the team's quality engineering — so the speed it brings arrives with the confidence to match.

That next step matters because agents change where quality work naturally lives. Shift-left moved testing *earlier in time*, a real advance when humans wrote every line. An agent compresses code, tests, and decisions into a single generative loop that runs continuously — which means quality no longer has to sit only *before* the loop (in planning) or *after* it (in CI). It can travel *inside* the loop, with the agent, as it works. Unlocking that is what this tutorial is about: **moving quality into the loop itself.**

## What we'll do

We start with a real, running application in a Git repository — business context, quality characteristics, and SLIs already defined, but not a single line of AI-assisted engineering yet. Working in small mobs of three around one machine, each team takes that repo from bare to a fully quality-engineered delivery pipeline, using the AI agent at every step. We use Claude Code as the reference implementation and call out where Copilot is similar or different throughout.

The day progresses through seven short exercises, each with a brief theory primer up front:

1. **Understand the business context.** Turn the team's DoR/DoD, quality characteristics, and SLIs into the agent's standing instructions and a shared test strategy the agent actually consults — written *before* a single test exists, so the later exercises have something to be held to.
2. **The agent as collaborator.** Run an AI code review, verify the diff together as a mob, and open a pull request from the terminal — establishing the ritual we reuse all day: read the diff, run it, question one claim, accept or reject.
3. **Unit tests and the loop hook.** Build a unit suite ordered by the SLIs, then break the code on purpose to expose tests that pass while asserting nothing. Write "a turn never ends with a failing test" into the agent's instructions — then, twenty minutes later, wire the hook that *enforces* it. Feeling the difference between asking an agent for something and enforcing it is where shift-left becomes Shift In.
4. **The CI pipeline.** Build it from nothing: a production-only install check, the test run, and one gate derived from a published SLI — measured against a real running server, at the documented threshold rather than a convenient one.
5. **A skill, then a subagent.** Encode *how* your team writes a system test as a **skill**, use it to write and run the first end-to-end suite, and only then delegate the **system tester role** to a subagent that preloads that skill: analyse the test basis, design the cases, implement, run. Technique in the skill, judgment in the subagent — with a hard rule that stops a cheap test generator burying you in slow end-to-end tests.
6. **System regression in the pipeline.** Add the slower suite as its own parallel job, installing only what it needs, so fast feedback stays fast and a red build already tells you which level broke.
7. **The feature build — quality in the loop.** Take a pre-prepared issue and inspect its raw text before feeding it to an agent that can write to your repo. Refine it through Example Mapping, driven by a second skill of a different shape — one that interviews the team rather than applying a procedure. Then let the agent build the feature: tests first from the confirmed acceptance criteria, the hook firing as it works, a smoke test against the running app, and a PR — with humans as the verification gate throughout.

## The strong message: Shift In

Shift-left asked us to test earlier. **Shift In** asks something different: embed quality engineering directly into the agent's reasoning-and-acting loop, so the agent generates, tests, and gates its own work as it goes — and the human's role shifts from typist to verifier. The hook that runs tests before the agent stops, the skill that encodes a repeatable technique, the subagent that holds a testing role with written limits, the SLI that became a pipeline gate, the human reproduction gate on every accepted change: these are not add-ons to AI coding. They are how quality survives autonomy.

## What you'll take away

- A working pattern for turning business context, DoR/DoD, and SLIs into an agent's standing instructions and an executable test strategy — and the habit of rewriting that file at module boundaries rather than once.
- A practical toolkit — instructions files, skills, subagents, hooks, and MCP — and clear judgment about when to reach for each, starting with the distinction that decides most of it: a **skill** carries a method, a **subagent** carries a role.
- Techniques to keep AI-generated tests honest and well-shaped: deliberately breaking code, by hand, in minutes, to confirm your tests really assert something — and keeping the pyramid the right way up when generating a slow test costs nothing.
- A mob-based verification ritual that keeps a human as the quality gate, even at agent speed.
- A concrete mental model of Shift In you can apply to your own codebase on Monday — plus the repository, eight solution branches to resync from, and the slide deck to take home.

*No prior experience with AI coding agents required. Comfort with Git, basic Python, and a willingness to give away the keyboard expected.*

---

_v2 — aligned with the built exercises. Changes from v1: exercise 3 writes the test agreement as an instruction before the hook enforces it; exercise 4 creates the pipeline rather than extending a stub; exercise 5 builds a **skill** first and then a subagent that preloads it, described as a testing role rather than a test generator — which moves the introduction of skills here from exercise 7; exercise 7's Example Mapping skill is framed as the second, differently-shaped skill; mutation testing is done by hand rather than with `mutmut`. Exercise count, format, timing and prerequisites are unchanged. Two things deliberately left out as too inside-baseball for an abstract but worth mentioning on stage: the three deliberate rewrites of the instructions file, and the restart in exercise 5 that discards the conversation and so proves what standing context is for._
