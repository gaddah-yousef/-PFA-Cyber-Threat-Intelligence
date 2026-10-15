import type { LucideIcon } from 'lucide-react'

interface Props {
  label: string
  value: number
  icon: LucideIcon
  tone: string
  caption: string
  eyebrow: string
}

export function StatCard({ label, value, icon: Icon, tone, caption, eyebrow }: Props) {
  return (
    <article className="rounded-xl border border-slate-200/80 bg-white p-5">
      <div className="mb-5 flex items-start justify-between gap-3">
        <div className={`rounded-lg p-2.5 ${tone}`}><Icon className="h-5 w-5" /></div>
        <span className="text-right text-[11px] font-semibold uppercase tracking-wider text-slate-400">{eyebrow}</span>
      </div>
      <p className="text-sm font-semibold text-slate-500">{label}</p>
      <p className="mt-1 text-3xl font-black tracking-tight text-ink">{value}</p>
      <p className="mt-2 text-xs leading-relaxed text-slate-400">{caption}</p>
    </article>
  )
}
