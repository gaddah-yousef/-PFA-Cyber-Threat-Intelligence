import { render, screen } from '@testing-library/react'
import { ShieldAlert } from 'lucide-react'
import { describe, expect, it } from 'vitest'
import { StatCard } from './StatCard'

describe('StatCard', () => {
  it('affiche le libellé, la valeur et la légende', () => {
    render(
      <StatCard
        label="Critiques"
        value={7}
        icon={ShieldAlert}
        tone="bg-red-50 text-red-600"
        caption="Action immédiate requise"
        eyebrow="Priorité 1"
      />,
    )
    expect(screen.getByText('Critiques')).toBeInTheDocument()
    expect(screen.getByText('7')).toBeInTheDocument()
    expect(screen.getByText('Action immédiate requise')).toBeInTheDocument()
    expect(screen.getByText('Priorité 1')).toBeInTheDocument()
  })
})
