import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as client from '../api/client'
import { AuthProvider } from '../auth/AuthContext'
import { AssetDetails } from './AssetDetails'

vi.mock('../api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/client')>()
  return { ...actual, getAsset: vi.fn(), getAssetSoftware: vi.fn(), getAssetVulnerabilities: vi.fn(), createAssetSoftware: vi.fn() }
})

describe('AssetDetails', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.setItem('pme_cyber_auth', JSON.stringify({ token: 'token', email: 'analyst@test.local', role: 'analyst' }))
    vi.mocked(client.getAsset).mockResolvedValue({
      id: 'asset-1', hostname: 'srv-web-01', ip_address: '192.0.2.10', asset_type: 'server', operating_system: 'Ubuntu 24.04',
      environment: 'production', criticality: 'critical', internet_exposed: true, owner: 'IT', description: null,
      software_count: 1, confirmed_vulnerabilities: 1, potential_vulnerabilities: 0,
      created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
    })
    vi.mocked(client.getAssetSoftware).mockResolvedValue([{ id: 'soft-1', asset_id: 'asset-1', name: 'Widget Server', vendor: 'Acme', version: '2.5.0', cpe: null, purl: null, created_at: '', updated_at: '' }])
    vi.mocked(client.getAssetVulnerabilities).mockResolvedValue([{ id: 'match-1', asset_id: 'asset-1', software_id: 'soft-1', threat_id: 't1', cve_id: 'CVE-2026-10001', software_name: 'Widget Server', software_version: '2.5.0', matching_status: 'confirmed', matching_reason: 'CPE et version correspondent.', matching_evidence: {}, remediation_status: 'open', risk_score: 84, risk_level: 'high', first_detected_at: '', last_checked_at: '' }])
  })

  it('explique le lien entre logiciel et CVE et permet d’ajouter un logiciel', async () => {
    vi.mocked(client.createAssetSoftware).mockResolvedValue({ id: 'soft-2', asset_id: 'asset-1', name: 'Nginx', vendor: 'F5', version: '1.26.0', cpe: null, purl: null, created_at: '', updated_at: '' })
    render(<MemoryRouter initialEntries={['/assets/asset-1']}><AuthProvider><Routes><Route path="/assets/:id" element={<AssetDetails />} /></Routes></AuthProvider></MemoryRouter>)
    expect(await screen.findByText('CVE-2026-10001')).toBeInTheDocument()
    expect(screen.getByText(/CPE et version correspondent/i)).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /ajouter un logiciel/i }))
    await userEvent.type(screen.getByLabelText(/^nom du logiciel/i), 'Nginx')
    await userEvent.type(screen.getByLabelText(/^version/i), '1.26.0')
    await userEvent.click(screen.getByRole('button', { name: /enregistrer le logiciel/i }))
    await waitFor(() => expect(client.createAssetSoftware).toHaveBeenCalledWith('asset-1', expect.objectContaining({ name: 'Nginx', version: '1.26.0' })))
  })
})
