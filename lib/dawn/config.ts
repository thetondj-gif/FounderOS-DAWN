export const DAWN_CONFIG = {
  tenant: {
    key: process.env.DAWN_TENANT_KEY ?? 'deus-intus',
    name: 'Deus Intus',
    status: 'PREPARED',
  },
  dataPlane: {
    status: process.env.DAWN_DATA_PLANE_STATUS ?? 'PREPARED_NOT_CONNECTED',
    writeMode: process.env.DAWN_WRITE_MODE ?? 'STAGING_ONLY',
    canonicalTruth: 'PostgreSQL',
    semanticIndex: 'Qdrant',
  },
  connectorState: process.env.DAWN_CONNECTOR_STATE ?? 'DECLARED_UNPROVEN',
  sectors: [
    { key: 'construction', name: 'Construction', scope: 'UK' },
    { key: 'energy', name: 'Energy', scope: 'UK' },
    { key: 'facilities', name: 'Facilities', scope: 'UK' },
    { key: 'property', name: 'Property', scope: 'UK' },
    { key: 'trades', name: 'Trades', scope: 'UK' },
    { key: 'academy', name: 'Academy / Education', scope: 'Global' },
    { key: 'coaching', name: 'Coaching', scope: 'Global' },
    { key: 'media', name: 'Media', scope: 'Global' },
    { key: 'photography', name: 'Photography', scope: 'Global' },
    { key: 'podcast', name: 'Podcast', scope: 'Global' },
    { key: 'ugc', name: 'UGC', scope: 'Global' },
    { key: 'saas-smb', name: 'SaaS / SMB Software', scope: 'Global' },
  ],
  connectors: {
    composioGoogle: { key: 'composio-google', transport: 'MCP', mode: 'READ_FIRST' },
    github: { key: 'github', mode: 'APPROVAL_GATED' },
    n8n: { key: 'n8n', mode: 'MISSION_GATED' },
    postiz: { key: 'postiz', mode: 'APPROVAL_GATED' },
  },
} as const
