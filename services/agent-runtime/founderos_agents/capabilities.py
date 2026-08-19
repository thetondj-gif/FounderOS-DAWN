from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class CapabilitySpec:
    id: str
    name: str
    category: str
    purpose: str
    interface: str
    permission_tier: int
    cost: str
    locality: str
    availability: str
    source: str
    health_probe: str | None = None
    notes: str = ""


CAPABILITIES: tuple[CapabilitySpec, ...] = (
    CapabilitySpec("founderos-api", "FounderOS API", "control-plane", "Inspect agents, connections, skills, metrics, brain and operating state.", "HTTP API", 1, "local", "local", "available", "FounderOS-DAWN", "founderos"),
    CapabilitySpec("microsoft-agent-framework", "Microsoft Agent Framework", "orchestration", "Coordinate agents, workflows, handoffs and Magentic orchestration.", "Python SDK", 2, "open-source", "local", "available", "microsoft/agent-framework"),
    CapabilitySpec("github", "GitHub", "engineering", "Repository, branch, pull request, issue and CI workflow operations.", "GitHub API / git", 4, "free/variable", "remote", "requires-adapter", "connected account", notes="Read access can be lower tier; canonical writes and merges are Tier 4."),
    CapabilitySpec("github-portfolio", "GitHub Portfolio Reader", "engineering", "Inventory owned/forked repositories and public stars, then inspect repository metadata, licence and README for DAWN adoption decisions.", "Read-only GitHub REST API", 1, "free/API-rate-limited", "remote", "available", "agent-runtime", "github-portfolio", notes="Without FOUNDER_AGENT_GITHUB_TOKEN, owned inventory is public-only. A read-scoped token enables private owned repositories; this adapter never mutates GitHub."),
    CapabilitySpec("ollama", "Ollama", "models", "Run local language and embedding models for routine agent work.", "HTTP API", 1, "local/free", "local", "available", "local runtime", "ollama"),
    CapabilitySpec("mlx", "MLX", "models", "Apple Silicon local model execution and optimisation.", "Python/CLI", 2, "open-source", "local", "known", "local/repository"),
    CapabilitySpec("openai", "OpenAI", "models", "Escalate high-value reasoning, generation and agent tasks to frontier models when justified.", "API", 3, "usage-based", "remote", "requires-adapter", "provider"),
    CapabilitySpec("hermes", "Hermes", "agents", "Existing local agent/gateway runtime and skill ecosystem.", "HTTP/CLI", 1, "local", "local", "known", "local service"),
    CapabilitySpec("n8n", "n8n", "automation", "Event-driven and scheduled workflow automation across services.", "HTTP/API/workflows", 3, "self-hosted", "local", "known", "local service"),
    CapabilitySpec("composio", "Composio", "integration", "Tool and SaaS integration layer for connected external services.", "API/MCP", 3, "variable", "remote", "requires-adapter", "external service"),
    CapabilitySpec("gmail", "Gmail", "communications", "Read, triage, draft and send business email.", "Connector/API", 5, "provider", "remote", "requires-adapter", "external service", notes="Read operations can be Tier 1; sending is Tier 5."),
    CapabilitySpec("google-calendar", "Google Calendar", "communications", "Read availability, prepare meetings and schedule events.", "Connector/API", 5, "provider", "remote", "requires-adapter", "external service", notes="Read is lower risk; event creation/modification is high-impact."),
    CapabilitySpec("google-drive", "Google Drive / Docs / Sheets / Slides", "knowledge", "Search, read and create venture documents and structured operating artefacts.", "Connector/API", 4, "provider", "remote", "requires-adapter", "external service"),
    CapabilitySpec("postiz", "Postiz", "marketing", "Schedule and publish social content across channels.", "HTTP/API", 5, "self-hosted", "local/remote", "known", "local service"),
    CapabilitySpec("firecrawl", "Firecrawl", "research", "Crawl and extract web content for research and intelligence workflows.", "HTTP API", 1, "self-hosted", "local", "known", "local service"),
    CapabilitySpec("playwright", "Playwright", "browser", "Browser automation, UI verification and web interaction.", "Browser/CLI", 3, "open-source", "local", "known", "local service"),
    CapabilitySpec("qdrant", "Qdrant", "memory", "Vector storage and semantic retrieval for DAWN knowledge and memory.", "HTTP/gRPC", 2, "self-hosted", "local", "known", "local service"),
    CapabilitySpec("graphiti", "Graphiti", "memory", "Temporal knowledge graph and entity relationship memory.", "Python/API", 2, "open-source", "local", "known", "repository/local service"),
    CapabilitySpec("obsidian", "Obsidian", "knowledge", "Human-readable local knowledge vault and operating documentation.", "Filesystem/REST adapter", 2, "local", "local", "known", "local vault"),
    CapabilitySpec("langfuse", "Langfuse", "observability", "Trace model/agent calls, evaluate behaviour and measure cost/quality.", "HTTP/API", 2, "self-hosted", "local", "known", "local service"),
    CapabilitySpec("comfyui", "ComfyUI", "creative", "Local image generation and creative workflows.", "HTTP/workflow API", 3, "local/free", "local", "known", "local service"),
    CapabilitySpec("voicebox", "Voicebox", "creative", "Local voice/audio generation and processing.", "HTTP/CLI", 3, "local", "local", "known", "local service"),
    CapabilitySpec("video-stack", "Video Production Stack", "creative", "Generate, edit and assemble short-form/product video assets using available local and API tools.", "Adapters/workflows", 3, "mixed", "mixed", "requires-adapter", "multiple repositories/services"),
    CapabilitySpec("image-stack", "Image / Design Stack", "creative", "Generate, edit and prepare product, campaign and social imagery.", "Adapters/workflows", 3, "mixed", "mixed", "requires-adapter", "multiple repositories/services"),
    CapabilitySpec("mcp", "MCP Tool Fabric", "integration", "Expose reusable capabilities to agents through standard MCP servers.", "MCP", 3, "mixed", "mixed", "known", "DAWN/tool ecosystem"),
    CapabilitySpec("skills", "Skill Library", "agents", "Reusable operating instructions and domain workflows for agents.", "SKILL.md/files", 1, "local", "local", "known", "repositories/local skills"),
    CapabilitySpec("scripts", "Local Scripts", "engineering", "Existing deterministic automations, migrations, health checks and utilities.", "CLI/files", 2, "local", "local", "known", "repositories"),
    CapabilitySpec("datasets", "DAWN Datasets", "knowledge", "Structured venture, market, operating and research data available to workflows.", "Files/DB/API", 1, "mixed", "mixed", "known", "DAWN data stores"),
    CapabilitySpec("postgres", "PostgreSQL", "data", "Canonical relational state, receipts, missions and operational records.", "SQL", 2, "self-hosted", "local", "known", "local service"),
    CapabilitySpec("research-intel", "DAWN Research Intelligence", "research", "Contracts, companies, market, planning and opportunity research built from existing sources.", "DAWN services/workflows", 1, "mixed", "mixed", "known", "DAWN"),
    CapabilitySpec("capability-foundry", "Capability Foundry", "engineering", "Discover gaps, build candidate adapters/tools in isolation, test and propose promotion.", "Agent workflow", 2, "local", "local", "available", "agent-runtime"),
    CapabilitySpec("proof-ledger", "Proof / Receipt Ledger", "governance", "Record evidence-backed execution and gate completion on receipts.", "DAWN data/API", 2, "local", "local", "known", "DAWN"),
)


_INDEX = {item.id: item for item in CAPABILITIES}


def capability_catalog(query: str | None = None, max_results: int = 100) -> list[dict[str, object]]:
    items: Iterable[CapabilitySpec] = CAPABILITIES
    if query:
        terms = [part.lower() for part in query.split() if part.strip()]
        items = (
            item
            for item in items
            if all(
                term in " ".join((item.id, item.name, item.category, item.purpose, item.interface, item.source)).lower()
                for term in terms
            )
        )
    return [asdict(item) for item in list(items)[: max(1, min(max_results, 200))]]


def get_capability(capability_id: str) -> dict[str, object] | None:
    item = _INDEX.get(capability_id.strip().lower())
    return asdict(item) if item else None
