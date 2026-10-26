#!/usr/bin/env python3
"""Stop hook: run the suite and refuse to let the turn end while it is red.

Reads the Stop hook JSON from stdin. On a failing run it prints
{"decision": "block", "reason": <pytest output>} and exits 0; on a green run it
prints nothing, which lets Claude stop.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

TESTS = ["tests/unit", "tests/api"]
TIMEOUT_SECONDS = 300
MAX_REASON_CHARS = 6000
NO_TESTS_COLLECTED = 5


def block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


def main() -> None:
    hook_input = json.load(sys.stdin)
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or hook_input.get("cwd") or ".")
    venv_python = project / ".venv" / "bin" / "python"
    python = str(venv_python) if venv_python.exists() else sys.executable

    try:
        result = subprocess.run(
            [python, "-m", "pytest", *TESTS, "-q"],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        block(f"pytest did not finish within {TIMEOUT_SECONDS}s. Fix the hang or say you could not.")

    output = (result.stdout + result.stderr).strip()

    if "No module named pytest" in output:
        # Environment problem, not a test failure: report it without trapping the turn.
        print('pytest is not installed; run: pip install -e ".[test]"', file=sys.stderr)
        sys.exit(1)

    if result.returncode in (0, NO_TESTS_COLLECTED):
        sys.exit(0)

    if len(output) > MAX_REASON_CHARS:
        output = "...(truncated)...\n" + output[-MAX_REASON_CHARS:]
    block(f"pytest {' '.join(TESTS)} failed. Fix the failing tests, or say clearly that you could not.\n\n{output}")


if __name__ == "__main__":
    main()
