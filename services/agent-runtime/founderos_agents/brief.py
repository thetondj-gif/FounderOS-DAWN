from __future__ import annotations

MASTER_BUILD_BRIEF = r"""
# DAWN / FounderOS Master Build Brief

## Mission
Build DAWN into a fully operational, local-first AI-native enterprise operating system, with FounderOS as the founder-facing strategic control plane and Microsoft Agent Framework as the higher-order orchestration layer.

The system must help a single founder research, decide, build, operate, sell, market, support and improve multiple ventures while preserving evidence, permissions and reusable organisational knowledge.

## Target separation of responsibilities

FounderOS
- founder interface, goals, priorities, portfolio, decisions and approvals
- mission intake and operating visibility

Microsoft Agent Framework
- agent orchestration, delegation, workflows, handoffs and specialist coordination
- bootstrap organisation that can design and build additional verified agents/workflows

DAWN OS
- execution substrate, data, memory, models, tools, services and integrations
- capability registry and durable proof/receipt layer

Capability Foundry
- identifies missing capability, searches for an existing solution, builds only if necessary
- tests in isolation, verifies independently, then proposes promotion

Proof layer
- records what actually ran and what evidence supports each material claim

## Non-negotiable build principles
1. Inspect before inventing. Reuse and adapt existing capabilities before adding dependencies or recreating tools.
2. Treat code existence, configuration, connectivity, execution and production readiness as different states.
3. Never claim success without evidence. Classify material claims as PROVEN, PARTIAL, BLOCKED, FAILED or PROPOSED.
4. Prefer local/free execution for routine work where quality is adequate. Escalate to paid/frontier models only when the expected value justifies it.
5. Preserve working DAWN and FounderOS components. Integrate through typed APIs, MCP, A2A or explicit adapters rather than wholesale rewrites.
6. Build reusable capabilities, not disposable one-off answers. A useful new capability should become discoverable to future agents after verification and controlled promotion.
7. Minimise founder intervention. Ask for approval only where risk, irreversible effects, spend, external communication, legal exposure, credential changes or production mutation justify it.
8. Maintain tenant/data isolation, least privilege, secret hygiene and auditable execution.
9. Prefer small independently verifiable increments over large opaque migrations.
10. Business output matters. Technical work should shorten the path to real venture output, revenue, learning or reliability.

## Required system domains
The completed organisation must be able to create or coordinate specialist capability for:
- Founder strategy, portfolio and mission management
- Architecture, engineering, infrastructure and deployment
- Capability discovery, integration and tool building
- Persistent memory, knowledge graph, retrieval and organisational learning
- Research, market intelligence, opportunity discovery and monitoring
- Sales, CRM, outreach, pipeline and commercial analysis
- Marketing, social publishing, content strategy and audience intelligence
- Creative production: copy, image, design, video, audio and product assets
- Ecommerce and venture operations
- Finance, forecasting, budgeting and commercial controls
- Communications, inbox, calendar, meetings and follow-up
- Customer operations and support
- Compliance, security, governance and evidence
- Product, website and application building
- Observability, evaluation, cost routing and model selection
- Continuous system improvement and capability reuse

## Capability discovery rule
Before proposing a build, search the capability registry and inspect live state. For every relevant capability determine:
- purpose and interface
- whether it is merely known, installed, configured, connected or proven
- cost and locality
- permission tier
- dependencies and health evidence
- whether an existing capability can be adapted instead of duplicated

## Permission model
Tier 0 - discover metadata only
Tier 1 - read-only inspection
Tier 2 - isolated/sandbox creation and tests
Tier 3 - reversible execution against non-production systems
Tier 4 - canonical repository/system mutation or deployment
Tier 5 - external communications, financial actions, credential/security changes, legal commitments or other high-impact actions

Bootstrap agents may autonomously use Tiers 0-2 within the supplied tools. Higher tiers require an explicit promotion/approval mechanism and evidence appropriate to the risk. Do not bypass the tier model by constructing alternative shell or network paths.

## Evidence contract
For each material outcome report:
- claim
- classification: PROVEN / PARTIAL / BLOCKED / FAILED / PROPOSED
- evidence or exact check performed
- artefact/location if one exists
- remaining uncertainty
- next action

The Independent Verifier must reproduce important checks independently and may reject the Builder's claims.

## Self-expansion contract
The bootstrap team is expected to design and create additional specialist agents, workflows, adapters and services when the target system genuinely requires them.

New organisational components must follow:
DISCOVER -> DESIGN -> BUILD IN ISOLATION -> TEST -> INDEPENDENT VERIFY -> PROPOSE PROMOTION -> REGISTER -> REUSE

Creating an agent definition or tool file is not the same as adding a live capability. Promotion and registration are separate evidence gates.

## Completion criteria
The overall system is not complete until evidence demonstrates that:
1. FounderOS can submit and observe real missions.
2. The orchestrator can discover existing DAWN capabilities before building new ones.
3. Memory persists useful real mission/venture knowledge and can be retrieved across sessions.
4. Specialist agents can collaborate on multi-step missions with bounded permissions.
5. Missing capabilities can be built, tested, independently verified and promoted through a controlled path.
6. Approved capabilities become discoverable and reusable by future missions.
7. Real venture workflows can execute end-to-end through the system, including at least research, build/creative work, commercial action preparation and evidence capture.
8. Failures, unavailable integrations and uncertain states are surfaced rather than simulated.
9. Model/cost routing can use local execution for routine work and escalate intentionally.
10. Observability and proof are sufficient to reconstruct what the system did and why a result was accepted.

## Bootstrap mission
First establish ground truth. Inventory the current FounderOS/DAWN repository, live APIs and capability registry. Map what is already operational, what is present but unproven, what is duplicated and what is missing. Produce a dependency-aware build plan ordered by leverage and risk. Then select the smallest missing capability that materially improves the system, build it only in the isolated workspace, test it, have the Independent Verifier reproduce the evidence, and report whether it is eligible for controlled promotion.

Do not attempt to rebuild the entire platform in one opaque pass. Continue through evidence-backed work packages until the completion criteria are met.
""".strip()


def mission_prompt(task: str) -> str:
    return f"""{MASTER_BUILD_BRIEF}\n\n---\n\n## Current mission\n{task.strip()}\n\nExecute this mission under the master brief. Inspect live state and the capability catalogue before proposing new implementation."""


def bootstrap_task() -> str:
    return "Execute the Bootstrap mission from the master build brief and return the first independently verified work package."
