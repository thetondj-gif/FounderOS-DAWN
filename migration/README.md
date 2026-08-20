# DAWN assets → FounderOS

This migration layer is intentionally separate from FounderOS runtime wiring.
It preserves reusable operator IP without importing the DAWN kernel, mission
orchestration, PostgreSQL/Qdrant authority, bridge code, or other runtime
assumptions.

## What is imported now

`npm run import:dawn` scans the existing DAWN repositories and produces a
complete file inventory. Existing `SKILL.md` files under `skills/`, `council/`
and `system/` are converted into native FounderOS `Skill` records with the full
Markdown body preserved.

Imported skills are deliberately marked `learning`, with `ownerAgentId=null`
and `tools=[]`. This prevents a migrated document from being falsely presented
as a live runtime capability before you configure the FounderOS agent/tool that
will execute it.

## What is inventoried for conversion next

The importer writes separate candidate inventories for:

- agents;
- workflows;
- tools;
- prompts;
- capabilities;
- bundles.

Those records are not silently converted because FounderOS expects an agent to
map to a real runtime `run()` implementation and workflows to reference actual
FounderOS agents/tools. The inventory makes the migration explicit and lossless
before those bindings are configured.

## Commands

Discovery only (no database changes):

```bash
npm run import:dawn -- \
  --skills-root /Users/alinton/dawn-skills \
  --dawn-root /Users/alinton/dawn-v4/DAWN_OS_Genesis
```

Import the discovered skills into the current FounderOS SQLite database:

```bash
npm run import:dawn -- \
  --skills-root /Users/alinton/dawn-skills \
  --dawn-root /Users/alinton/dawn-v4/DAWN_OS_Genesis \
  --apply-skills
```

If one of those source directories is elsewhere, pass its real path. A missing
root is never invented or treated as an empty source.

Generated reports are written to `migration/generated/` and should normally be
reviewed before committing because they describe the local source estate.

## Migration truth states

- `learning`: imported definition exists in FounderOS but its runtime/tool
  binding is not yet proven.
- `live`: use only after the corresponding FounderOS agent/tool integration is
  actually configured and tested.

The migration does not delete or mutate the source DAWN repositories.
