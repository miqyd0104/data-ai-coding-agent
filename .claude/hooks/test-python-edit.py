"""Run tests for Python file edits and return failures in Claude's hook format."""

import json
import subprocess
import sys
from pathlib import Path


def handle_edit(event, runner=subprocess.run):
    path = event.get("tool_input", {}).get("file_path", "")
    if not path.endswith(".py"):
        return None
    # Resolve from the edited file, so a session in a subdirectory still tests
    # the correct checkout (including a Git worktree).
    for parent in Path(path).resolve().parents:
        if (parent / "pyproject.toml").is_file():
            root = parent
            break
    else:
        return {"decision": "block", "reason": "Cannot locate the Python project for this edit."}
    try:
        result = runner(["uv", "run", "pytest", "-q"], cwd=root, capture_output=True,
                        text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"decision": "block", "reason": f"Could not run tests: {error}"}
    if result.returncode:
        return {"decision": "block", "reason":
                "Tests failed after the Python edit. Fix these failures:\n"
                + (result.stdout + result.stderr)[-16000:]}
    return {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                   "additionalContext": "uv run pytest -q passed."}}


if __name__ == "__main__":
    response = handle_edit(json.load(sys.stdin))
    if response is not None:
        print(json.dumps(response))
