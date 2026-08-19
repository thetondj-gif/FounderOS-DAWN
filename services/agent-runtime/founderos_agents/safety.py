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

CHECK_NAMES = {"python_compile", "python_unittest_sandbox"}


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


def check_command(name: str, workspace_root: Path) -> list[str]:
    if name not in CHECK_NAMES:
        raise ValueError(f"unsupported check: {name}")
    if name == "python_compile":
        # compileall parses bytecode but does not import or execute candidate modules.
        return [sys.executable, "-m", "compileall", "-q", "."]

    workspace = str(workspace_root.resolve())
    # Candidate code executes only inside a constrained container. The workspace is
    # mounted read-only; /tmp is the only writable filesystem and networking is disabled.
    return [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--pids-limit",
        "128",
        "--memory",
        "512m",
        "--cpus",
        "1",
        "--read-only",
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,size=64m",
        "--user",
        "65534:65534",
        "-e",
        "PYTHONDONTWRITEBYTECODE=1",
        "-v",
        f"{workspace}:/workspace:ro",
        "-w",
        "/workspace",
        "python:3.12-slim",
        "python",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-v",
    ]
