import { readFile } from 'node:fs/promises';
import path from 'node:path';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const JOB_ROOT = process.env.FOUNDER_JOB_ROOT || '/tmp/founder-os-jobs';

function validId(id: string) {
  return /^[0-9a-f-]{36}$/i.test(id);
}

export async function GET(_: Request, { params }: { params: { id: string } }) {
  const id = params.id;
  if (!validId(id)) return Response.json({ error: 'invalid job id' }, { status: 400 });

  try {
    const dir = path.join(JOB_ROOT, id);
    const meta = JSON.parse(await readFile(path.join(dir, 'meta.json'), 'utf8'));
    let log = '';
    try {
      const raw = await readFile(path.join(dir, 'output.log'), 'utf8');
      log = raw.length > 120000 ? raw.slice(-120000) : raw;
    } catch {}

    if (meta.status === 'running' && meta.pid) {
      try { process.kill(meta.pid, 0); }
      catch { meta.status = 'finished_unknown'; }
    }

    return Response.json({ job: { ...meta, log } });
  } catch {
    return Response.json({ error: 'job not found' }, { status: 404 });
  }
}
