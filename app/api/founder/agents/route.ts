import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const execFileAsync = promisify(execFile);

const AGENTS = [
  { id: 'antigravity', label: 'Antigravity', bin: 'agy' },
  { id: 'codex', label: 'Codex CLI', bin: 'codex' },
  { id: 'gemini', label: 'Gemini CLI', bin: 'gemini' },
  { id: 'opencode', label: 'OpenCode', bin: 'opencode' },
  { id: 'hermes', label: 'Hermes', bin: 'hermes' },
];

async function detect(bin: string) {
  try {
    const { stdout } = await execFileAsync('/usr/bin/env', ['which', bin], { timeout: 3000 });
    return stdout.trim();
  } catch { return ''; }
}

export async function GET() {
  const agents = await Promise.all(AGENTS.map(async (a) => {
    const command = await detect(a.bin);
    return { id: a.id, label: a.label, available: Boolean(command), command: command || undefined };
  }));
  return Response.json({ agents, host: process.env.HOSTNAME ?? 'local', runtime: 'node' });
}
