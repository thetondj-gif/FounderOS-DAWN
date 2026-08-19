from __future__ import annotations

import os

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .agents import role_catalog
from .config import Settings
from .workflow import run_mission


app = FastAPI(title="FounderOS Agent Runtime", version="0.1.0")


class MissionRequest(BaseModel):
    task: str = Field(min_length=5, max_length=20_000)


def _settings() -> Settings:
    return Settings.from_env()


def _probe(url: str, timeout: float) -> dict[str, object]:
    try:
        response = httpx.get(url, timeout=timeout)
        return {"ok": response.is_success, "status_code": response.status_code, "url": url}
    except Exception as exc:
        return {"ok": False, "status_code": None, "url": url, "error": str(exc)}


@app.get("/healthz")
def healthz() -> dict[str, object]:
    settings = _settings()
    return {
        "ok": True,
        "service": "founderos-agent-runtime",
        "framework": "microsoft-agent-framework",
        "model": settings.ollama_model,
        "agents": role_catalog(),
    }


@app.get("/readyz")
def readyz() -> dict[str, object]:
    settings = _settings()
    ollama = _probe(f"{settings.ollama_host.rstrip('/')}/api/tags", settings.request_timeout_seconds)
    founder_os = _probe(f"{settings.founder_os_base_url}/api/agents", settings.request_timeout_seconds)
    return {"ok": bool(ollama["ok"] and founder_os["ok"]), "ollama": ollama, "founder_os": founder_os}


@app.get("/agents")
def agents() -> dict[str, object]:
    return {"agents": role_catalog()}


@app.post("/missions/run")
async def missions_run(request: MissionRequest) -> dict[str, object]:
    try:
        return await run_mission(request.task.strip(), _settings())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"mission execution failed: {exc}") from exc


def run() -> None:
    uvicorn.run(
        "founderos_agents.main:app",
        host=os.environ.get("FOUNDER_AGENT_BIND_HOST", "127.0.0.1"),
        port=int(os.environ.get("FOUNDER_AGENT_PORT", "4200")),
        reload=False,
    )


if __name__ == "__main__":
    run()
