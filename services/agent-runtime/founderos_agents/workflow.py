from __future__ import annotations

from typing import Any

from agent_framework.orchestrations import MagenticBuilder

from .agents import build_agents
from .config import Settings


def build_founder_workflow(settings: Settings):
    bundle = build_agents(settings)
    return MagenticBuilder(
        participants=bundle.participants,
        intermediate_output_from=bundle.participants,
        manager_agent=bundle.governor,
        max_round_count=12,
        max_stall_count=2,
        max_reset_count=1,
    ).build()


def _event_record(event: Any) -> dict[str, Any]:
    data = getattr(event, "data", None)
    return {
        "type": str(getattr(event, "type", "unknown")),
        "executor_id": getattr(event, "executor_id", None),
        "data": str(data)[:10_000] if data is not None else None,
    }


async def run_mission(task: str, settings: Settings) -> dict[str, Any]:
    # Workflows preserve state across calls, so every mission receives a fresh workflow.
    workflow = build_founder_workflow(settings)
    trace: list[dict[str, Any]] = []
    final_output: str | None = None

    async for event in workflow.run(task, stream=True):
        record = _event_record(event)
        if record["type"] in {"output", "magentic_orchestrator", "status", "error"}:
            trace.append(record)
        if record["type"] == "output" and record["data"]:
            # Participant outputs are configured as intermediate; the manager's terminal
            # output is emitted last, so this intentionally tracks the newest output.
            final_output = record["data"]

    return {
        "ok": final_output is not None,
        "task": task,
        "final": final_output,
        "trace": trace[-100:],
    }
