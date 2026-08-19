import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { getDb } from '@/lib/data';
import type { Skill } from '@/lib/schemas';

type CandidateKind = 'skill' | 'agent' | 'workflow' | 'prompt' | 'capability' | 'bundle' | 'tool' | 'other';

type Candidate = {
  kind: CandidateKind;
  sourceRoot: string;
  relativePath: string;
  sha256: string;
  bytes: number;
};

type Args = {
  skillsRoot?: string;
  dawnRoot?: string;
  applySkills: boolean;
  outDir: string;
};

function parseArgs(argv: string[]): Args {
  const out: Args = {
    applySkills: false,
    outDir: path.join(process.cwd(), 'migration', 'generated'),
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--apply-skills') out.applySkills = true;
    else if (arg === '--skills-root') out.skillsRoot = argv[++i];
    else if (arg === '--dawn-root') out.dawnRoot = argv[++i];
    else if (arg === '--out-dir') out.outDir = path.resolve(argv[++i]);
    else if (arg === '--help' || arg === '-h') {
      console.log(`\nFounderOS DAWN asset importer\n\nUsage:\n  npm run import:dawn -- --skills-root /path/to/dawn-skills --dawn-root /path/to/DAWN_OS_Genesis [--apply-skills]\n\nDefaults:\n  - discovery/report generation only\n  - skills are imported only with --apply-skills\n  - imported skills are status=learning until you configure/prove their runtime tools\n`);
      process.exit(0);
    }
  }
  return out;
}

function existingDir(value?: string): string | undefined {
  if (!value) return undefined;
  const resolved = path.resolve(value);
  return fs.existsSync(resolved) && fs.statSync(resolved).isDirectory() ? resolved : undefined;
}

function sha256(buffer: Buffer | string): string {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

function walk(root: string): string[] {
  const files: string[] = [];
  const stack = [root];
  while (stack.length) {
    const current = stack.pop()!;
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      if (entry.name === '.git' || entry.name === 'node_modules' || entry.name === '.next') continue;
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) stack.push(full);
      else if (entry.isFile()) files.push(full);
    }
  }
  return files.sort();
}

function classify(relativePath: string): CandidateKind {
  const p = relativePath.toLowerCase();
  const base = path.basename(p);
  if (base === 'skill.md' || p.includes('/skills/')) return 'skill';
  if (p.includes('/agents/') || /(^|[-_.])agent([-_.]|$)/.test(base)) return 'agent';
  if (p.includes('/workflows/') || /workflow/.test(base)) return 'workflow';
  if (p.includes('/prompts/') || /prompt/.test(base)) return 'prompt';
  if (p.includes('/capabilit') || /capabilit/.test(base)) return 'capability';
  if (p.includes('/bundles/') || /bundle/.test(base)) return 'bundle';
  if (p.includes('/tools/') || /tool/.test(base)) return 'tool';
  return 'other';
}

