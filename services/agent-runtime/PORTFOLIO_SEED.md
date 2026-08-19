# DAWN GitHub Portfolio — Seed Hypotheses

This file is **not** the final portfolio audit. It captures high-signal hypotheses from the founder's currently known estate so the Portfolio Architect does not begin from zero. Every entry must be re-checked against live GitHub metadata, README/source, licence, current DAWN state and overlap before promotion.

## Evaluation rule

Do not merge repositories simply because they are useful. Prefer one canonical responsibility per component and use narrow adapters/MCP/API boundaries. Assign every material project one disposition from the Master Build Brief.

## Highest-signal platform candidates

| Repository / family | Likely DAWN responsibility | Seed disposition | What must be proven |
| --- | --- | --- | --- |
| `StaffDeck` | Digital employee catalogue, SOP/state-machine skills, knowledge, permissions, work records, traces, human takeover, schedules | **ADOPT_AS_SERVICE / INTEGRATE_VIA_ADAPTER candidate** | Licence implications, Apple Silicon deployment, API surface, auth/tenant model, overlap with FounderOS UI and MAF orchestration |
| `agency-agents` | Large specialist-role and operating-playbook library | **EXTRACT_CAPABILITY / REFERENCE_ONLY candidate** | Which roles materially improve DAWN; convert selected role specs into governed MAF agents/skills instead of importing every persona |
| `OmniRoute` | Model/provider gateway, free-tier routing, fallbacks, token/cost optimisation | **ADOPT_AS_SERVICE candidate** | Provider terms, security, local deployment, API compatibility, routing quality and whether it can become DAWN's single model gateway |
| `world-intel-mcp` | Broad world/market/company/risk intelligence over MCP; Qdrant-backed history | **INTEGRATE_VIA_ADAPTER candidate** | Data-source reliability, UK relevance, overlap with DAWN research sources, resource footprint, tool allowlisting |
| `cfo-stack` | Founder/small-business bookkeeping, finance skills, deterministic Beancount ledger/reporting | **EXTRACT_CAPABILITY / INTEGRATE_VIA_ADAPTER candidate** | UK jurisdiction support, review controls, separation of accounting evidence from model advice, high-stakes approval boundaries |

## Existing service candidates that should normally remain intact

- `n8n` — deterministic/event/scheduled automation. Prefer **ADOPT_AS_SERVICE** behind an orchestration adapter rather than rebuilding workflow plumbing.
- `postiz-app` — social scheduling/publishing. Prefer **ADOPT_AS_SERVICE**; external publishing remains Tier 5.
- `firecrawl` — web extraction/research. Prefer **ADOPT_AS_SERVICE / INTEGRATE_VIA_ADAPTER**.
- `graphiti` — temporal/entity knowledge graph. Compare directly with current DAWN memory architecture; likely **INTEGRATE_VIA_ADAPTER** if it closes temporal-memory gaps.
- `obsidian-local-rest-api` — human-readable local knowledge/vault bridge. Likely **INTEGRATE_VIA_ADAPTER**, not canonical machine memory.
- `langfuse` — traces/evaluation/cost observability. Prefer **ADOPT_AS_SERVICE** unless the current proof ledger already supersedes a function.
- `ComfyUI` — local image-generation workflow engine. Prefer **ADOPT_AS_SERVICE** with curated workflows rather than embedding its internals.
- `voicebox` — local voice/audio capability. Evaluate as **ADOPT_AS_SERVICE / INTEGRATE_VIA_ADAPTER**.
- `penpot` — collaborative design system. Keep separate from runtime; expose only useful design operations if needed.
- `webstudio` — website/page-building candidate. Compare against current Deus Intus web workflow before adoption.

## Creative/video cluster — rationalise rather than run all of them

Candidates include `OpenMontage`, `OpenCut`, `hyperframes`, `hyperframes-launch-video`, `flux`, `flux-3-video-api`, `SkyReels-V2`, `stable-diffusion-webui`, `heygen-cli`, `open-design`, `open-codesign`, `huashu-design-en`, `fantastic-posters`, and `AI-Content-Studio`.

The Portfolio Architect should score these by:
1. local Apple Silicon viability,
2. quality,
3. API/CLI automation surface,
4. licence,
5. maintenance,
6. overlap with ComfyUI,
7. suitability for repeatable commercial content production.

Target: a small canonical **Creative Fabric**, not a dozen overlapping runtimes.

## Agent/runtime cluster — rationalise carefully

Candidates include `hermes-agent`, `awesome-hermes-agent`, `open-webui`, `Open-Generative-AI`, `automaton`, `Agent-Reach`, `hail`, `Kimi-K2.5`, `llama-cookbook`, `airllm`, `mlx`, `free-llm-api-resources`, and `OmniRoute`.

Current architectural hypothesis:
- Microsoft Agent Framework = higher-order orchestration kernel.
- FounderOS = founder control plane.
- StaffDeck may provide digital-employee/skill operating surfaces if integration beats rebuilding them.
- OmniRoute may become the provider/model gateway.
- Ollama/MLX remain local execution substrates.
- Hermes should be assessed feature-by-feature; preserve unique proven capabilities rather than keeping overlapping orchestration purely for historical reasons.
- `agency-agents` should seed selected specialist roles, not become another runtime.

## Intelligence/research cluster

Candidates include `world-intel-mcp`, `firecrawl`, `social-media-monitoring-open-source`, `youtube-automation-agent`, `ytxscript`, DAWN sector research code and existing public-data connectors.

Target: one DAWN Intelligence division with source adapters and MCP/tool exposure, shared evidence/receipts, shared memory and scheduled monitoring.

## Business operating capabilities

- `cfo-stack` — finance/accounting capability candidate.
- `StaffDeck` — workforce/process capability candidate.
- `odoo` — archived fork; evaluate only as a reference or external ERP option, not automatically part of DAWN.
- `paypal-rest-api-specifications` and `stripe-ruby` — provider references/SDKs, not DAWN subsystems by themselves.
- `ai-marketing-skills` — candidate skills source for Marketing division.
- `skills` — candidate consolidation point for reusable instructions; avoid duplicate skill definitions across runtimes.

## Venture/product repositories

Repositories such as `deus-intus`, `deus-intus-web`, `Deus-Intus-App`, `deus-intus-second-brain`, `deus-intus-asset-lab`, and the numerous AI-ops/retainer/product concept repos should normally be treated as **ventures, knowledge sources, product backlogs or test tenants**, not core DAWN infrastructure.

Deus Intus should be the first real end-to-end proving ground for the completed platform: research -> planning -> creative -> site/product -> publishing -> commercial operations -> finance -> memory -> proof.

## Consolidation deliverables required from Portfolio Architect

1. Complete inventory count for owned/forked/starred repositories.
2. Domain map with duplicates grouped together.
3. Deep inspection of every high-signal candidate.
4. Canonical component recommendation for each DAWN responsibility.
5. Explicit list of repositories to retire/archive/reference only.
6. Licence/security/resource concerns.
7. Adapter/MCP boundaries for adopted services.
8. Capability gaps remaining after reuse.
9. Dependency-ordered integration plan.
10. First independently verifiable integration work package.
