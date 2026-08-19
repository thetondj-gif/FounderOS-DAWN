from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    workspace_root: Path
    ollama_host: str
    ollama_model: str
    founder_os_base_url: str
    request_timeout_seconds: float
    max_file_bytes: int
    github_owner: str = "thetondj-gif"
    github_token: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        repo_root = Path(os.environ.get("FOUNDER_AGENT_REPO_ROOT", _repo_root())).expanduser().resolve()
        workspace_root = Path(
            os.environ.get("FOUNDER_AGENT_WORKSPACE_ROOT", repo_root / ".agent-workspace")
        ).expanduser().resolve()
        return cls(
            repo_root=repo_root,
            workspace_root=workspace_root,
            ollama_host=os.environ.get("FOUNDER_AGENT_OLLAMA_HOST", "http://127.0.0.1:11434"),
            ollama_model=os.environ.get("FOUNDER_AGENT_OLLAMA_MODEL", "qwen3.5:9b"),
            founder_os_base_url=os.environ.get("FOUNDER_OS_BASE_URL", "http://127.0.0.1:4100").rstrip("/"),
            request_timeout_seconds=float(os.environ.get("FOUNDER_AGENT_HTTP_TIMEOUT", "5")),
            max_file_bytes=int(os.environ.get("FOUNDER_AGENT_MAX_FILE_BYTES", "200000")),
            github_owner=os.environ.get("FOUNDER_AGENT_GITHUB_OWNER", "thetondj-gif"),
            github_token=os.environ.get("FOUNDER_AGENT_GITHUB_TOKEN") or None,
        )
