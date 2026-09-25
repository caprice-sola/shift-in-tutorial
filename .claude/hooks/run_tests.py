#!/usr/bin/env python3
"""Stop hook: run pytest, and block Claude from stopping if it fails.

Registered under hooks -> Stop in .claude/settings.json. Output shape per
https://code.claude.com/docs/en/hooks#stop-decision-control : Stop is one of
the events that use the "standard decision model", so a top-level
`{"decision": "block", "reason": "..."}` printed to stdout on exit 0 is
enough to keep Claude going — no exit code 2 needed. Omitting `decision`
(or printing nothing) allows the stop, which is what happens here when the
suite passes.
"""

import json
import os
import subprocess
import sys

# Read (and discard) the hook's stdin input. We don't need any field from
# it, but Claude Code always sends one and expects the process to consume
# stdin cleanly.
sys.stdin.read()

project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
venv_pytest = os.path.join(project_dir, ".venv", "bin", "pytest")
pytest_cmd = venv_pytest if os.path.exists(venv_pytest) else "pytest"

result = subprocess.run(
    [pytest_cmd, "tests/unit", "tests/api"],  # never tests/gates: real server, ~1s
    cwd=project_dir,
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    output = (result.stdout + result.stderr).strip()
    print(json.dumps({
        "decision": "block",
        "reason": f"pytest failed, fix before stopping:\n\n{output}",
    }))

sys.exit(0)
