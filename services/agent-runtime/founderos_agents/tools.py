from __future__ import annotations

import json
import subprocess
from typing import Any

import httpx
from agent_framework import tool

from .config import Settings
from .safety import check_command, safe_repo_path, workspace_path


IGNORED_DIRS = {".git", ".next", "node_modules", ".agent-workspace", "__pycache__", ".venv"}


def _json_text(value: Any) -> str:
    return json.dumps(value, indent=2, default=str)[:50_000]


def _get_json(settings: Settings, path: str) -> dict[str, Any]:
    url = f"{settings.founder_os_base_url}{path}"
    try:
        with httpx.Client(timeout=settings.request_timeout_seconds) as client:
            response = client.get(url)
        return {
            "url": url,
            "status_code": response.status_code,
            "ok": response.is_success,
            "data": response.json() if response.is_success else response.text[:2000],
        }
    except Exception as exc:  # network state is reported, never disguised
        return {"url": url, "status_code": None, "ok": False, "error": str(exc)}


def build_tools(settings: Settings) -> dict[str, Any]:
    @tool(approval_mode="never_require")
    def inspect_founderos() -> str:
        """Read current FounderOS/DAWN runtime surfaces without changing anything."""
        endpoints = ["/api/agents", "/api/connections", "/api/skills", "/api/metrics", "/api/brain"]
        return _json_text({path: _get_json(settings, path) for path in endpoints})

    @tool(approval_mode="never_require")
    def list_repo_tree(relative_path: str = ".", max_entries: int = 300) -> str:
        """List repository files below a safe relative path. Secret-like paths are excluded."""
        root = safe_repo_path(settings.repo_root, relative_path)
        if not root.exists():
            return f"NOT_FOUND: {relative_path}"
        if root.is_file():
            return relative_path
        entries: list[str] = []
        for path in sorted(root.rglob("*")):
            if any(part in IGNORED_DIRS for part in path.parts):
                continue
            rel = path.relative_to(settings.repo_root)
            try:
                safe_repo_path(settings.repo_root, str(rel))
            except ValueError:
                continue
            entries.append(f"{'DIR ' if path.is_dir() else 'FILE'} {rel}")
            if len(entries) >= max(1, min(max_entries, 1000)):
                entries.append("...TRUNCATED...")
                break
        return "\n".join(entries)

    @tool(approval_mode="never_require")
    def read_repo_file(relative_path: str) -> str:
        """Read a non-secret UTF-8 text file from the canonical repository."""
        path = safe_repo_path(settings.repo_root, relative_path)
        if not path.exists() or not path.is_file():
            return f"NOT_FOUND: {relative_path}"
        if path.stat().st_size > settings.max_file_bytes:
            return f"REFUSED: file exceeds {settings.max_file_bytes} bytes"
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return "REFUSED: binary/non-UTF8 file"

    @tool(approval_mode="never_require")
    def read_workspace_file(relative_path: str) -> str:
        """Read a UTF-8 file from the isolated agent build workspace."""
        path = workspace_path(settings.workspace_root, relative_path)
        if not path.exists() or not path.is_file():
            return f"NOT_FOUND: {relative_path}"
        if path.stat().st_size > settings.max_file_bytes:
            return f"REFUSED: file exceeds {settings.max_file_bytes} bytes"
        return path.read_text(encoding="utf-8")

    @tool(approval_mode="never_require")
    def write_workspace_file(relative_path: str, content: str) -> str:
        """Write candidate code only inside .agent-workspace. This cannot modify the canonical repo."""
        path = workspace_path(settings.workspace_root, relative_path)
        if len(content.encode("utf-8")) > settings.max_file_bytes:
            return f"REFUSED: content exceeds {settings.max_file_bytes} bytes"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"WROTE {path.relative_to(settings.workspace_root)} ({len(content.encode('utf-8'))} bytes)"

    @tool(approval_mode="never_require")
    def run_workspace_check(check: str) -> str:
        """Run python_compile on the host or python_unittest_sandbox in a locked-down Docker container."""
        settings.workspace_root.mkdir(parents=True, exist_ok=True)
        command = check_command(check, settings.workspace_root)
        try:
            completed = subprocess.run(
                command,
                cwd=settings.workspace_root,
                capture_output=True,
                text=True,
                timeout=180,
                shell=False,
                check=False,
            )
            output = (completed.stdout + "\n" + completed.stderr).strip()
            return _json_text(
                {
                    "check": check,
                    "command": command,
                    "exit_code": completed.returncode,
                    "ok": completed.returncode == 0,
                    "output": output[-20_000:],
                }
            )
        except Exception as exc:
            return _json_text({"check": check, "ok": False, "error": str(exc)})

    return {
        "inspect_founderos": inspect_founderos,
        "list_repo_tree": list_repo_tree,
        "read_repo_file": read_repo_file,
        "read_workspace_file": read_workspace_file,
        "write_workspace_file": write_workspace_file,
        "run_workspace_check": run_workspace_check,
    }
