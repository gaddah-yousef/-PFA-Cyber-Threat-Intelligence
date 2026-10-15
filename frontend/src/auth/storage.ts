export type Role = 'admin' | 'analyst' | 'viewer'

export interface AuthState {
  token: string | null
  email: string | null
  role: Role | null
}

const STORAGE_KEY = 'pme_cyber_auth'
const EMPTY_STATE: AuthState = { token: null, email: null, role: null }

export function readStoredAuth(): AuthState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return EMPTY_STATE
    return { ...EMPTY_STATE, ...JSON.parse(raw) }
  } catch {
    return EMPTY_STATE
  }
}

export function writeStoredAuth(state: AuthState): void {
  if (state.token) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } else {
    localStorage.removeItem(STORAGE_KEY)
  }
}

export function getStoredToken(): string | null {
  return readStoredAuth().token
}
