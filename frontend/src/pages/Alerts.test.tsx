import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as client from '../api/client'
import { AuthProvider } from '../auth/AuthContext'
import { Alerts } from './Alerts'

vi.mock('../api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/client')>()
  return { ...actual, getAlerts: vi.fn(), acknowledgeAlert: vi.fn(), createTestAlert: vi.fn() }
})

const sampleAlert = {
  id: 'a1',
  threat_id: 't1',
  level: 'critical' as const,
  title: 'Menace critique détectée',
  message: 'exemple',
  channel: 'dashboard',
  acknowledged: false,
  status: 'new' as const,
  assigned_to: null,
  resolution_notes: null,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}

describe('Alerts', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.setItem(
      'pme_cyber_auth',
      JSON.stringify({ token: 'token', email: 'admin@pme-cyber.local', role: 'admin' }),
    )
  })

  it('permet à un analyste/admin d’acquitter une alerte non traitée', async () => {
    vi.mocked(client.getAlerts).mockResolvedValue([sampleAlert])
    vi.mocked(client.acknowledgeAlert).mockResolvedValue({ ...sampleAlert, acknowledged: true })

    render(
      <AuthProvider>
        <Alerts />
      </AuthProvider>,
    )

    expect(await screen.findByText('Menace critique détectée')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /acquitter/i }))

    await waitFor(() => expect(client.acknowledgeAlert).toHaveBeenCalledWith('a1'))
  })

  it('masque les actions d’écriture pour le rôle responsable PME (viewer)', async () => {
    localStorage.setItem(
      'pme_cyber_auth',
      JSON.stringify({ token: 'token', email: 'pme@example.com', role: 'viewer' }),
    )
    vi.mocked(client.getAlerts).mockResolvedValue([sampleAlert])

    render(
      <AuthProvider>
        <Alerts />
      </AuthProvider>,
    )

    expect(await screen.findByText('Menace critique détectée')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /acquitter/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /alerte test/i })).not.toBeInTheDocument()
  })
})
