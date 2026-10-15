import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as client from '../api/client'
import { ThreatDetails } from './ThreatDetails'

vi.mock('../api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/client')>()
  return { ...actual, getThreat: vi.fn(), explainThreat: vi.fn() }
})

describe('ThreatDetails', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(client.getThreat).mockResolvedValue({
      id: 'threat-1', indicator: 'CVE-2026-10001', indicator_type: 'cve', threat_type: 'vulnerability',
      source: 'nvd', severity: 'critical', risk_score: 96, risk_level: 'critical',
      description: 'Critical vulnerability', recommended_action: 'Apply patch', cvss_score: 9.8,
      epss_score: 0.725, epss_percentile: 0.982, epss_updated_at: '2026-10-10T00:00:00Z',
      known_exploited: true, kev_date_added: '2026-10-09', kev_due_date: '2026-10-30',
      kev_required_action: 'Apply mitigations or discontinue use.', kev_ransomware_use: 'Known',
      first_seen: '2026-10-08T00:00:00Z', last_seen: '2026-10-11T00:00:00Z', created_at: '2026-10-11T00:00:00Z',
    })
    vi.mocked(client.explainThreat).mockResolvedValue({
      score: 96, level: 'critical', factors: { known_exploited: 15, epss_likelihood: 10 },
    })
  })

  it('affiche la probabilité EPSS et les consignes CISA KEV', async () => {
    render(
      <MemoryRouter initialEntries={['/threats/threat-1']}>
        <Routes><Route path="/threats/:id" element={<ThreatDetails />} /></Routes>
      </MemoryRouter>,
    )

    expect(await screen.findByText('CVE-2026-10001')).toBeInTheDocument()
    expect(screen.getByText(/exploitation confirmée/i)).toBeInTheDocument()
    expect(screen.getByText('72,5 %')).toBeInTheDocument()
    expect(screen.getByText(/98,2e percentile/i)).toBeInTheDocument()
    expect(screen.getByText('Apply mitigations or discontinue use.')).toBeInTheDocument()
  })
})
