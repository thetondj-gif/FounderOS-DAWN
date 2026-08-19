from __future__ import annotations

import json
import subprocess
from typing import Any

import httpx
from agent_framework import tool

from .brief import MASTER_BUILD_BRIEF
from .capabilities import capability_catalog, get_capability
from .config import Settings
from .portfolio import inspect_repository, portfolio_snapshot
from .safety import check_command, safe_repo_path, workspace_path


IGNORED_DIRS = {".git", ".next", "node_modules", ".agent-workspace", "__pycache__", ".venv"}


def _json_text(value: Any, max_chars: int = 50_000) -> str:
    return json.dumps(value, indent=2, default=str)[:max_chars]


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


def _probe_url(url: str, timeout: float) -> dict[str, Any]:
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url)
        return {
            "url": url,
            "ok": response.is_success,
            "status_code": response.status_code,
            "evidence": response.text[:1000],
        }
    except Exception as exc:
        return {"url": url, "ok": False, "status_code": None, "error": str(exc)}


def build_tools(settings: Settings) -> dict[str, Any]:
    @tool(approval_mode="never_require")
    def read_master_brief() -> str:
        """Return the canonical DAWN/FounderOS target architecture, build rules, permission model and acceptance criteria."""
        return MASTER_BUILD_BRIEF

    @tool(approval_mode="never_require")
    def discover_capabilities(query: str = "", max_results: int = 100) -> str:
        """Search the known DAWN/FounderOS capability catalogue before proposing or building a duplicate capability."""
        catalogue = capability_catalog(query or None, max_results=max_results)
        live_connections = _get_json(settings, "/api/connections")
        live_skills = _get_json(settings, "/api/skills")
        return _json_text(
            {
                "catalogue": catalogue,
                "catalogue_count": len(catalogue),
                "runtime_snapshots": {
                    "founderos_connections": live_connections,
                    "founderos_skills": live_skills,
                },
                "interpretation_rule": (
                    "Catalogue availability is metadata, not proof of live connectivity. "
                    "Use inspect_capability/probe_capability and existing runtime APIs before claiming a tool is connected."
                ),
            }
        )

    @tool(approval_mode="never_require")
    def inspect_capability(capability_id: str) -> str:
        """Read metadata, permission tier and integration status for one named registered capability."""
        item = get_capability(capability_id)
        if item is None:
            return _json_text({"found": False, "capability_id": capability_id})
        return _json_text({"found": True, "capability": item})

    @tool(approval_mode="never_require")
    def probe_capability(capability_id: str) -> str:
        """Probe only pre-registered safe health surfaces. Capabilities without a health adapter return UNKNOWN rather than guessed success."""
        item = get_capability(capability_id)
        if item is None:
            return _json_text({"found": False, "capability_id": capability_id})
        probe = item.get("health_probe")
        if probe == "founderos":
            evidence = _probe_url(f"{settings.founder_os_base_url}/api/agents", settings.request_timeout_seconds)
        elif probe == "ollama":
            evidence = _probe_url(f"{settings.ollama_host.rstrip('/')}/api/tags", settings.request_timeout_seconds)
        elif probe == "github-portfolio":
            try:
                snapshot = portfolio_snapshot(
                    settings.github_owner,
                    settings.github_token,
                    settings.request_timeout_seconds,
                    max_pages=1,
                )
                evidence = {
                    "ok": True,
                    "owner": snapshot["owner"],
                    "owned_scope": snapshot["owned_scope"],
                    "owned_count_first_page": snapshot["owned_count"],
                    "starred_count_first_page": snapshot["starred_count"],
                }
            except Exception as exc:
                evidence = {"ok": False, "error": str(exc)}
        else:
            return _json_text(
                {
                    "found": True,
                    "capability": item,
                    "classification": "UNKNOWN",
                    "reason": "No safe live health adapter is registered for this capability yet.",
                }
            )
        return _json_text(
            {
                "found": True,
                "capability": item,
                "classification": "PROVEN" if evidence.get("ok") else "BLOCKED",
                "evidence": evidence,
            }
        )

    @tool(approval_mode="never_require")
    def audit_github_portfolio(relation: str = "all", offset: int = 0, limit: int = 100) -> str:
        """Read owned repositories and public starred repositories from GitHub in deterministic pages for portfolio architecture analysis."""
        try:
            snapshot = portfolio_snapshot(
                settings.github_owner,
                settings.github_token,
                settings.request_timeout_seconds,
                max_pages=20,
            )
            relation_value = relation.strip().lower()
            if relation_value == "owned":
                items = snapshot["owned"]
            elif relation_value == "starred":
                items = snapshot["starred"]
            elif relation_value == "all":
                items = snapshot["owned"] + snapshot["starred"]
            else:
                return _json_text({"ok": False, "error": "relation must be all, owned or starred"})
            safe_offset = max(0, offset)
            safe_limit = max(1, min(limit, 100))
            page = items[safe_offset : safe_offset + safe_limit]
            next_offset = safe_offset + len(page)
            return _json_text(
                {
                    "ok": True,
                    "owner": snapshot["owner"],
                    "owned_scope": snapshot["owned_scope"],
                    "owned_count": snapshot["owned_count"],
                    "starred_count": snapshot["starred_count"],
                    "relation": relation_value,
                    "offset": safe_offset,
                    "returned": len(page),
                    "next_offset": next_offset if next_offset < len(items) else None,
                    "items": page,
                    "interpretation_rule": snapshot["interpretation_rule"],
                },
                max_chars=120_000,
            )
        except Exception as exc:
            return _json_text({"ok": False, "classification": "BLOCKED", "error": str(exc)})

    @tool(approval_mode="never_require")
    def inspect_github_repository(full_name: str) -> str:
        """Read one GitHub repository's metadata, licence and README for adoption/integration assessment. No mutation is possible."""
        try:
            return _json_text(
                {
                    "ok": True,
                    **inspect_repository(full_name, settings.github_token, settings.request_timeout_seconds),
                },
                max_chars=80_000,
            )
        except Exception as exc:
            return _json_text({"ok": False, "classification": "BLOCKED", "repository": full_name, "error": str(exc)})

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
        "read_master_brief": read_master_brief,
        "discover_capabilities": discover_capabilities,
        "inspect_capability": inspect_capability,
        "probe_capability": probe_capability,
        "audit_github_portfolio": audit_github_portfolio,
        "inspect_github_repository": inspect_github_repository,
        "inspect_founderos": inspect_founderos,
        "list_repo_tree": list_repo_tree,
        "read_repo_file": read_repo_file,
        "read_workspace_file": read_workspace_file,
        "write_workspace_file": write_workspace_file,
        "run_workspace_check": run_workspace_check,
    }
