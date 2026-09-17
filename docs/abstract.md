# Shift In: Making Your AI Coding Agent a Quality Engineer

**Full-day hands-on tutorial · ~6 hours · mob programming · bring your curiosity, we bring the repo**

## The opportunity

AI coding agents — GitHub Copilot, Claude Code — have already shown they can write, refactor, and test code at remarkable speed, and teams are seeing real value from them every day. The question is no longer whether they help, but how far we can take them. Today, most teams use the agent as a fast, capable assistant alongside their existing workflow. The bigger prize is to make it a full participant in the team's quality engineering — so the speed it brings arrives with the confidence to match.

That next step matters because agents change where quality work naturally lives. Shift-left moved testing *earlier in time*, a real advance when humans wrote every line. An agent compresses code, tests, and decisions into a single generative loop that runs continuously — which means quality no longer has to sit only *before* the loop (in planning) or *after* it (in CI). It can travel *inside* the loop, with the agent, as it works. Unlocking that is what this tutorial is about: **moving quality into the loop itself.**

## What we'll do

We start with a real, running application in a Git repository — business context, quality characteristics, and SLIs already defined, but not a single line of AI-assisted engineering yet. Working in small mobs of three around one machine, each team takes that repo from bare to a fully quality-engineered delivery pipeline, using the AI agent at every step. We use Claude Code as the reference implementation and call out where Copilot is similar or different throughout.

The day progresses through seven short exercises, each with a brief theory primer up front:

1. **Understand the business context.** Turn the team's DoR/DoD, quality characteristics, and SLIs into the agent's standing instructions and a shared, versioned test strategy the agent actually consults.
2. **The agent as collaborator.** Run an AI code review, verify the diff together as a mob, and open a pull request from the terminal — establishing the verification ritual we reuse all day.
3. **Unit tests and the loop hook.** Generate unit tests, then break the code on purpose to expose tests that pass while asserting nothing — and wire a hook that runs the suite *inside the agent's loop* before it finishes. This is where shift-left becomes Shift In.
4. **The CI pipeline.** Have the agent design a pipeline that gates every commit, including one SLI-based check.
5. **System tests as a subagent.** Delegate Robot Framework system-test creation to a specialized subagent — and enforce the right pyramid level so the agent doesn't bury you in slow end-to-end tests.
6. **System regression in the pipeline.** Add the slower suite as its own stage and update the agent's instructions to keep tests at the level that gives confidence cheapest.
7. **The feature build — quality in the loop.** Take a pre-prepared issue, refine its user stories and acceptance criteria through Example Mapping — driven by a purpose-built skill — with a BDD agent that interviews the team, then let the coding agent build the feature — generating and running its own tests against the pipeline and opening a PR, with humans as the verification gate throughout.

## The strong message: Shift In

Shift-left asked us to test earlier. **Shift In** asks something different: embed quality engineering directly into the agent's reasoning-and-acting loop, so the agent generates, tests, and gates its own work as it goes — and the human's role shifts from typist to verifier. The hook that runs tests before the agent stops, the skill that encodes a repeatable technique, the subagent that owns system testing, the human reproduction gate on every accepted change: these are not add-ons to AI coding. They are how quality survives autonomy.

## What you'll take away

- A working pattern for turning business context, DoR/DoD, and SLIs into an agent's standing instructions and an executable test strategy.
- A practical toolkit — instructions files, skills, subagents, hooks, and MCP — and clear judgment about when to reach for each.
- Techniques to keep AI-generated tests honest and well-shaped — deliberately breaking code (mutation testing, done by hand in minutes) to confirm your tests really assert something, and keeping the pyramid the right way up.
- A mob-based verification ritual that keeps a human as the quality gate, even at agent speed.
- A concrete mental model of Shift In you can apply to your own codebase on Monday — plus a reusable repository and solution branches to take home.

*No prior experience with AI coding agents required. Comfort with Git, basic Python, and a willingness to give away the keyboard expected.*
