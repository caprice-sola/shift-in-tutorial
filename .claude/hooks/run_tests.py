#!/usr/bin/env python3
"""Stop hook: don't let the agent end its turn while pytest is red.

This is the shift-left -> Shift In pivot for this workshop (docs/shift-in-thesis.md):
quality feedback moves from "after a push" (CI, M3b) to "before the agent's turn
even ends." See docs/test-strategy.md for what these tests are supposed to cover.
"""
import json
import subprocess
import sys

MAX_REASON_CHARS = 4000


def main() -> None:
    payload = json.load(sys.stdin)
    if payload.get("stop_hook_active"):
        return  # already blocked once this turn - don't loop forever

    try:
        result = subprocess.run(
            ["pytest", "-q"],
            capture_output=True,
            text=True,
            cwd=payload.get("cwd"),
        )
    except FileNotFoundError:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "Stop",
                "decision": "block",
                "reason": "pytest isn't installed/on PATH. Run `pip install -e \".[test]\"` "
                           "(from the repo root, in your active environment) before finishing.",
            }
        }))
        return

    if result.returncode == 0:
        return  # tests pass, allow the stop

    output = (result.stdout + result.stderr).strip()
    if len(output) > MAX_REASON_CHARS:
        output = output[-MAX_REASON_CHARS:]
    reason = f"pytest is failing - fix before finishing:\n\n{output}"
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "decision": "block",
            "reason": reason,
        }
    }))


if __name__ == "__main__":
    main()
