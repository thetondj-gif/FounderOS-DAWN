'use client';

import { useEffect, useMemo, useState } from 'react';
import { Play, RefreshCw, TerminalSquare, CheckCircle2, AlertTriangle } from 'lucide-react';

type Agent = { id: string; label: string; available: boolean; command?: string };
type Job = { id: string; agent: string; status: string; startedAt: string; log?: string; pid?: number };

export function FounderCommandCenter() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [agent, setAgent] = useState('auto');
  const [prompt, setPrompt] = useState('');
  const [workspace, setWorkspace] = useState('');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [activeJob, setActiveJob] = useState<Job | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refreshAgents() {
    const res = await fetch('/api/founder/agents', { cache: 'no-store' });
    if (!res.ok) throw new Error(`agent discovery failed (${res.status})`);
    const body = await res.json();
    setAgents(body.agents ?? []);
  }

  useEffect(() => { refreshAgents().catch((e) => setError(String(e))); }, []);

  const availableCount = useMemo(() => agents.filter((a) => a.available).length, [agents]);

  async function run() {
    if (!prompt.trim() || busy) return;
    setBusy(true); setError(null);
    try {
      const res = await fetch('/api/founder/run', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt.trim(), agent, workspace: workspace.trim() || undefined }),
      });
      const body = await res.json();
      if (!res.ok) throw new Error(body.error ?? `run failed (${res.status})`);
      setPrompt('');
      setActiveJob(body.job);
      setJobs((j) => [body.job, ...j].slice(0, 12));
    } catch (e) { setError(e instanceof Error ? e.message : String(e)); }
    finally { setBusy(false); }
  }

  async function refreshJob(id: string) {
    const res = await fetch(`/api/founder/jobs/${id}`, { cache: 'no-store' });
    const body = await res.json();
    if (!res.ok) throw new Error(body.error ?? 'status failed');
    setActiveJob(body.job);
    setJobs((list) => list.map((j) => j.id === id ? body.job : j));
  }

  useEffect(() => {
    if (!activeJob || !['queued','running'].includes(activeJob.status)) return;
    const t = setInterval(() => refreshJob(activeJob.id).catch(() => {}), 2500);
    return () => clearInterval(t);
  }, [activeJob?.id, activeJob?.status]);

  return (
    <main className="mx-auto flex min-h-[calc(100vh-64px)] w-full max-w-3xl flex-col gap-4 px-3 py-4 sm:px-6 sm:py-8">
      <header className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold tracking-tight sm:text-2xl">Founder Command</h1>
          <p className="mt-1 text-xs text-os-dim">One mobile front door to the agents already installed on your Mini.</p>
        </div>
        <button onClick={() => refreshAgents().catch((e) => setError(String(e)))} className="rounded-md border border-os-border bg-os-surface p-2" aria-label="Refresh agents">
          <RefreshCw className="h-4 w-4" />
        </button>
      </header>

      <section className="rounded-xl border border-os-border bg-os-surface p-3 sm:p-4">
        <div className="mb-3 flex items-center justify-between gap-3 text-xs">
          <span className="font-semibold">Execution route</span>
          <span className="font-mono text-os-dim">{availableCount}/{agents.length} detected</span>
        </div>
        <select value={agent} onChange={(e) => setAgent(e.target.value)} className="w-full rounded-lg border border-os-border bg-os-bg px-3 py-2.5 text-sm">
          <option value="auto">Auto-select strongest available</option>
          {agents.map((a) => <option key={a.id} value={a.id} disabled={!a.available}>{a.label}{a.available ? '' : ' — unavailable'}</option>)}
        </select>
        <input value={workspace} onChange={(e) => setWorkspace(e.target.value)} placeholder="Workspace path (optional; defaults to FounderOS runtime)" className="mt-2 w-full rounded-lg border border-os-border bg-os-bg px-3 py-2.5 text-sm" />
        <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} rows={7} placeholder="Tell the agent what outcome you want. It should build, test and return the finished result." className="mt-2 w-full resize-none rounded-lg border border-os-border bg-os-bg px-3 py-3 text-sm leading-relaxed" />
        <button onClick={run} disabled={busy || !prompt.trim() || availableCount === 0} className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-os-text px-4 py-3 text-sm font-bold text-os-bg disabled:opacity-40">
          <Play className="h-4 w-4" /> {busy ? 'Launching…' : 'Execute'}
        </button>
        {error && <div className="mt-3 flex gap-2 rounded-lg border border-os-err/30 p-2.5 text-xs text-os-err"><AlertTriangle className="h-4 w-4 shrink-0" />{error}</div>}
      </section>

      {activeJob && (
        <section className="rounded-xl border border-os-border bg-os-surface p-3 sm:p-4">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-sm font-semibold"><TerminalSquare className="h-4 w-4" />{activeJob.agent}</div>
            <div className="flex items-center gap-1.5 font-mono text-[11px] uppercase text-os-dim">
              {activeJob.status === 'complete' && <CheckCircle2 className="h-3.5 w-3.5 text-os-ok" />}{activeJob.status}
            </div>
          </div>
          <pre className="mt-3 max-h-[45vh] overflow-auto whitespace-pre-wrap rounded-lg bg-os-bg p-3 font-mono text-[11px] leading-relaxed text-os-muted">{activeJob.log || 'Process launched. Waiting for output…'}</pre>
          <button onClick={() => refreshJob(activeJob.id)} className="mt-2 text-xs font-semibold text-os-muted">Refresh output</button>
        </section>
      )}

      {jobs.length > 0 && <section className="space-y-2 pb-8"><h2 className="text-xs font-bold uppercase tracking-wider text-os-dim">Recent jobs</h2>{jobs.map((j) => <button key={j.id} onClick={() => refreshJob(j.id)} className="flex w-full items-center justify-between rounded-lg border border-os-border bg-os-surface px-3 py-2 text-left text-xs"><span className="truncate">{j.agent} · {j.id}</span><span className="font-mono uppercase text-os-dim">{j.status}</span></button>)}</section>}
    </main>
  );
}
