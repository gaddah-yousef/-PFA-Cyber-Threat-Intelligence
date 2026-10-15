import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { RiskBadge } from './RiskBadge'

describe('RiskBadge', () => {
  it('affiche le libellé français correspondant au niveau de risque', () => {
    render(<RiskBadge level="critical" />)
    expect(screen.getByText('Critique')).toBeInTheDocument()
  })

  it.each([
    ['low', 'Faible'],
    ['medium', 'Moyen'],
    ['high', 'Élevé'],
  ] as const)('mappe %s vers %s', (level, label) => {
    render(<RiskBadge level={level} />)
    expect(screen.getByText(label)).toBeInTheDocument()
  })
})
