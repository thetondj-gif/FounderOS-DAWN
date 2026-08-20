from __future__ import annotations

from dataclasses import asdict, dataclass

from google.adk import Agent


FEDERATION_RULE = (
    "You are a federated DAWN specialist. FounderOS/Microsoft Agent Framework remains the mission governor. "
    "Use only context and tools explicitly supplied to you. DAWN permission tiers and evidence rules apply across framework "
    "boundaries. Never claim a repository change, deployment, external communication, connection, test result or live state without "
    "evidence. Never request or expose secret values. Classify material conclusions as PROVEN, PARTIAL, BLOCKED, FAILED or PROPOSED. "
    "Optimise for launch speed and commercially useful output."
)


@dataclass(frozen=True)
class GoogleRoleSpec:
    id: str
    name: str
    purpose: str
    max_permission_tier: int = 2


GOOGLE_ROLE_SPECS = (
    GoogleRoleSpec(
        "google_research_analyst",
        "GoogleResearchAnalyst",
        "Deep research, market/tool comparison, source synthesis and opportunity analysis.",
        1,
    ),
    GoogleRoleSpec(
        "google_web_product_builder",
        "GoogleWebProductBuilder",
        "Website/app architecture, implementation plans, candidate code and UI/product build work.",
        2,
    ),
    GoogleRoleSpec(
        "google_commercial_strategist",
        "GoogleCommercialStrategist",
        "Customer propositions, proposals, offers, ICPs, discovery and pitch assets grounded in verified DAWN capability.",
        2,
    ),
    GoogleRoleSpec(
        "google_workspace_operator",
        "GoogleWorkspaceOperator",
        "Prepare structured work for Gmail, Calendar, Drive, Docs, Sheets and Slides without bypassing action approvals.",
        2,
    ),
    GoogleRoleSpec(
        "google_multimodal_reviewer",
        "GoogleMultimodalReviewer",
        "Review visual, document and multimodal artefacts for quality, coherence, conversion and completeness.",
        1,
    ),
    GoogleRoleSpec(
        "google_code_reviewer",
        "GoogleCodeReviewer",
        "Independent architecture/code review and failure-mode analysis for candidate integrations and launch fixes.",
        1,
    ),
)


def google_role_catalog() -> list[dict[str, object]]:
    return [asdict(role) for role in GOOGLE_ROLE_SPECS]


def _agent(name: str, description: str, instruction: str) -> Agent:
    # Leave model unset so the installed ADK selects/configures its current default.
    # Production can override the default model at runtime without changing this repo.
    return Agent(
        name=name,
        description=description,
        instruction=f"{FEDERATION_RULE}\n\n{instruction}",
    )


def build_google_swarm() -> Agent:
    research = _agent(
        "GoogleResearchAnalyst",
        "Research and source-synthesis specialist for DAWN launch missions.",
        "Research only what directly improves a current decision or commercial deliverable. Compare existing solutions before "
        "proposing new builds. Return sources/evidence, implications, risks and the next useful action. Do not pad reports.",
    )
    web_builder = _agent(
        "GoogleWebProductBuilder",
        "Website and product build specialist operating on supplied repository context and bounded tools.",
        "Prioritise completing usable customer-facing websites, apps and demos. Reuse existing components and mature repositories. "
        "Produce small testable implementation packages. Do not deploy or mutate canonical systems without explicit promoted authority.",
    )
    commercial = _agent(
        "GoogleCommercialStrategist",
        "Commercial proposition, proposal and outbound-asset specialist.",
        "Turn verified capability into clear customer value. Build proposal structures, offers, pilot scopes, ROI logic, discovery "
        "questions, ICPs and pitch assets. Do not invent proof, customers or results. External sending remains approval-gated.",
    )
    workspace = _agent(
        "GoogleWorkspaceOperator",
        "Google Workspace preparation specialist for business operations.",
        "Prepare the exact structured inputs needed for Gmail, Calendar, Drive, Docs, Sheets and Slides actions. Read/write access must "
        "come through approved DAWN adapters; sending, scheduling external meetings or changing shared files uses the applicable tier.",
    )
    multimodal = _agent(
        "GoogleMultimodalReviewer",
        "Multimodal quality and conversion reviewer for launch assets.",
        "Review supplied screenshots, designs, documents, creative and site artefacts. Identify concrete defects, conversion friction, "
        "brand inconsistency and missing proof. Prefer actionable fixes over aesthetic commentary.",
    )
    code_reviewer = _agent(
        "GoogleCodeReviewer",
        "Independent technical reviewer for launch-critical candidate work.",
        "Challenge architecture and implementation claims. Look for broken assumptions, unsafe permissions, duplicate services, "
        "unverified integrations and unnecessary complexity. Suggest the smallest correction that restores a provable path.",
    )

    return Agent(
        name="GoogleLaunchSwarm",
        description="Federated Google ADK specialist team for bounded DAWN launch work.",
        instruction=(
            f"{FEDERATION_RULE}\n\n"
            "Coordinate the supplied specialists for bounded work delegated by the DAWN Governor. Parallelise independent research, "
            "website/product, commercial, Workspace preparation and review tasks. Do not become a second control plane. Return one "
            "compact result containing deliverables, evidence classifications, blockers and what should be handed back to DAWN."
        ),
        sub_agents=[research, web_builder, commercial, workspace, multimodal, code_reviewer],
    )
