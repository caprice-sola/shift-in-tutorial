#!/usr/bin/env python3
"""Stop hook: don't let the agent end its turn while pytest is red.

This is the shift-left -> Shift In pivot for this workshop: quality feedback moves
from "after a push" (CI, M3b) to "before the agent's turn even ends." See
docs/test-strategy.md for what these tests are supposed to cover.
"""
import json
import subprocess
import sys

MAX_REASON_CHARS = 4000

# NOTE: decision/reason are TOP-LEVEL fields for a Stop hook - NOT nested under
# hookSpecificOutput (that wrapper is for events like PreToolUse/UserPromptSubmit
# that need a hookEventName-scoped shape). Getting this wrong doesn't error, it
# just makes the hook a silent no-op: verified against code.claude.com/docs/en/hooks
# and hooks-guide.md ("PostToolUse and Stop hooks use a top-level decision: 'block'
# field") after a review pass caught the nested version failing to block.


def block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}))


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return  # can't tell what's going on; don't block on unreadable input

    if payload.get("stop_hook_active"):
        return  # already blocked once this turn - don't loop forever

    try:
        result = subprocess.run(
            # unit + api only - tests/gates spins up a real server for the
            # SLI latency gate (M3b) and belongs in CI, not every turn-end.
            ["pytest", "-q", "--tb=short", "tests/unit", "tests/api"],
            capture_output=True,
            text=True,
            cwd=payload.get("cwd"),
        )
    except OSError as exc:
        block(f"Couldn't run pytest ({exc}). If it's not installed, run "
              "`pip install -e \".[test]\"` from the repo root before finishing.")
        return

    if result.returncode == 0:
        return  # tests pass, allow the stop

    output = (result.stdout + result.stderr).strip()
    if len(output) > MAX_REASON_CHARS:
        output = output[-MAX_REASON_CHARS:]

    if result.returncode == 5:
        block(f"pytest collected zero tests (exit 5) - check cwd/testpaths, "
              f"not a real failure:\n\n{output}")
    else:
        block(f"pytest is failing - fix before finishing:\n\n{output}")


if __name__ == "__main__":
    main()
