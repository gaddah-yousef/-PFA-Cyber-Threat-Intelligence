import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as client from '../api/client'
import type { ReflexSheet } from '../types'
import { ReflexSheets } from './ReflexSheets'

vi.mock('../api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/client')>()
  return { ...actual, getReflexSheets: vi.fn() }
})

const detailedSheet = {
  title: 'Réagir à une campagne de phishing',
  summary: 'Limiter la compromission des comptes et des postes.',
  priority: 'élevée',
  owner: 'Responsable informatique',
  actions: ['Bloquer le domaine', 'Alerter les collaborateurs'],
  sections: [
    { title: 'Actions immédiates', timeframe: '0–15 min', actions: ['Conserver le message original.'] },
    { title: 'Qualification', timeframe: '15–60 min', actions: ['Identifier les destinataires.'] },
    { title: 'Retour à la normale', timeframe: 'Après confinement', actions: ['Renforcer la MFA.'] },
  ],
  evidence_to_preserve: ['Message original au format EML.'],
  escalation_criteria: ['Un mot de passe a été saisi.'],
  do_not: ['Ne pas supprimer le message avant sa conservation.'],
  references: [{ label: 'Guide officiel', url: 'https://example.test/guide' }],
}

describe('ReflexSheets', () => {
  beforeEach(() => {
    vi.mocked(client.getReflexSheets).mockResolvedValue({
      phishing: detailedSheet as unknown as ReflexSheet,
      data_breach: {
        ...detailedSheet,
        title: 'Réagir à une fuite de données',
        priority: 'critique',
      } as unknown as ReflexSheet,
    })
  })

  it('présente une procédure chronologique avec preuves, escalade et références', async () => {
    render(<ReflexSheets />)

    expect(await screen.findByRole('heading', { name: 'Réagir à une campagne de phishing' })).toBeInTheDocument()
    expect(screen.getByText('0–15 min')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Éléments à préserver' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Quand escalader ?' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Guide officiel' })).toHaveAttribute('href', 'https://example.test/guide')
  })

  it('permet de sélectionner une autre procédure', async () => {
    render(<ReflexSheets />)

    const dataBreachButton = await screen.findByRole('button', { name: /Fuite de données/i })
    await userEvent.click(dataBreachButton)

    expect(screen.getByRole('heading', { name: 'Réagir à une fuite de données' })).toBeInTheDocument()
  })
})
