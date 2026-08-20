# DAWN Show Mode

Status: operating requirement; host execution not yet proven.

## Purpose
Protect live DJ/audio performance on the Mac mini while DAWN remains available at reduced capacity.

## Behaviour
When Show Mode is active, DAWN must prioritise audio stability over local AI throughput.

### Keep available
- FounderOS/control-plane health surfaces where lightweight
- PostgreSQL/Qdrant and other low-impact state services when safe
- lightweight monitoring and receipts
- remote/cloud agent work that does not materially load the Mac
- queued work intake, provided execution can be deferred safely

### Pause, defer or throttle
- Ollama/MLX inference unless explicitly allowlisted and resource-safe
- ComfyUI image generation
- local video generation/rendering/transcoding
- bulk embedding/indexing jobs
- high-concurrency agent execution
- large Docker builds/tests
- CPU/GPU intensive crawls or browser automation
- non-urgent maintenance, backups, migrations and batch jobs

## Activation model
Initial implementation should be explicit/manual and reversible. Automatic detection may be added only after it is proven reliable and cannot accidentally interrupt a show.

Suggested interface:
- `show-mode on`
- `show-mode status`
- `show-mode off`

FounderOS should also expose the current operating profile visibly.

## Resource policy
Show Mode should use a declarative allow/defer policy rather than killing arbitrary processes. Each DAWN capability should eventually declare its expected CPU, memory, GPU and latency impact so the resource governor can make deterministic decisions.

## Queue semantics
Work blocked by Show Mode is DEFERRED, not FAILED. Deferred jobs must remain visible with their reason and resume only after Show Mode is disabled or an explicit override is granted.

## Safety
- Never terminate or reconfigure DJ/audio applications.
- Never assume an audio process is safe to stop.
- Never run destructive cleanup to free resources.
- External/cloud work may continue only when it does not materially increase host load or require local heavy processing.
- Exiting Show Mode must restore only services/jobs that DAWN itself paused; it must not alter unrelated user processes.

## Proof required before production use
1. Baseline Mac resource measurements with DAWN idle.
2. Controlled heavy-workload test without Show Mode.
3. Equivalent test with Show Mode enabled.
4. Verification that heavy jobs are deferred/throttled and lightweight control-plane functions remain responsive.
5. Verification that enabling/disabling Show Mode does not terminate unrelated processes.
6. Recovery proof that deferred DAWN jobs can resume normally.

Until those checks pass on the actual Mac mini, Show Mode is PROPOSED/IMPLEMENTED-AS-POLICY, not PROVEN operational.