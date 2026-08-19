# FounderOS Agent Runtime

This service is the first Microsoft Agent Framework orchestration nucleus for FounderOS/DAWN.
It is intentionally a sidecar: the existing Next.js runtime, database, connectors and agents remain intact while this service coordinates higher-order missions above them.

## Initial agent nucleus

| Agent | Responsibility | Mutation authority |
| --- | --- | --- |
| Founder Governor | Owns the mission, delegates and demands proof | None |
| Systems Architect | Inspects architecture and chooses the smallest integration seam | Read-only |
| DAWN Operator | Inspects live FounderOS/DAWN APIs and existing capabilities | Read-only |
| Capability Builder | Builds candidate agents/adapters/tools/workflows and tests them | `.agent-workspace/` only |
| Independent Verifier | Re-runs checks and challenges claims | Checks only |

The team is orchestrated with Microsoft Agent Framework `MagenticBuilder`.

## Master build brief

Every mission is automatically wrapped with the canonical DAWN/FounderOS master brief. It defines:

- FounderOS / Microsoft Agent Framework / DAWN separation of responsibilities
- inspect-before-inventing and reuse-first rules
- the required operating domains for the completed organisation
- permission Tiers 0-5
- PROVEN / PARTIAL / BLOCKED / FAILED / PROPOSED evidence semantics
- self-expansion rules for additional specialist agents, workflows and adapters
- system-level completion criteria
- the first bootstrap mission

The brief is available through `GET /brief` and to every bootstrap agent through the `read_master_brief` tool.

## Capability discovery gateway

The runtime includes a canonical capability catalogue covering the current/target stack: FounderOS, Microsoft Agent Framework, GitHub, Ollama, MLX, OpenAI, Hermes, n8n, Composio, Gmail, Google Calendar/Drive, Postiz, Firecrawl, Playwright, Qdrant, Graphiti, Obsidian, Langfuse, ComfyUI, Voicebox, MCP, skills, scripts, datasets, PostgreSQL, DAWN research intelligence, the Capability Foundry and proof ledger.

Catalogue metadata deliberately distinguishes `available`, `known` and `requires-adapter`. A catalogue record is not proof that a service is connected. Agents have `discover_capabilities`, `inspect_capability` and safe `probe_capability` tools; runtime connection/skill snapshots are also included when discovery runs.

API surfaces:

```bash
curl http://127.0.0.1:4200/brief
curl 'http://127.0.0.1:4200/capabilities?q=memory'
curl http://127.0.0.1:4200/capabilities/qdrant
```

## Safety boundary

The initial nucleus is deliberately not allowed to edit the canonical repository or run unrestricted host commands.

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

The runtime uses local Ollama by default. Override any setting as needed:

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

Run an arbitrary mission under the master brief:

```bash
curl -sS -X POST http://127.0.0.1:4200/missions/run \
  -H 'content-type: application/json' \
  -d '{"task":"Inspect FounderOS and DAWN, identify one missing capability needed for reliable orchestration, build a sandboxed candidate, test it, then independently verify the result."}'
```

Run the canonical bootstrap mission:

```bash
curl -sS -X POST http://127.0.0.1:4200/missions/bootstrap
```

## What this proves

Stage 1 is complete when:

1. `/readyz` proves both Ollama and the FounderOS agent API are reachable.
2. A mission causes the Governor to delegate real inspection work.
3. The team consults the capability catalogue before inventing a new component.
4. The Builder creates a candidate only inside `.agent-workspace/`.
5. A bounded automated check actually executes, with executable candidate code confined to Docker.
6. The Verifier independently classifies the outcome from evidence.

It does **not** yet prove production deployment, autonomous PR promotion, MCP publication, persistent workflow checkpoints or human approval. Those belong to the next gates after this nucleus is proven on the live DAWN host.
