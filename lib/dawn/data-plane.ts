import { DAWN_CONFIG } from './config'

export const DAWN_TENANT_KEY = DAWN_CONFIG.tenant.key
export const QDRANT_COLLECTION = process.env.QDRANT_COLLECTION ?? 'dawn_v4_deus_intus'

export type DawmSafetyState = {
  dataPlaneStatus: string
  writeMode: string
  connectorState: string
}

export function getDawnSafetyState(): DawmSafetyState {
  return {
    dataPlaneStatus: DAWN_CONFIG.dataPlane.status,
    writeMode: DAWN_CONFIG.dataPlane.writeMode,
    connectorState: DAWN_CONFIG.connectorState,
  }
}

export function canPerformExternalWrite(): boolean {
  return DAWN_CONFIG.dataPlane.writeMode !== 'STAGING_ONLY'
}

export const DAWN_SQL = {
  crmAccounts: 'SELECT * FROM crm_accounts WHERE tenant_key = $1 ORDER BY last_seen_at DESC',
  crmOpportunities: 'SELECT * FROM crm_opportunities WHERE tenant_key = $1 ORDER BY last_activity_at DESC',
  sectorSignals: 'SELECT * FROM sector_signals WHERE tenant_key = $1 ORDER BY observed_at DESC LIMIT $2',
  ingestQueue: 'SELECT * FROM ingest_queue WHERE tenant_key = $1 ORDER BY received_at DESC LIMIT $2',
  evidence: 'SELECT * FROM evidence WHERE tenant_key = $1 ORDER BY captured_at DESC LIMIT $2',
  dataProducts: 'SELECT * FROM data_products WHERE tenant_key = $1 ORDER BY updated_at DESC LIMIT $2',
} as const
