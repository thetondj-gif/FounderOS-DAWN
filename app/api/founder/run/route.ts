import { randomUUID } from 'node:crypto';
import { mkdir, open, writeFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import path from 'node:path';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const JOB_ROOT = process.env.FOUNDER_JOB_ROOT || '/tmp/founder-os-jobs';
const WORKSPACE_ROOT = path.resolve(process.env.FOUNDER_WORKSPACE_ROOT || process.cwd());

type AgentId = 'antigravity' | 'codex' | 'gemini' | 'opencode' | 'hermes';
const PRIORITY: AgentId[] = ['antigravity', 'codex', 'gemini', 'opencode', 'hermes'];

const adapters: Record<AgentId, { bin: string; args: (prompt: string) => string[] }> = {
  antigravity: { bin: process.env.FOUNDER_ANTIGRAVITY_BIN || 'agy', args: (p) => ['-p', p, '--print-timeout', '20m'] },
  codex: { bin: process.env.FOUNDER_CODEX_BIN || 'codex', args: (p) => ['exec', '--full-auto', p] },
  gemini: { bin: process.env.FOUNDER_GEMINI_BIN || 'gemini', args: (p) => ['-p', p] },
  opencode: { bin: process.env.FOUNDER_OPENCODE_BIN || 'opencode', args: (p) => ['run', p] },
  hermes: { bin: process.env.FOUNDER_HERMES_BIN || 'hermes', args: (p) => ['chat', '--prompt', p] },
};

async function exists(bin: string) {
  return new Promise<boolean>((resolve) => {
    const child = spawn('/usr/bin/env', ['which', bin], { stdio: 'ignore' });
    child.once('exit', (code) => resolve(code === 0));
    child.once('error', () => resolve(false));
  });
}

function safeWorkspace(requested?: string) {
  if (!requested) return WORKSPACE_ROOT;
  const resolved = path.resolve(requested);
  if (resolved !== WORKSPACE_ROOT && !resolved.startsWith(WORKSPACE_ROOT + path.sep)) {
    throw new Error(`workspace must be inside ${WORKSPACE_ROOT}`);
  }
  return resolved;
}

async function selectAgent(requested: string): Promise<AgentId> {
  if (requested !== 'auto') {
    if (!(requested in adapters)) throw new Error('unknown agent');
    const id = requested as AgentId;
    if (!(await exists(adapters[id].bin))) throw new Error(`${id} is not installed on this host`);
    return id;
  }
  for (const id of PRIORITY) if (await exists(adapters[id].bin)) return id;
  throw new Error('no supported local execution agent is currently available');
}

export async function POST(req: Request) {
  if (process.env.VERCEL) {
    return Response.json({ error: 'Direct agent execution must run on the Mac Mini host runtime, not Vercel.' }, { status: 409 });
  }

  try {
    const body = await req.json() as { prompt?: string; agent?: string; workspace?: string };
    const prompt = String(body.prompt || '').trim();
    if (!prompt) return Response.json({ error: 'prompt is required' }, { status: 400 });
    if (prompt.length > 40000) return Response.json({ error: 'prompt exceeds 40,000 characters' }, { status: 413 });

    const agent = await selectAgent(body.agent || 'auto');
    const cwd = safeWorkspace(body.workspace);
    const id = randomUUID();
    const dir = path.join(JOB_ROOT, id);
    await mkdir(dir, { recursive: true });
    const logPath = path.join(dir, 'output.log');
    const metaPath = path.join(dir, 'meta.json');
    const logHandle = await open(logPath, 'a');
    const adapter = adapters[agent];
    const startedAt = new Date().toISOString();

    const child = spawn(adapter.bin, adapter.args(prompt), {
      cwd,
      env: { ...process.env, FOUNDER_JOB_ID: id },
      stdio: ['ignore', logHandle.fd, logHandle.fd],
      detached: false,
    });

    const meta = { id, agent, status: 'running', startedAt, cwd, pid: child.pid };
    await writeFile(metaPath, JSON.stringify(meta, null, 2));

    child.once('exit', async (code, signal) => {
      const finalMeta = { ...meta, status: code === 0 ? 'complete' : 'failed', finishedAt: new Date().toISOString(), exitCode: code, signal };
      await writeFile(metaPath, JSON.stringify(finalMeta, null, 2)).catch(() => {});
      await logHandle.close().catch(() => {});
    });
    child.once('error', async (error) => {
      const finalMeta = { ...meta, status: 'failed', finishedAt: new Date().toISOString(), error: error.message };
      await writeFile(metaPath, JSON.stringify(finalMeta, null, 2)).catch(() => {});
      await logHandle.close().catch(() => {});
    });

    return Response.json({ job: meta }, { status: 202 });
  } catch (error) {
    return Response.json({ error: error instanceof Error ? error.message : String(error) }, { status: 400 });
  }
}
