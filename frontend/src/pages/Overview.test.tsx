import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as client from '../api/client'
import { Overview } from './Overview'

vi.mock('../api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/client')>()
  return {
    ...actual,
    getStats: vi.fn(),
    getThreats: vi.fn(),
    getAlerts: vi.fn(),
  }
})

describe('Overview', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(client.getStats).mockResolvedValue({
      total: 1519,
      critical: 56,
      high: 996,
      medium: 467,
      low: 0,
      alerts: 1053,
    })
    vi.mocked(client.getThreats).mockResolvedValue([])
    vi.mocked(client.getAlerts).mockResolvedValue([])
  })

  it('affiche le visuel cyber du dashboard et permet d’arrêter son animation', async () => {
    render(
      <MemoryRouter>
        <Overview />
      </MemoryRouter>,
    )

    const visual = await screen.findByRole('img', {
      name: /analyse visuelle d’une cartographie de cybermenaces/i,
    })
    expect(visual).toHaveAttribute('src', '/images/login/threat-analysis.jpg')

    const motionControl = screen.getByRole('button', {
      name: /désactiver l’animation du fond/i,
    })
    expect(motionControl).toHaveAttribute('aria-pressed', 'true')

    await userEvent.click(motionControl)

    expect(motionControl).toHaveAttribute('aria-pressed', 'false')
    expect(motionControl).toHaveAccessibleName(/activer l’animation du fond/i)
  })
})
