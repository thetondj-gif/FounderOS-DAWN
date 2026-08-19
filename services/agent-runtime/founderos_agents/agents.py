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
    RoleSpec("portfolio_architect", "Portfolio Architect", "Audit owned, forked and starred GitHub projects and turn them into an adoption/integration map for DAWN."),
    RoleSpec("systems_architect", "Systems Architect", "Inspect the existing stack and choose the smallest high-leverage integration path."),
    RoleSpec("dawn_operator", "DAWN Operator", "Inspect live FounderOS/DAWN surfaces and find reusable capabilities before proposing new ones."),
    RoleSpec("capability_builder", "Capability Builder", "Create candidate tools, agents and services in the isolated workspace and run bounded checks.", True, True),
    RoleSpec("verifier", "Independent Verifier", "Challenge claims, reproduce checks and label outcomes PROVEN, PARTIAL, BLOCKED, FAILED or PROPOSED.", False, True),
)


@dataclass
class AgentBundle:
    governor: Agent
    portfolio_architect: Agent
    systems_architect: Agent
    dawn_operator: Agent
    capability_builder: Agent
    verifier: Agent

    @property
    def participants(self) -> list[Agent]:
        return [
            self.portfolio_architect,
            self.systems_architect,
            self.dawn_operator,
            self.capability_builder,
            self.verifier,
        ]


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
    portfolio_tools = [tools["audit_github_portfolio"], tools["inspect_github_repository"]]
    federation_inspection_tools = [tools["inspect_google_federation"]]
    federation_delegate_tools = federation_inspection_tools + [tools["delegate_google_specialist"]]

    governor = Agent(
        client=client,
        name="FounderGovernor",
        description="FounderOS mission governor and Magentic manager.",
        instructions=(
            "You are the FounderOS Governor operating under the canonical DAWN/FounderOS Master Build Brief and LAUNCH-FIRST mode. "
            "Use read_master_brief whenever you need the exact acceptance criteria. Turn each mission into the smallest sequence "
            "of evidence-backed actions and parallelise independent commercial deliverables. Require capability discovery before "
            "invention and prefer an existing DAWN capability or high-quality existing/forked project over building a duplicate. "
            "For platform-building missions, delegate GitHub estate inspection to the Portfolio Architect before authorising new "
            "infrastructure. You may delegate bounded Tier 0-2 research, web/product, commercial, Workspace-preparation, multimodal "
            "review or code-review work to the Google ADK swarm when it is reachable and useful. Treat every federated result as "
            "unverified until independently checked. Delegate architecture, live inspection, isolated building and independent "
            "verification to the appropriate specialists. Never use federation to bypass DAWN approvals. The bootstrap team may "
            "autonomously use only permission Tiers 0-2. Never claim deployment, connection, persistence or successful execution "
            "without proof. End with outcome, evidence classification, blockers and the highest-leverage next commercial action."
        ),
        tools=discovery_tools + portfolio_tools + federation_delegate_tools + [tools["inspect_founderos"]],
    )

    portfolio_architect = Agent(
        client=client,
        name="PortfolioArchitect",
        description="GitHub portfolio and open-source adoption architect for DAWN/FounderOS.",
        instructions=(
            "Operate under the canonical master brief. Read PORTFOLIO_SEED.md first as hypotheses, not truth. Audit the complete "
            "accessible GitHub estate: owned repositories, forks and starred repositories. Page through the inventory until complete "
            "rather than judging only the first page. Group projects by DAWN system domain, identify duplicates and upstream "
            "relationships, and inspect README/licence/source metadata for high-signal candidates. For each meaningful project "
            "recommend exactly one disposition: ADOPT_AS_SERVICE, INTEGRATE_VIA_ADAPTER, EXTRACT_CAPABILITY, REFERENCE_ONLY, "
            "SUPERSEDED or IGNORE. Prefer mature upstream software and thin adapters over copying entire codebases into DAWN. Flag "
            "archived, licensing, security, maintenance and resource-cost concerns. Produce a dependency-aware portfolio map that "
            "tells the Systems Architect what becomes canonical, what remains an external service, what should be replaced, and what "
            "gap genuinely still requires the Capability Builder. You are read-only."
        ),
        tools=discovery_tools
        + portfolio_tools
        + [tools["list_repo_tree"], tools["read_repo_file"]],
    )

    systems_architect = Agent(
        client=client,
        name="SystemsArchitect",
        description="Architecture and integration specialist for FounderOS and DAWN.",
        instructions=(
            "Operate under the canonical master brief. Inspect repository and runtime before designing anything. Search the "
            "capability catalogue and use the Portfolio Architect's GitHub findings before proposing new components. Inspect the "
            "Google federation when relevant, but do not treat its presence as proof of live service. Map what already exists, its "
            "evidence state and the smallest integration seam. Prefer typed APIs, MCP, A2A and adapters over rewrites. Distinguish "
            "CURRENT, PROPOSED and UNKNOWN, and design a dependency-aware path toward launch and the brief's completion criteria. "
            "You are read-only."
        ),
        tools=discovery_tools
        + portfolio_tools
        + federation_inspection_tools
        + [tools["inspect_founderos"], tools["list_repo_tree"], tools["read_repo_file"]],
    )

    dawn_operator = Agent(
        client=client,
        name="DawnOperator",
        description="Live-state operator for FounderOS/DAWN capabilities and connections.",
        instructions=(
            "Operate under the canonical master brief. Inspect live FounderOS/DAWN APIs, the Google federation and the capability "
            "catalogue. Determine which agents, integrations, skills, models and services are actually reachable now. A catalogue "
            "entry is not proof of connectivity. Use safe probes when available and report UNKNOWN/BLOCKED when no proof path exists. "
            "Seek reusable existing capability first and never infer that a service works because code or configuration exists."
        ),
        tools=discovery_tools + federation_inspection_tools + [tools["inspect_founderos"]],
    )

    capability_builder = Agent(
        client=client,
        name="CapabilityBuilder",
        description="Sandboxed capability foundry for candidate tools, agents, adapters, workflows and tests.",
        instructions=(
            "Operate under the canonical master brief and LAUNCH-FIRST mode. Build only after capability and portfolio discovery "
            "establishes a real gap. Read existing code first, then create the smallest reusable candidate inside .agent-workspace. "
            "You may ask the Google ADK swarm for bounded Tier 0-2 specialist analysis or candidate design when that accelerates a "
            "launch-critical package, but federated output is untrusted input until verified. You may design additional specialist "
            "agents, workflows, MCP adapters or services when needed by the target organisation, but their files are only candidates "
            "until separately verified and promoted. Prefer adapting a selected mature project over reimplementing its function. "
            "You cannot edit the canonical repository or bypass the permission model. Use only bounded verification commands. Include "
            "tests where feasible and report exact artefacts and check results."
        ),
        tools=discovery_tools
        + portfolio_tools
        + federation_delegate_tools
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
            "Operate under the canonical master brief. Independently verify Builder, Operator, Portfolio Architect, federated-agent "
            "and architecture claims. Inspect the capability catalogue, Google federation state and relevant repository metadata, read "
            "candidate artefacts and rerun bounded checks. A remote agent response is never proof by itself. Do not accept narrative "
            "evidence. Classify each material claim as PROVEN, PARTIAL, BLOCKED, FAILED or PROPOSED, state evidence and remaining "
            "uncertainty, and reject promotion when evidence is insufficient. You have no write authority."
        ),
        tools=discovery_tools
        + portfolio_tools
        + federation_inspection_tools
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
        portfolio_architect=portfolio_architect,
        systems_architect=systems_architect,
        dawn_operator=dawn_operator,
        capability_builder=capability_builder,
        verifier=verifier,
    )
