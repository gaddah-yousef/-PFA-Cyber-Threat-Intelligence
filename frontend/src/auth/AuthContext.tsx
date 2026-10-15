import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { login as loginRequest } from '../api/client'
import { readStoredAuth, writeStoredAuth, type AuthState, type Role } from './storage'

interface AuthContextValue extends AuthState {
  isAuthenticated: boolean
  canWrite: boolean
  isAdmin: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const EMPTY_STATE: AuthState = { token: null, email: null, role: null }

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<AuthState>(readStoredAuth)

  useEffect(() => {
    writeStoredAuth(auth)
  }, [auth])

  useEffect(() => {
    const handleUnauthorized = () => setAuth(EMPTY_STATE)
    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized)
  }, [])

  const login = async (email: string, password: string) => {
    const data = await loginRequest(email, password)
    setAuth({ token: data.access_token, email: data.email, role: data.role as Role })
  }

  const logout = () => setAuth(EMPTY_STATE)

  const value = useMemo<AuthContextValue>(
    () => ({
      ...auth,
      isAuthenticated: Boolean(auth.token),
      canWrite: auth.role === 'admin' || auth.role === 'analyst',
      isAdmin: auth.role === 'admin',
      login,
      logout,
    }),
    [auth],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth doit être utilisé dans un AuthProvider')
  return ctx
}
