# Using GitHub MCP in M2

The facilitator pre-provisions a GitHub MCP server for the workshop, so installing it is never
part of the exercise — using it is. Once connected, Claude Code gets GitHub actions (open a PR,
read a PR, comment, etc.) as tools it can call directly, instead of you leaving the terminal for
the GitHub web UI or a separate `gh` command.

## The M2 flow

1. **Review first.** Ask the agent to review the diff (or the relevant files) before anything is
   proposed as final. This is the "AI code review" step — treat its findings as a starting point
   for discussion, not a verdict.
2. **Verify as a mob before anything ships.** This is the rotation ritual: driver writes the
   prompt → agent acts → the mob reads the diff aloud together → the navigator challenges one
   thing → accept or reject. Do this *before* opening a PR, not after — the PR should already
   represent something the mob agreed with.
3. **Open the PR via the MCP tool**, once the mob has actually accepted the change. Ask for it
   directly, e.g.:
   > "Open a PR from this branch into `solution/m1-context` (or your working branch) titled
   > '...', summarizing what the review found and what we fixed."
4. **Read what comes back.** The agent will report a PR URL/number — open it and confirm the diff
   on GitHub matches what the mob just verified locally. A PR opened by an agent is still an agent
   claim until a human has looked at the rendered diff.

## What to expect the review to catch here

Two of the planted issues in this starter app are the kind an AI review typically surfaces fast:
missing input validation on link creation, and an unhandled lookup that turns a "not found" into a
server error. A third (short-code collisions) is subtler and easy for a quick pass to miss —
worth a deliberate "did we check for X?" prompt from the navigator rather than assuming the review
was exhaustive. Coverage of *review* is also a map of gaps, not a guarantee.

## Copilot equivalent

GitHub MCP (and Playwright MCP) ship enabled by default in Copilot's agent mode — there's no
separate provisioning step. The workflow above — review, mob verification, then open the PR — is
identical regardless of which agent is driving.
