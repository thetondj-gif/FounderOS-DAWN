import { beforeAll, describe, expect, test } from 'vitest';
import { mkdtempSync, readdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

beforeAll(() => {
  process.env.FOUNDER_OS_DB = path.join(mkdtempSync(path.join(tmpdir(), 'founder-os-smoke-')), 'test.db');
  process.env.FUNNEL_PROVIDER = 'seed';
  process.env.GBRAIN_BIN = path.join(tmpdir(), 'founder-os-no-gbrain-cli');
});

type PageEntry = {
  file: string;
  load: () => Promise<{ default: (props?: any) => unknown }>;
  props?: unknown;
};

const PAGES: PageEntry[] = [
  { file: 'page.tsx', load: () => import('@/app/page') },
  { file: 'comms/page.tsx', load: () => import('@/app/comms/page') },
  { file: 'social/page.tsx', load: () => import('@/app/social/page') },
  { file: 'social/[platform]/page.tsx', load: () => import('@/app/social/[platform]/page'), props: { params: { platform: 'instagram' } } },
  { file: 'social/beehiiv/page.tsx', load: () => import('@/app/social/beehiiv/page') },
  { file: 'content/page.tsx', load: () => import('@/app/content/page') },
  { file: 'content/lead-magnets/page.tsx', load: () => import('@/app/content/lead-magnets/page') },
  { file: 'agents/page.tsx', load: () => import('@/app/agents/page') },
  { file: 'founder/page.tsx', load: () => import('@/app/founder/page') },
  { file: 'tasks/page.tsx', load: () => import('@/app/tasks/page') },
  { file: 'skills/page.tsx', load: () => import('@/app/skills/page') },
  { file: 'org/page.tsx', load: () => import('@/app/org/page'), props: { searchParams: {} } },
  { file: 'brain/page.tsx', load: () => import('@/app/brain/page') },
  { file: 'doctor/page.tsx', load: () => import('@/app/doctor/page') },
  { file: 'finances/page.tsx', load: () => import('@/app/finances/page') },
  { file: 'funnel/page.tsx', load: () => import('@/app/funnel/page'), props: { searchParams: {} } },
  { file: 'workflows/page.tsx', load: () => import('@/app/workflows/page') },
  { file: 'integrations/page.tsx', load: () => import('@/app/integrations/page') },
  { file: 'roadmap/page.tsx', load: () => import('@/app/roadmap/page') },
  { file: 'analytics/page.tsx', load: () => import('@/app/analytics/page') },
  { file: 'reference/page.tsx', load: () => import('@/app/reference/page') },
  { file: 'personas/page.tsx', load: () => import('@/app/personas/page') },
];

function discoverPages(dir: string, base = ''): string[] {
  const out: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const rel = base ? `${base}/${entry.name}` : entry.name;
    if (entry.isDirectory()) out.push(...discoverPages(path.join(dir, entry.name), rel));
    else if (entry.name === 'page.tsx') out.push(rel);
  }
  return out;
}

describe('platform smoke — every page renders without throwing', () => {
  test.each(PAGES)('$file renders', async ({ load, props }) => {
    const mod = await load();
    const Page = mod.default;
    await expect(Promise.resolve(Page(props))).resolves.toBeTruthy();
  }, 20_000);

  test('the smoke net covers every app/**/page.tsx (no page escapes)', () => {
    const discovered = discoverPages(path.join(process.cwd(), 'app')).sort();
    const covered = PAGES.map((p) => p.file).sort();
    expect(covered).toEqual(discovered);
  });
});
