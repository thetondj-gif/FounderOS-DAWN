from pathlib import Path

import pytest

from founderos_agents.safety import check_command, safe_repo_path, workspace_path


def test_repo_path_rejects_traversal(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="escapes"):
        safe_repo_path(tmp_path, "../outside.txt")


def test_repo_path_rejects_secret_like_files(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="sensitive"):
        safe_repo_path(tmp_path, ".env.local")


def test_workspace_path_stays_inside_workspace(tmp_path: Path) -> None:
    result = workspace_path(tmp_path, "candidate/tool.py")
    assert result == (tmp_path / "candidate/tool.py").resolve()


def test_command_runner_is_allowlist_only() -> None:
    assert check_command("python_compile")
    with pytest.raises(ValueError, match="unsupported"):
        check_command("rm_everything")
