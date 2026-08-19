# FounderOS Agent Runtime

This service is the first Microsoft Agent Framework orchestration nucleus for FounderOS/DAWN.
It is intentionally a sidecar: the existing Next.js runtime, database, connectors and agents remain intact while this service coordinates higher-order missions above them.

## Bootstrap organisation

| Agent | Responsibility | Mutation authority |
| --- | --- | --- |
| Founder Governor | Owns the mission, delegates and demands proof | None |
| Portfolio Architect | Audits owned/forked/starred GitHub projects and produces the adoption/integration map | Read-only |
| Systems Architect | Converts capability + portfolio evidence into the target architecture | Read-only |
| DAWN Operator | Inspects live FounderOS/DAWN APIs and existing capabilities | Read-only |
| Capability Builder | Builds candidate agents/adapters/tools/workflows and tests them | `.agent-workspace/` only |
| Independent Verifier | Re-runs checks and challenges claims | Checks only |

The team is orchestrated with Microsoft Agent Framework `MagenticBuilder`.

## Master build brief

Every mission is automatically wrapped with the canonical DAWN/FounderOS master brief. It defines:

- FounderOS / Microsoft Agent Framework / DAWN separation of responsibilities
- inspect-before-inventing and reuse-first rules
- GitHub estate assimilation before substantial new platform builds
- required operating domains for the completed organisation
- permission Tiers 0-5
- PROVEN / PARTIAL / BLOCKED / FAILED / PROPOSED evidence semantics
- self-expansion rules for additional specialist agents, workflows and adapters
- system-level completion criteria
- bootstrap and portfolio-audit missions

The brief is available through `GET /brief` and to every bootstrap agent through `read_master_brief`.

## Capability discovery and GitHub portfolio audit

The runtime includes the DAWN capability catalogue plus a read-only GitHub Portfolio Reader. The Portfolio Architect can page through owned repositories and public stars, then inspect high-signal repository metadata, licence and README content.

Material projects receive one disposition:

- `ADOPT_AS_SERVICE`
- `INTEGRATE_VIA_ADAPTER`
- `EXTRACT_CAPABILITY`
- `REFERENCE_ONLY`
- `SUPERSEDED`
- `IGNORE`

This is intentionally not a "merge every fork" mechanism. Mature systems should normally stay intact behind a narrow DAWN adapter.

Without a token, the portfolio reader sees public owned repositories plus public stars. A read-scoped GitHub token enables the private owned estate; the adapter has no GitHub mutation functions.

```bash
export FOUNDER_AGENT_GITHUB_OWNER=thetondj-gif
export FOUNDER_AGENT_GITHUB_TOKEN='<read-scoped token>'  # optional for private owned repos
```

API surfaces:

```bash
curl http://127.0.0.1:4200/brief
curl 'http://127.0.0.1:4200/capabilities?q=memory'
curl http://127.0.0.1:4200/capabilities/github-portfolio
curl http://127.0.0.1:4200/portfolio
```

Agent tools include `audit_github_portfolio` and `inspect_github_repository`. Inventory pages expose continuation offsets so the Portfolio Architect is instructed to scan the whole estate rather than only the first page.

## Safety boundary

The bootstrap organisation is deliberately not allowed to edit the canonical repository or run unrestricted host commands.

- GitHub portfolio operations are read-only.
- Repository tools are read-only and reject secret-like paths.
- Candidate code is written only below `.agent-workspace/`.
- `python_compile` may run on the host because it parses/compiles without importing candidate modules.
- Executable Python tests use `python_unittest_sandbox`, which runs in Docker with networking disabled, all Linux capabilities dropped, `no-new-privileges`, CPU/memory/PID limits, a read-only root filesystem and a read-only workspace mount.
- The service binds to `127.0.0.1` by default.
- Live connection failures are returned as failures, not converted into simulated success.
- The Builder can create candidate specialist agents and adapters, but cannot promote them into the canonical system itself.

Promotion from `.agent-workspace/` into the real repository is a separate gate and should require tests, independent verification and a reviewed PR.

## Install

```bash
cd services/agent-runtime
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e '.[dev]'
```

The runtime uses local Ollama by default:

```bash
export FOUNDER_AGENT_OLLAMA_HOST=http://127.0.0.1:11434
export FOUNDER_AGENT_OLLAMA_MODEL=qwen3.5:9b
export FOUNDER_OS_BASE_URL=http://127.0.0.1:4100
export FOUNDER_AGENT_PORT=4200
```

## Run

```bash
founderos-agents
```

Health and readiness:

```bash
curl http://127.0.0.1:4200/healthz
curl http://127.0.0.1:4200/readyz
curl http://127.0.0.1:4200/agents
```

Run the complete GitHub estate analysis:

```bash
curl -sS -X POST http://127.0.0.1:4200/missions/portfolio-audit
```

Run the canonical bootstrap mission, which now consumes capability and GitHub-estate evidence:

```bash
curl -sS -X POST http://127.0.0.1:4200/missions/bootstrap
```

## Proof boundary

CI proves construction, safety rules, portfolio classification primitives and framework compatibility. Live host proof still requires `/readyz` plus an actual portfolio/bootstrap mission against the Mac-hosted Ollama and FounderOS runtime.

It does **not** yet prove production deployment, autonomous PR promotion, MCP publication, persistent workflow checkpoints or human approval. Those remain subsequent evidence gates.
