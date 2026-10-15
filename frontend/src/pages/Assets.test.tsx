import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as client from '../api/client'
import { AuthProvider } from '../auth/AuthContext'
import { Assets } from './Assets'

vi.mock('../api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/client')>()
  return {
    ...actual,
    getAssetsPage: vi.fn(),
    getAssetStats: vi.fn(),
    createAsset: vi.fn(),
    importAssetsCsv: vi.fn(),
  }
})

const asset = {
  id: 'asset-1', hostname: 'srv-web-01', ip_address: '192.0.2.10', asset_type: 'server',
  operating_system: 'Ubuntu 24.04', environment: 'production', criticality: 'critical',
  internet_exposed: true, owner: 'Infrastructure', description: null, software_count: 2,
  confirmed_vulnerabilities: 1, potential_vulnerabilities: 1,
  created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
} as const

describe('Assets', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.setItem('pme_cyber_auth', JSON.stringify({ token: 'token', email: 'admin@test.local', role: 'admin' }))
    vi.mocked(client.getAssetsPage).mockResolvedValue({ items: [asset], total: 1 })
    vi.mocked(client.getAssetStats).mockResolvedValue({ total: 1, critical: 1, internet_exposed: 1, with_confirmed_vulnerabilities: 1, requiring_verification: 1 })
  })

  it('présente les actifs et leurs indicateurs de risque', async () => {
    render(<MemoryRouter><AuthProvider><Assets /></AuthProvider></MemoryRouter>)
    expect(await screen.findByText('srv-web-01')).toBeInTheDocument()
    expect(screen.getByText('Ubuntu 24.04')).toBeInTheDocument()
    expect(screen.getByText('1 confirmée')).toBeInTheDocument()
  })

  it('crée un actif avec un formulaire explicite', async () => {
    vi.mocked(client.createAsset).mockResolvedValue(asset)
    render(<MemoryRouter><AuthProvider><Assets /></AuthProvider></MemoryRouter>)
    await screen.findByText('srv-web-01')
    await userEvent.click(screen.getByRole('button', { name: /ajouter un actif/i }))
    await userEvent.type(screen.getByLabelText(/nom de l'actif/i), 'srv-db-01')
    await userEvent.type(screen.getByLabelText(/système d'exploitation/i), 'Debian 13')
    await userEvent.click(screen.getByRole('button', { name: /enregistrer l'actif/i }))
    await waitFor(() => expect(client.createAsset).toHaveBeenCalledWith(expect.objectContaining({ hostname: 'srv-db-01', operating_system: 'Debian 13' })))
  })
})