function titleFromMarkdown(markdown: string, fallback: string): string {
  const heading = markdown.match(/^#\s+(.+)$/m)?.[1]?.trim();
  if (heading) return heading.replace(/^DAWN\s*[-—:]?\s*/i, '').slice(0, 100);
  return fallback
    .split(/[-_]/g)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
    .slice(0, 100);
}

function descriptionFromMarkdown(markdown: string): string {
  const body = markdown
    .replace(/^---[\s\S]*?---\s*/m, '')
    .replace(/^#.*$/gm, '')
    .split(/\n\s*\n/)
    .map((p) => p.replace(/[`*_>#-]/g, '').trim())
    .find((p) => p.length >= 20);
  return (body ?? 'Imported from the existing DAWN skill library for FounderOS configuration.').slice(0, 500);
}

function categoryFor(relativePath: string, slug: string): string {
  const p = relativePath.toLowerCase();
  if (p.startsWith('council/') || p.includes('/council/')) return 'Council';
  if (p.startsWith('system/') || p.includes('/system/')) return 'System';
  if (slug.startsWith('deus-')) return 'Deus Intus';
  if (/content|social|campaign|brand|creative|media/.test(slug)) return 'Content';
  if (/sales|revenue|proposal|lead|crm/.test(slug)) return 'Sales';
  if (/research|intel|radar|competitor|venture/.test(slug)) return 'Intelligence';
  if (/build|code|product|engineering/.test(slug)) return 'Product & Build';
  return 'Imported';
}

function stableSkillId(relativePath: string): string {
  const dir = path.basename(path.dirname(relativePath)).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const namespace = relativePath.split(path.sep)[0].toLowerCase().replace(/[^a-z0-9]+/g, '-');
  return `dawn-${namespace}-${dir}`.slice(0, 120);
}

function discover(root: string): Candidate[] {
  return walk(root).map((file) => {
    const buffer = fs.readFileSync(file);
    const relativePath = path.relative(root, file);
    return {
      kind: classify(relativePath),
      sourceRoot: root,
      relativePath,
      sha256: sha256(buffer),
      bytes: buffer.length,
    };
  });
}

function discoverSkills(skillsRoot: string): Skill[] {
  const roots = ['skills', 'council', 'system']
    .map((folder) => path.join(skillsRoot, folder))
    .filter((folder) => fs.existsSync(folder) && fs.statSync(folder).isDirectory());

  const found: Skill[] = [];
  let order = 10_000;
  for (const root of roots) {
    for (const file of walk(root)) {
      if (path.basename(file).toLowerCase() !== 'skill.md') continue;
      const markdown = fs.readFileSync(file, 'utf8');
      if (!markdown.trim()) continue;
      const relativePath = path.relative(skillsRoot, file);
      const slug = path.basename(path.dirname(file)).toLowerCase();
      found.push({
        id: stableSkillId(relativePath),
        name: titleFromMarkdown(markdown, slug),
        category: categoryFor(relativePath, slug),
        description: descriptionFromMarkdown(markdown),
        ownerAgentId: null,
        status: 'learning',
        tools: [],
        markdown,
        order: order++,
      });
    }
  }
  return found.sort((a, b) => a.name.localeCompare(b.name));
}

function writeJson(file: string, value: unknown): void {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n', 'utf8');
}

function main(): void {
  const args = parseArgs(process.argv.slice(2));
  const skillsRoot = existingDir(args.skillsRoot);
  const dawnRoot = existingDir(args.dawnRoot);

  if (!skillsRoot && !dawnRoot) {
    throw new Error('Provide at least one existing --skills-root or --dawn-root directory. No files were changed.');
  }

  const candidates = [
    ...(skillsRoot ? discover(skillsRoot) : []),
    ...(dawnRoot ? discover(dawnRoot) : []),
  ];
  const byKind = candidates.reduce<Record<string, number>>((acc, item) => {
    acc[item.kind] = (acc[item.kind] ?? 0) + 1;
    return acc;
  }, {});

  const skills = skillsRoot ? discoverSkills(skillsRoot) : [];
  writeJson(path.join(args.outDir, 'asset-inventory.json'), {
    generatedAt: new Date().toISOString(),
    roots: { skillsRoot: skillsRoot ?? null, dawnRoot: dawnRoot ?? null },
    counts: byKind,
    totalFiles: candidates.length,
    candidates,
  });
  writeJson(path.join(args.outDir, 'founderos-skills.json'), skills);
  writeJson(
    path.join(args.outDir, 'agent-candidates.json'),
    candidates.filter((item) => item.kind === 'agent'),
  );
  writeJson(
    path.join(args.outDir, 'workflow-candidates.json'),
    candidates.filter((item) => item.kind === 'workflow'),
  );
  writeJson(
    path.join(args.outDir, 'tool-prompt-capability-candidates.json'),
    candidates.filter((item) => ['tool', 'prompt', 'capability', 'bundle'].includes(item.kind)),
  );

  let imported = 0;
  if (args.applySkills && skills.length) {
    const db = getDb();
    for (const skill of skills) {
      db.skills.insert(skill);
      imported += 1;
    }
  }

  console.log(JSON.stringify({
    ok: true,
    discoveryOnly: !args.applySkills,
    discoveredFiles: candidates.length,
    discoveredSkills: skills.length,
    importedSkills: imported,
    outputDirectory: args.outDir,
    note: args.applySkills
      ? 'Skills imported as learning. Configure owner/tools/runtime before marking live.'
      : 'No database changes made. Re-run with --apply-skills to import discovered skills.',
  }, null, 2));
}

main();
