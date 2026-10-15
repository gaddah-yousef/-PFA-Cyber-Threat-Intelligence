import axios from 'axios'
import { getStoredToken } from '../auth/storage'
import type {
  Alert,
  AlertUpdateInput,
  Asset,
  AssetImportReport,
  AssetInput,
  AssetStats,
  AssetVulnerability,
  AuditLog,
  Collector,
  LoginResponse,
  ReflexSheet,
  RiskBreakdown,
  SiemEvent,
  Stats,
  Software,
  SoftwareInput,
  Threat,
  User,
  UserCreateInput,
} from '../types'

const configuredApiUrl = import.meta.env.VITE_API_URL
const API_BASE_URL = (
  configuredApiUrl !== undefined
    ? configuredApiUrl
    : `${window.location.protocol}//${window.location.hostname}:8000`
).replace(/\/+$/, '')

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.dispatchEvent(new Event('auth:unauthorized'))
    }
    return Promise.reject(error)
  },
)

export const login = async (email: string, password: string) => {
  const form = new URLSearchParams()
  form.set('username', email)
  form.set('password', password)
  const response = await axios.post<LoginResponse>(
    `${API_BASE_URL}/api/auth/login`,
    form,
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } },
  )
  return response.data
}

export const getStats = async () => (await api.get<Stats>('/api/stats')).data
export const getThreats = async (params?: Record<string, string>) =>
  (await api.get<Threat[]>('/api/threats', { params })).data
export const getThreatsPage = async (params?: Record<string, string>) => {
  const response = await api.get<Threat[]>('/api/threats', { params })
  const total = Number(response.headers['x-total-count'] ?? response.data.length)
  return { items: response.data, total }
}
export const getThreat = async (id: string) =>
  (await api.get<Threat>(`/api/threats/${id}`)).data
export const getAlerts = async () => (await api.get<Alert[]>('/api/alerts')).data
export const createTestAlert = async () =>
  (await api.post<Alert>('/api/alerts/test', {})).data
export const acknowledgeAlert = async (id: string) =>
  (await api.patch<Alert>(`/api/alerts/${id}/acknowledge`)).data
export const updateAlert = async (id: string, payload: AlertUpdateInput) =>
  (await api.patch<Alert>(`/api/alerts/${id}`, payload)).data
export const getAlertSiemEvent = async (id: string) =>
  (await api.get<SiemEvent>(`/api/alerts/${id}/siem-event`)).data
export const explainThreat = async (id: string) =>
  (await api.get<RiskBreakdown>(`/api/threats/${id}/explain`)).data
export const getAuditLogs = async () => (await api.get<AuditLog[]>('/api/audit-logs')).data
export const getReflexSheets = async () =>
  (await api.get<Record<string, ReflexSheet>>('/api/reflex-sheets')).data
export const getCollectors = async () =>
  (await api.get<Collector[]>('/api/collectors')).data
export const runCollector = async (name: string) =>
  (await api.post<{ source: string; threats_processed: number }>(`/api/collectors/${name}/run`)).data

export const getAssetsPage = async (params?: Record<string, string | boolean>) => {
  const response = await api.get<Asset[]>('/api/assets', { params })
  return { items: response.data, total: Number(response.headers['x-total-count'] ?? response.data.length) }
}
export const getAssetStats = async () => (await api.get<AssetStats>('/api/assets/stats')).data
export const getAsset = async (id: string) => (await api.get<Asset>(`/api/assets/${id}`)).data
export const createAsset = async (payload: AssetInput) => (await api.post<Asset>('/api/assets', payload)).data
export const updateAsset = async (id: string, payload: Partial<AssetInput>) => (await api.patch<Asset>(`/api/assets/${id}`, payload)).data
export const deleteAsset = async (id: string) => api.delete(`/api/assets/${id}`)
export const importAssetsCsv = async (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return (await api.post<AssetImportReport>('/api/assets/import', form, { headers: { 'Content-Type': 'multipart/form-data' } })).data
}
export const getAssetSoftware = async (id: string) => (await api.get<Software[]>(`/api/assets/${id}/software`)).data
export const createAssetSoftware = async (id: string, payload: SoftwareInput) => (await api.post<Software>(`/api/assets/${id}/software`, payload)).data
export const getAssetVulnerabilities = async (id: string) => (await api.get<AssetVulnerability[]>(`/api/assets/${id}/vulnerabilities`)).data
export const getUsers = async () => (await api.get<User[]>('/api/auth/users')).data
export const createUser = async (payload: UserCreateInput) =>
  (await api.post<User>('/api/auth/users', payload)).data
export const updateUser = async (
  id: string,
  payload: Partial<Pick<User, 'role' | 'is_active'>>,
) => (await api.patch<User>(`/api/auth/users/${id}`, payload)).data

export default api
