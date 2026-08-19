from __future__ import annotations

import os

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from .agents import role_catalog
from .brief import MASTER_BUILD_BRIEF, bootstrap_task, launch_sprint_task, portfolio_audit_task
from .capabilities import capability_catalog, get_capability
from .config import Settings
from .federation import delegate_google_task, inspect_google_federation
from .portfolio import portfolio_snapshot
from .workflow import run_mission


app = FastAPI(title="FounderOS Agent Runtime", version="0.3.0")


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
        "version": "0.3.0",
        "mode": "LAUNCH-FIRST",
        "model": settings.ollama_model,
        "brief": "DAWN / FounderOS Master Build Brief",
        "capability_count": len(capability_catalog()),
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


@app.get("/brief")
def brief() -> dict[str, object]:
    return {
        "name": "DAWN / FounderOS Master Build Brief",
        "brief": MASTER_BUILD_BRIEF,
        "bootstrap_task": bootstrap_task(),
        "portfolio_audit_task": portfolio_audit_task(),
        "launch_sprint_task": launch_sprint_task(),
    }


@app.get("/capabilities")
def capabilities(
    q: str = Query(default="", max_length=200),
    limit: int = Query(default=100, ge=1, le=200),
) -> dict[str, object]:
    items = capability_catalog(q or None, max_results=limit)
    return {"query": q, "count": len(items), "capabilities": items}


@app.get("/capabilities/{capability_id}")
def capability(capability_id: str) -> dict[str, object]:
    item = get_capability(capability_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"unknown capability: {capability_id}")
    return {"capability": item}


@app.get("/portfolio")
def portfolio(max_pages: int = Query(default=10, ge=1, le=20)) -> dict[str, object]:
    settings = _settings()
    try:
        return portfolio_snapshot(
            settings.github_owner,
            settings.github_token,
            settings.request_timeout_seconds,
            max_pages=max_pages,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"portfolio read failed: {exc}") from exc


@app.get("/federation/google")
def google_federation_status() -> dict[str, object]:
    return inspect_google_federation(_settings().request_timeout_seconds)


@app.post("/federation/google/delegate")
async def google_federation_delegate(request: MissionRequest) -> dict[str, object]:
    try:
        return await delegate_google_task(request.task.strip())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"google federation delegation failed: {exc}") from exc


@app.post("/missions/run")
async def missions_run(request: MissionRequest) -> dict[str, object]:
    try:
        return await run_mission(request.task.strip(), _settings())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"mission execution failed: {exc}") from exc


@app.post("/missions/bootstrap")
async def missions_bootstrap() -> dict[str, object]:
    try:
        return await run_mission(bootstrap_task(), _settings())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"bootstrap mission execution failed: {exc}") from exc


@app.post("/missions/portfolio-audit")
async def missions_portfolio_audit() -> dict[str, object]:
    try:
        return await run_mission(portfolio_audit_task(), _settings())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"portfolio audit mission execution failed: {exc}") from exc


@app.post("/missions/launch-sprint")
async def missions_launch_sprint() -> dict[str, object]:
    try:
        return await run_mission(launch_sprint_task(), _settings())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"launch sprint mission execution failed: {exc}") from exc


def run() -> None:
    uvicorn.run(
        "founderos_agents.main:app",
        host=os.environ.get("FOUNDER_AGENT_BIND_HOST", "127.0.0.1"),
        port=int(os.environ.get("FOUNDER_AGENT_PORT", "4200")),
        reload=False,
    )


if __name__ == "__main__":
    run()
