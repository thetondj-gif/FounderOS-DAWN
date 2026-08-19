# DAWN V4 Command Center Integration

## Purpose

This repository retains the FounderOS frontend shell while DAWN V4 supplies its data and operational rules for the `deus-intus` tenant.

## Authority model

- PostgreSQL is canonical for tenants, CRM entities, missions, facts, decisions, evidence metadata and ingestion state.
- Google Drive and Sheets are source, staging, review and founder-readable surfaces.
- Qdrant is a derived, rebuildable semantic index.
- Runtime memory is non-canonical.

## Current safety state

The integration defaults to `PREPARED_NOT_CONNECTED` and `STAGING_ONLY`. It must not initiate connector writes or treat Drive rows as canonical data. Google Workspace integration is read-first; GitHub and publishing remain approval-gated.

## Data sources

The Drive IDs and ingestion constraints are stored in `config/dawn/google-drive-intake.json`. They are references only, not credentials. Do not commit API keys, OAuth tokens, service account JSON, tunnel tokens or database passwords.

## Mac Mini deployment

From the checked-out `FounderOS-DAWN` repo on the Mac Mini:

```bash
git fetch origin
git checkout feat/command-center
git pull --ff-only origin feat/command-center
npm ci
npm run dev -- -p 4101
```

Use a production process manager only after a successful local build:

```bash
npm run build
npm run start -- -p 4101
```

The existing process on port 4100 can be inspected with `lsof -nP -iTCP:4100 -sTCP:LISTEN`. Do not expose the app publicly through a tunnel until authentication and the connector write gates are verified.
