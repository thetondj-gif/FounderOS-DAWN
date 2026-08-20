from __future__ import annotations

import os

import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from .agents import build_google_swarm


def create_app():
    host = os.environ.get("DAWN_GOOGLE_BIND_HOST", "127.0.0.1")
    port = int(os.environ.get("DAWN_GOOGLE_PORT", "4300"))
    return to_a2a(build_google_swarm(), host=host, port=port)


app = create_app()


def run() -> None:
    uvicorn.run(
        "dawn_google_agents.server:app",
        host=os.environ.get("DAWN_GOOGLE_BIND_HOST", "127.0.0.1"),
        port=int(os.environ.get("DAWN_GOOGLE_PORT", "4300")),
        reload=False,
    )


if __name__ == "__main__":
    run()
