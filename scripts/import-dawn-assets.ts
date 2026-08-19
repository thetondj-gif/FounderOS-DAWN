import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { getDb } from '@/lib/data';
import type { Skill } from '@/lib/schemas';

type CandidateKind = 'skill' | 'agent' | 'workflow' | 'prompt' | 'capability' | 'bundle' | 'tool' | 'knowledge' | 'product' | 'other';

type Candidate = {
  kind: CandidateKind;
  sourceRoot: string;
  sourceRepo: string;
  relativePath: string;
  sha256: string;
  bytes: number;
};

type Args = {
  skillsRoot?: string;
  dawnRoot?: string;
  sourceRoots: string[];
  estateRoot?: string;
  applySkills: boolean;
  applyAllSkills: boolean;
  outDir: string;
};

function parseArgs(argv: string[]): Args {
  const out: Args = {
    sourceRoots: [],
    applySkills: false,
    applyAllSkills: false,
    outDir: path.join(process.cwd(), 'migration', 'generated'),
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--apply-skills') out.applySkills = true;
    else if (arg === '--apply-all-skills') out.applyAllSkills = true;
    else if (arg === '--skills-root') out.skillsRoot = argv[++i];
    else if (arg === '--dawn-root') out.dawnRoot = argv[++i];
    else if (arg === '--source-root') out.sourceRoots.push(argv[++i]);
    else if (arg === '--estate-root') out.estateRoot = argv[++i];
    else if (arg === '--out-dir') out.outDir = path.resolve(argv[++i]);
    else if (arg === '--help' || arg === '-h') {
      console.log(`\nFounderOS private-estate asset importer\n\nUsage:\n  npm run import:dawn -- --skills-root /path/to/dawn-skills --dawn-root /path/to/DAWN_OS_Genesis\n  npm run import:dawn -- --source-root /path/to/hermes-agent --source-root /path/to/another-repo\n  npm run import:dawn -- --estate-root /path/containing/repo-checkouts\n\nApply modes:\n  --apply-skills      Import only canonical dawn-skills SKILL.md files\n  --apply-all-skills  Import every discovered SKILL.md as status=learning (review recommended)\n\nDefaults:\n  - discovery/report generation only\n  - no source repository is mutated\n  - every discovered file retains source repo + path + content hash\n`);
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

function repoName(root: string): string {
  return path.basename(root).replace(/\.git$/, '');
}

function sha256(buffer: Buffer | string): string {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

function shouldSkipDir(name: string): boolean {
  return ['.git', 'node_modules', '.next', 'dist', 'build', '.cache', 'coverage', 'vendor'].includes(name);
}

function walk(root: string): string[] {
  const files: string[] = [];
  const stack = [root];
  while (stack.length) {
    const current = stack.pop()!;
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      if (entry.isDirectory() && shouldSkipDir(entry.name)) continue;
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
  if (base === 'skill.md' || p.includes('/skills/') || p.startsWith('skills/') || p.includes('/optional-skills/')) return 'skill';
  if (p.includes('/agents/') || p.startsWith('agents/') || base === 'agents.md' || /(^|[-_.])agent([-_.]|$)/.test(base)) return 'agent';
  if (p.includes('/workflows/') || p.startsWith('workflows/') || /workflow|flow\.md$/.test(base)) return 'workflow';
  if (p.includes('/prompts/') || p.startsWith('prompts/') || /prompt/.test(base)) return 'prompt';
  if (p.includes('/capabilit') || /capabilit/.test(base)) return 'capability';
  if (p.includes('/bundles/') || /bundle/.test(base)) return 'bundle';
  if (p.includes('/tools/') || p.startsWith('tools/') || /tool/.test(base)) return 'tool';
  if (/brain|knowledge|memory|playbook|guide|handbook|reference/.test(p)) return 'knowledge';
  if (/product|venture|offer|retainer|licen[cs]e|service|studio|academy|franchise|commerce/.test(p)) return 'product';
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
  return (body ?? 'Imported from the existing private capability estate for FounderOS configuration.').slice(0, 500);
}

function categoryFor(relativePath: string, slug: string): string {
  const p = relativePath.toLowerCase();
  if (p.startsWith('council/') || p.includes('/council/')) return 'Council';
  if (p.startsWith('system/') || p.includes('/system/')) return 'System';
  if (slug.startsWith('deus-')) return 'Deus Intus';
  if (/content|social|campaign|brand|creative|media|video|image/.test(`${slug} ${p}`)) return 'Content';
  if (/sales|revenue|proposal|lead|crm/.test(`${slug} ${p}`)) return 'Sales';
  if (/research|intel|radar|competitor|venture|osint/.test(`${slug} ${p}`)) return 'Intelligence';
  if (/build|code|product|engineering|mlops|huggingface/.test(`${slug} ${p}`)) return 'Product & Build';
  return 'Imported';
}

function stableSkillId(sourceRepo: string, relativePath: string): string {
  const dir = path.basename(path.dirname(relativePath)).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const repo = sourceRepo.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  return `import-${repo}-${dir}`.slice(0, 120);
}

function discover(root: string): Candidate[] {
  const sourceRepo = repoName(root);
  return walk(root).map((file) => {
    const buffer = fs.readFileSync(file);
    const relativePath = path.relative(root, file);
    return {
      kind: classify(relativePath),
      sourceRoot: root,
      sourceRepo,
      relativePath,
      sha256: sha256(buffer),
      bytes: buffer.length,
    };
  });
}

function discoverSkillsFromRoot(root: string): Skill[] {
  const sourceRepo = repoName(root);
  const found: Skill[] = [];
  let order = 10_000;
  for (const file of walk(root)) {
    if (path.basename(file).toLowerCase() !== 'skill.md') continue;
    const markdown = fs.readFileSync(file, 'utf8');
    if (!markdown.trim()) continue;
    const relativePath = path.relative(root, file);
    const slug = path.basename(path.dirname(file)).toLowerCase();
    const provenance = `\n\n---\nFounderOS migration provenance\n- source_repo: ${sourceRepo}\n- source_path: ${relativePath}\n- source_sha256: ${sha256(markdown)}\n`;
    found.push({
      id: stableSkillId(sourceRepo, relativePath),
      name: titleFromMarkdown(markdown, slug),
      category: categoryFor(relativePath, slug),
      description: descriptionFromMarkdown(markdown),
      ownerAgentId: null,
      status: 'learning',
      tools: [],
      markdown: `${markdown.trimEnd()}${provenance}`,
      order: order++,
    });
  }
  return found.sort((a, b) => a.name.localeCompare(b.name));
}

function rootsFromEstate(estateRoot?: string): string[] {
  const root = existingDir(estateRoot);
  if (!root) return [];
  return fs.readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(root, entry.name))
    .filter((candidate) => fs.existsSync(path.join(candidate, '.git')) || fs.existsSync(path.join(candidate, 'package.json')) || fs.existsSync(path.join(candidate, 'README.md')));
}

function writeJson(file: string, value: unknown): void {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n', 'utf8');
}

function main(): void {
  const args = parseArgs(process.argv.slice(2));
  const canonicalSkillsRoot = existingDir(args.skillsRoot);
  const canonicalDawnRoot = existingDir(args.dawnRoot);
  const explicitRoots = args.sourceRoots.map(existingDir).filter((v): v is string => Boolean(v));
  const estateRoots = rootsFromEstate(args.estateRoot);
  const roots = Array.from(new Set([
    ...(canonicalSkillsRoot ? [canonicalSkillsRoot] : []),
    ...(canonicalDawnRoot ? [canonicalDawnRoot] : []),
    ...explicitRoots,
    ...estateRoots,
  ]));

  if (!roots.length) {
    throw new Error('Provide at least one existing --skills-root, --dawn-root, --source-root or --estate-root. No files were changed.');
  }

  const candidates = roots.flatMap(discover);
  const byKind = candidates.reduce<Record<string, number>>((acc, item) => {
    acc[item.kind] = (acc[item.kind] ?? 0) + 1;
    return acc;
  }, {});

  const canonicalSkills = canonicalSkillsRoot ? discoverSkillsFromRoot(canonicalSkillsRoot) : [];
  const allSkills = roots.flatMap(discoverSkillsFromRoot);
  const uniqueAllSkills = Array.from(new Map(allSkills.map((skill) => [skill.id, skill])).values());

  writeJson(path.join(args.outDir, 'asset-inventory.json'), {
    generatedAt: new Date().toISOString(),
    roots: roots.map((root) => ({ sourceRepo: repoName(root), sourceRoot: root })),
    counts: byKind,
    totalFiles: candidates.length,
    candidates,
  });
  writeJson(path.join(args.outDir, 'founderos-canonical-skills.json'), canonicalSkills);
  writeJson(path.join(args.outDir, 'founderos-all-skill-candidates.json'), uniqueAllSkills);
  writeJson(path.join(args.outDir, 'agent-candidates.json'), candidates.filter((item) => item.kind === 'agent'));
  writeJson(path.join(args.outDir, 'workflow-candidates.json'), candidates.filter((item) => item.kind === 'workflow'));
  writeJson(path.join(args.outDir, 'knowledge-product-candidates.json'), candidates.filter((item) => ['knowledge', 'product'].includes(item.kind)));
  writeJson(path.join(args.outDir, 'tool-prompt-capability-candidates.json'), candidates.filter((item) => ['tool', 'prompt', 'capability', 'bundle'].includes(item.kind)));

  let imported = 0;
  const selectedSkills = args.applyAllSkills ? uniqueAllSkills : (args.applySkills ? canonicalSkills : []);
  if (selectedSkills.length) {
    const db = getDb();
    for (const skill of selectedSkills) {
      db.skills.insert(skill);
      imported += 1;
    }
  }

  console.log(JSON.stringify({
    ok: true,
    discoveryOnly: !args.applySkills && !args.applyAllSkills,
    sourceRepos: roots.map(repoName),
    discoveredFiles: candidates.length,
    canonicalSkills: canonicalSkills.length,
    allSkillCandidates: uniqueAllSkills.length,
    importedSkills: imported,
    outputDirectory: args.outDir,
    note: selectedSkills.length
      ? 'Skills imported as learning with source repo/path/hash provenance. Configure owner/tools/runtime before marking live.'
      : 'No database changes made. Review generated inventories before importing.',
  }, null, 2));
}

main();
