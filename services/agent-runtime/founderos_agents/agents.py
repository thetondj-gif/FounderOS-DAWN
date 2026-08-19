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
    RoleSpec("capability_builder", "Capability Builder", "Create candidate tools, agents and services in the isolated workspace and run bounded checks.", True, True),
    RoleSpec("verifier", "Independent Verifier", "Challenge claims, reproduce checks and label outcomes PROVEN, PARTIAL, BLOCKED, FAILED or PROPOSED.", False, True),
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

    discovery_tools = [
        tools["read_master_brief"],
        tools["discover_capabilities"],
        tools["inspect_capability"],
        tools["probe_capability"],
    ]

    governor = Agent(
        client=client,
        name="FounderGovernor",
        description="FounderOS mission governor and Magentic manager.",
        instructions=(
            "You are the FounderOS Governor operating under the canonical DAWN/FounderOS Master Build Brief. "
            "Use read_master_brief whenever you need the exact acceptance criteria. Turn each mission into the smallest sequence "
            "of evidence-backed actions. Require capability discovery before invention and prefer an existing DAWN capability over "
            "building a duplicate. Delegate architecture, live inspection, isolated building and independent verification to the "
            "appropriate specialists. The bootstrap team may autonomously use only permission Tiers 0-2. Never claim deployment, "
            "connection, persistence or successful execution without proof. End with outcome, evidence classification, blockers and "
            "the single highest-leverage next action."
        ),
        tools=discovery_tools + [tools["inspect_founderos"]],
    )

    systems_architect = Agent(
        client=client,
        name="SystemsArchitect",
        description="Architecture and integration specialist for FounderOS and DAWN.",
        instructions=(
            "Operate under the canonical master brief. Inspect repository and runtime before designing anything. Search the "
            "capability catalogue before proposing new components. Map what already exists, its evidence state and the smallest "
            "integration seam. Prefer typed APIs, MCP, A2A and adapters over rewrites. Distinguish CURRENT, PROPOSED and UNKNOWN, "
            "and design a dependency-aware path toward the brief's completion criteria. You are read-only."
        ),
        tools=discovery_tools + [tools["inspect_founderos"], tools["list_repo_tree"], tools["read_repo_file"]],
    )

    dawn_operator = Agent(
        client=client,
        name="DawnOperator",
        description="Live-state operator for FounderOS/DAWN capabilities and connections.",
        instructions=(
            "Operate under the canonical master brief. Inspect live FounderOS/DAWN APIs and the capability catalogue. Determine "
            "which agents, integrations, skills, models and services are actually reachable now. A catalogue entry is not proof of "
            "connectivity. Use safe probes when available and report UNKNOWN/BLOCKED when no proof path exists. Seek reusable "
            "existing capability first and never infer that a service works because code or configuration exists."
        ),
        tools=discovery_tools + [tools["inspect_founderos"]],
    )

    capability_builder = Agent(
        client=client,
        name="CapabilityBuilder",
        description="Sandboxed capability foundry for candidate tools, agents, adapters, workflows and tests.",
        instructions=(
            "Operate under the canonical master brief. Build only after capability discovery establishes a real gap. Read existing "
            "code first, then create the smallest reusable candidate inside .agent-workspace. You may design additional specialist "
            "agents, workflows, MCP adapters or services when needed by the target organisation, but their files are only candidates "
            "until separately verified and promoted. You cannot edit the canonical repository or bypass the permission model. Use "
            "only bounded verification commands. Include tests where feasible and report exact artefacts and check results."
        ),
        tools=discovery_tools
        + [
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
        description="Independent proof, challenge and failure-analysis agent.",
        instructions=(
            "Operate under the canonical master brief. Independently verify Builder, Operator and architecture claims. Inspect the "
            "capability catalogue, read candidate artefacts and rerun relevant bounded checks. Do not accept narrative evidence. "
            "Classify each material claim as PROVEN, PARTIAL, BLOCKED, FAILED or PROPOSED, state evidence and remaining uncertainty, "
            "and reject promotion when evidence is insufficient. You have no write authority."
        ),
        tools=discovery_tools
        + [
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
