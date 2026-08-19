from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent_framework import Agent
from agent_framework.ollama import OllamaChatClient

from .config import Settings
from .tools import build_tools


@dataclass(frozen=True)
class RoleSpec:
    id: str
    name: str
    purpose: str
    can_write_workspace: bool = False
    can_run_checks: bool = False


ROLE_SPECS = (
    RoleSpec("governor", "Founder Governor", "Own the mission, delegate work, enforce evidence and decide what happens next."),
    RoleSpec("systems_architect", "Systems Architect", "Inspect the existing stack and choose the smallest high-leverage integration path."),
    RoleSpec("dawn_operator", "DAWN Operator", "Inspect live FounderOS/DAWN surfaces and find reusable capabilities before proposing new ones."),
    RoleSpec("capability_builder", "Capability Builder", "Create candidate tools and services in the isolated workspace and run bounded checks.", True, True),
    RoleSpec("verifier", "Independent Verifier", "Challenge claims, reproduce checks and label outcomes PROVEN, INFERRED, BLOCKED or FAILED.", False, True),
)


@dataclass
class AgentBundle:
    governor: Agent
    systems_architect: Agent
    dawn_operator: Agent
    capability_builder: Agent
    verifier: Agent

    @property
    def participants(self) -> list[Agent]:
        return [self.systems_architect, self.dawn_operator, self.capability_builder, self.verifier]


def role_catalog() -> list[dict[str, Any]]:
    return [
        {
            "id": role.id,
            "name": role.name,
            "purpose": role.purpose,
            "can_write_workspace": role.can_write_workspace,
            "can_run_checks": role.can_run_checks,
        }
        for role in ROLE_SPECS
    ]


def build_agents(settings: Settings) -> AgentBundle:
    client = OllamaChatClient(host=settings.ollama_host, model=settings.ollama_model)
    tools = build_tools(settings)

    governor = Agent(
        client=client,
        name="FounderGovernor",
        description="FounderOS mission governor and Magentic manager.",
        instructions=(
            "You are the FounderOS Governor. Turn the mission into the smallest sequence of evidence-backed actions. "
            "Delegate inspection before invention. Prefer an existing DAWN capability over building a duplicate. "
            "A build is not complete because code was written: require independent verification and concrete evidence. "
            "Never claim deployment, connection, persistence, or successful execution without proof. "
            "The Capability Builder may only create candidates in the isolated workspace. Canonical repo mutation, secrets, "
            "production deployment and unrestricted shell execution are outside this nucleus. End with: outcome, evidence, "
            "remaining blockers, and the single highest-leverage next action."
        ),
        tools=[tools["inspect_founderos"]],
    )

    systems_architect = Agent(
        client=client,
        name="SystemsArchitect",
        description="Architecture and integration specialist for FounderOS and DAWN.",
        instructions=(
            "Inspect the repository and current runtime before designing anything. Map what already exists, identify the real "
            "integration seam, and recommend minimal changes that preserve working systems. Distinguish CURRENT, PROPOSED and "
            "UNKNOWN. You are read-only and must not ask the Builder to recreate capabilities already present."
        ),
        tools=[tools["inspect_founderos"], tools["list_repo_tree"], tools["read_repo_file"]],
    )

    dawn_operator = Agent(
        client=client,
        name="DawnOperator",
        description="Live-state operator for FounderOS/DAWN capabilities and connections.",
        instructions=(
            "Inspect live FounderOS/DAWN API surfaces. Determine which agents, integrations, skills and metrics are actually "
            "reachable now. Report connection failures honestly. Seek a reusable existing capability first. Do not infer that a "
            "service is working merely because code or configuration exists."
        ),
        tools=[tools["inspect_founderos"]],
    )

    capability_builder = Agent(
        client=client,
        name="CapabilityBuilder",
        description="Sandboxed capability foundry for candidate tools, adapters and tests.",
        instructions=(
            "Build only when the Governor has a concrete gap to close. Read existing code first, then create the smallest candidate "
            "implementation inside the isolated .agent-workspace. You cannot edit the canonical repository. Use only the bounded "
            "verification commands provided. Include tests where feasible. Report exact files created and check results; never "
            "describe an unexecuted candidate as implemented in DAWN."
        ),
        tools=[
            tools["inspect_founderos"],
            tools["list_repo_tree"],
            tools["read_repo_file"],
            tools["read_workspace_file"],
            tools["write_workspace_file"],
            tools["run_workspace_check"],
        ],
    )

    verifier = Agent(
        client=client,
        name="IndependentVerifier",
        description="Independent proof and failure-analysis agent.",
        instructions=(
            "Independently verify the Builder and Operator claims. Read the candidate files and rerun relevant bounded checks. "
            "Do not accept narrative evidence. Classify each material claim as PROVEN, INFERRED, BLOCKED or FAILED and state the "
            "evidence. You are read-only except for running the provided checks."
        ),
        tools=[
            tools["inspect_founderos"],
            tools["list_repo_tree"],
            tools["read_repo_file"],
            tools["read_workspace_file"],
            tools["run_workspace_check"],
        ],
    )

    return AgentBundle(
        governor=governor,
        systems_architect=systems_architect,
        dawn_operator=dawn_operator,
        capability_builder=capability_builder,
        verifier=verifier,
    )
