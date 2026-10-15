import type { RiskLevel } from '../types'

const styles: Record<RiskLevel, string> = {
  critical: 'bg-red-50 text-red-700 ring-red-200',
  high: 'bg-orange-50 text-orange-700 ring-orange-200',
  medium: 'bg-amber-50 text-amber-700 ring-amber-200',
  low: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
}

const labels: Record<RiskLevel, string> = {
  critical: 'Critique',
  high: 'Élevé',
  medium: 'Moyen',
  low: 'Faible',
}

export function RiskBadge({ level }: { level: RiskLevel }) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold ring-1 ring-inset ${styles[level]}`}>
      {labels[level]}
    </span>
  )
}
