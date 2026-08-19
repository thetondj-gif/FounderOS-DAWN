from __future__ import annotations

import sys
from pathlib import Path


DENIED_NAME_FRAGMENTS = (
    ".env",
    "credential",
    "credentials",
    "secret",
    "secrets",
    "private_key",
    "id_rsa",
    "id_ed25519",
)

CHECK_COMMANDS: dict[str, list[str]] = {
    "python_compile": [sys.executable, "-m", "compileall", "-q", "."],
    "pytest": [sys.executable, "-m", "pytest", "-q"],
    "npm_test": ["npm", "test"],
    "npm_typecheck": ["npm", "run", "typecheck"],
}


def resolve_inside(root: Path, relative_path: str) -> Path:
    candidate_input = Path(relative_path)
    if candidate_input.is_absolute():
        raise ValueError("absolute paths are not allowed")
    root = root.resolve()
    candidate = (root / candidate_input).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("path escapes allowed root")
    return candidate


def is_sensitive_path(path: Path) -> bool:
    lowered = "/".join(part.lower() for part in path.parts)
    return any(fragment in lowered for fragment in DENIED_NAME_FRAGMENTS)


def safe_repo_path(repo_root: Path, relative_path: str) -> Path:
    path = resolve_inside(repo_root, relative_path)
    if is_sensitive_path(Path(relative_path)):
        raise ValueError("sensitive paths are not readable by agents")
    return path


def workspace_path(workspace_root: Path, relative_path: str) -> Path:
    path = resolve_inside(workspace_root, relative_path)
    if is_sensitive_path(Path(relative_path)):
        raise ValueError("sensitive paths are not writable by agents")
    return path


def check_command(name: str) -> list[str]:
    try:
        return list(CHECK_COMMANDS[name])
    except KeyError as exc:
        raise ValueError(f"unsupported check: {name}") from exc
