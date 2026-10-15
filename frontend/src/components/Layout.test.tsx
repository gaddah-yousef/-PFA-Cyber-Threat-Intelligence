import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthContext'
import { getCollectors } from '../api/client'
import { Layout } from './Layout'

vi.mock('../api/client', () => ({
  getCollectors: vi.fn(),
  login: vi.fn(),
}))

const mockedGetCollectors = vi.mocked(getCollectors)

describe('Layout', () => {
  beforeEach(() => {
    localStorage.setItem('pme_cyber_auth', JSON.stringify({
      token: 'test-token',
      email: 'analyste@test.local',
      role: 'analyst',
    }))
  })

  it('affiche la derniere collecte reelle et les sources a configurer', async () => {
    mockedGetCollectors.mockResolvedValue([
      {
        name: 'nvd',
        requires_api_key: true,
        configured: true,
        threat_count: 40,
        last_collected_at: '2026-10-06T14:30:00Z',
      },
      {
        name: 'urlhaus',
        requires_api_key: true,
        configured: false,
        threat_count: 0,
        last_collected_at: null,
      },
    ])

    render(
      <MemoryRouter>
        <AuthProvider>
          <Routes>
            <Route element={<Layout />}>
              <Route index element={<p>Contenu</p>} />
            </Route>
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    )

    expect(await screen.findByText(/1 source à configurer/i)).toBeInTheDocument()
    expect(screen.getByText(/06\/10\/2026/)).toBeInTheDocument()
    expect(screen.queryByText(/a l'instant/i)).not.toBeInTheDocument()
  })
})
