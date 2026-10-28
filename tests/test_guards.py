import importlib.util
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

HOOK_PATH = Path(__file__).resolve().parents[1] / ".claude/hooks/test-python-edit.py"
MODULE_SPEC = importlib.util.spec_from_file_location("test_python_edit_hook", HOOK_PATH)
HOOK = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(HOOK)


def test_python_edit_runs_tests_from_project_root(tmp_path):
    (tmp_path / "pyproject.toml").touch()
    calls = []

    def runner(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0, stdout="1 passed", stderr="")

    result = HOOK.handle_edit(
        {"tool_input": {"file_path": str(tmp_path / "kettle/a.py")}}, runner=runner
    )
    assert calls[0][0] == ["uv", "run", "pytest", "-q"]
    assert calls[0][1]["cwd"] == tmp_path.resolve()
    assert result["hookSpecificOutput"]["additionalContext"] == "uv run pytest -q passed."


def test_failed_tests_are_fed_back_to_agent(tmp_path):
    (tmp_path / "pyproject.toml").touch()

    def runner(*args, **kwargs):
        return SimpleNamespace(returncode=1, stdout="FAILED test_refunds", stderr="details")

    result = HOOK.handle_edit({"tool_input": {"file_path": str(tmp_path / "a.py")}}, runner)
    assert result["decision"] == "block"
    assert "FAILED test_refunds" in result["reason"]
    assert "details" in result["reason"]


def test_non_python_edit_does_not_run_tests():
    def runner(*args, **kwargs):
        pytest.fail("A documentation edit should not run the Python tests")

    assert HOOK.handle_edit({"tool_input": {"file_path": "README.md"}}, runner) is None


@pytest.mark.parametrize("error", [OSError("missing uv"), subprocess.TimeoutExpired("uv", 120)])
def test_hook_reports_unavailable_test_runner(tmp_path, error):
    (tmp_path / "pyproject.toml").touch()

    def runner(*args, **kwargs):
        raise error

    result = HOOK.handle_edit({"tool_input": {"file_path": str(tmp_path / "a.py")}}, runner)
    assert result["decision"] == "block"
    assert "Could not run tests" in result["reason"]
