# FounderOS Agent Runtime

This service is the first Microsoft Agent Framework orchestration nucleus for FounderOS/DAWN.
It is intentionally a sidecar: the existing Next.js runtime, database, connectors and agents remain intact while this service coordinates higher-order missions above them.

## Initial agent nucleus

| Agent | Responsibility | Mutation authority |
| --- | --- | --- |
| Founder Governor | Owns the mission, delegates and demands proof | None |
| Systems Architect | Inspects architecture and chooses the smallest integration seam | Read-only |
| DAWN Operator | Inspects live FounderOS/DAWN APIs and existing capabilities | Read-only |
| Capability Builder | Builds candidate adapters/tools and tests them | `.agent-workspace/` only |
| Independent Verifier | Re-runs checks and challenges claims | Checks only |

The team is orchestrated with Microsoft Agent Framework `MagenticBuilder`.

## Safety boundary

The initial nucleus is deliberately not allowed to edit the canonical repository or run arbitrary shell commands.

- Repository tools are read-only and reject secret-like paths.
- Candidate code is written only below `.agent-workspace/`.
- Verification commands are selected from a fixed allowlist: `python_compile`, `pytest`, `npm_test`, `npm_typecheck`.
- The service binds to `127.0.0.1` by default.
- Live connection failures are returned as failures, not converted into simulated success.

Promotion from `.agent-workspace/` into the real repository is a separate future gate and should require tests, independent verification and a reviewed PR.

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

Run a mission:

```bash
curl -sS -X POST http://127.0.0.1:4200/missions/run \
  -H 'content-type: application/json' \
  -d '{"task":"Inspect FounderOS and DAWN, identify one missing capability needed for reliable orchestration, build a sandboxed candidate, test it, then independently verify the result."}'
```

## What this proves

Stage 1 is complete when:

1. `/readyz` proves both Ollama and the FounderOS agent API are reachable.
2. A mission causes the Governor to delegate real inspection work.
3. The Builder creates a candidate only inside `.agent-workspace/`.
4. A bounded automated check actually executes.
5. The Verifier independently classifies the outcome from evidence.

It does **not** yet prove production deployment, autonomous PR creation, MCP publication, persistent workflow checkpoints or human approval. Those belong to the next gates after this nucleus is proven.
