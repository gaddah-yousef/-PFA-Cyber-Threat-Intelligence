export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'

export interface Threat {
  id: string
  indicator: string
  indicator_type: 'ip' | 'domain' | 'url' | 'cve' | 'hash'
  threat_type: string
  source: string
  severity: RiskLevel
  risk_score: number
  risk_level: RiskLevel
  description: string
  recommended_action: string
  cvss_score?: number | null
  epss_score?: number | null
  epss_percentile?: number | null
  epss_updated_at?: string | null
  known_exploited: boolean
  kev_date_added?: string | null
  kev_due_date?: string | null
  kev_required_action?: string | null
  kev_ransomware_use?: string | null
  first_seen: string
  last_seen: string
  created_at: string
}

export type AssetType = 'server' | 'workstation' | 'network_device' | 'application' | 'cloud_resource' | 'other'
export type AssetEnvironment = 'production' | 'development' | 'testing'
export type AssetCriticality = 'low' | 'medium' | 'high' | 'critical'
export type MatchingStatus = 'confirmed' | 'potential' | 'not_affected'

export interface Asset {
  id: string
  hostname: string
  ip_address: string | null
  asset_type: AssetType
  operating_system: string
  environment: AssetEnvironment
  criticality: AssetCriticality
  internet_exposed: boolean
  owner: string | null
  description: string | null
  software_count: number
  confirmed_vulnerabilities: number
  potential_vulnerabilities: number
  created_at: string
  updated_at: string
}

export interface AssetInput {
  hostname: string
  ip_address?: string | null
  asset_type: AssetType
  operating_system: string
  environment: AssetEnvironment
  criticality: AssetCriticality
  internet_exposed: boolean
  owner?: string | null
  description?: string | null
}

export interface AssetStats {
  total: number
  critical: number
  internet_exposed: number
  with_confirmed_vulnerabilities: number
  requiring_verification: number
}

export interface Software {
  id: string
  asset_id: string
  name: string
  vendor: string | null
  version: string
  cpe: string | null
  purl: string | null
  created_at: string
  updated_at: string
}

export interface SoftwareInput {
  name: string
  vendor?: string | null
  version: string
  cpe?: string | null
  purl?: string | null
}

export interface AssetVulnerability {
  id: string
  asset_id: string
  software_id: string
  threat_id: string
  cve_id: string
  software_name: string
  software_version: string
  matching_status: MatchingStatus
  matching_reason: string
  matching_evidence: Record<string, unknown>
  remediation_status: string
  risk_score: number
  risk_level: RiskLevel
  first_detected_at: string
  last_checked_at: string
}

export interface AssetImportReport {
  created: number
  skipped: number
  error_count: number
  errors: Array<{ row: number; message: string }>
}

export type AlertStatus = 'new' | 'investigating' | 'resolved' | 'false_positive'

export interface Alert {
  id: string
  threat_id: string | null
  level: 'high' | 'critical'
  title: string
  message: string
  channel: string
  acknowledged: boolean
  status: AlertStatus
  assigned_to: string | null
  resolution_notes: string | null
  created_at: string
  updated_at: string
}

export interface AlertUpdateInput {
  status?: AlertStatus
  assigned_to?: string | null
  resolution_notes?: string | null
}

export interface SiemEvent {
  schema_version: string
  event_type: string
  generated_at: string
  alert: {
    id: string
    level: string
    status: AlertStatus
    title: string
    message: string
    assigned_to: string | null
    acknowledged: boolean
    created_at: string
  }
  threat: {
    id: string
    indicator: string
    indicator_type: string
    threat_type: string
    source: string
    severity: string
    risk_score: number
    risk_level: string
    description: string
    first_seen: string
    last_seen: string
  }
  recommended_action: string
}

export interface RiskBreakdown {
  score: number
  level: RiskLevel
  factors: Record<string, number>
}

export interface AuditLog {
  id: string
  actor_email: string
  actor_role: string
  action: string
  target_type: string | null
  target_id: string | null
  details: string | null
  created_at: string
}

export interface Stats {
  total: number
  critical: number
  high: number
  medium: number
  low: number
  alerts: number
}

export interface ReflexSheet {
  title: string
  summary: string
  priority: 'critique' | 'élevée' | 'modérée'
  owner: string
  reviewed_at: string
  actions: string[]
  sections: Array<{
    title: string
    timeframe: string
    actions: string[]
  }>
  evidence_to_preserve: string[]
  escalation_criteria: string[]
  do_not: string[]
  references: Array<{
    label: string
    url: string
  }>
}

export interface Collector {
  name: string
  requires_api_key: boolean
  configured: boolean
  threat_count: number
  last_collected_at: string | null
}

export interface LoginResponse {
  access_token: string
  token_type: string
  role: 'admin' | 'analyst' | 'viewer'
  email: string
}

export type UserRole = 'admin' | 'analyst' | 'viewer'

export interface User {
  id: string
  email: string
  role: UserRole
  is_active: boolean
  created_at: string
}

export interface UserCreateInput {
  email: string
  password: string
  role: UserRole
}
