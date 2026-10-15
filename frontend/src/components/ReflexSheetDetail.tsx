import {
  AlertTriangle,
  Archive,
  ArrowUpRight,
  BookOpenCheck,
  Clock3,
  ShieldAlert,
  UserRound,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import type { ReflexSheet } from '../types'

const PRIORITY_STYLES = {
  critique: 'bg-red-50 text-red-700 border-red-200',
  élevée: 'bg-orange-50 text-orange-700 border-orange-200',
  modérée: 'bg-amber-50 text-amber-700 border-amber-200',
}

interface InfoPanelProps {
  title: string
  items: string[]
  icon: LucideIcon
  tone: 'neutral' | 'warning' | 'danger'
}

const PANEL_STYLES = {
  neutral: 'border-slate-200 bg-slate-50 text-slate-700',
  warning: 'border-amber-200 bg-amber-50 text-amber-900',
  danger: 'border-red-200 bg-red-50 text-red-900',
}

function InfoPanel({ title, items, icon: Icon, tone }: InfoPanelProps) {
  return (
    <section className={`rounded-xl border p-5 ${PANEL_STYLES[tone]}`}>
      <h3 className="flex items-center gap-2 font-black">
        <Icon className="h-5 w-5" aria-hidden="true" /> {title}
      </h3>
      <ul className="mt-4 space-y-3 text-sm leading-relaxed">
        {items.map((item) => (
          <li key={item} className="flex gap-2">
            <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-current opacity-60" aria-hidden="true" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}

export function ReflexSheetDetail({ sheet }: { sheet: ReflexSheet }) {
  const reviewedAt = new Date(`${sheet.reviewed_at}T00:00:00`).toLocaleDateString('fr-FR')

  return (
    <article className="min-w-0 space-y-6" aria-labelledby="reflex-sheet-title">
      <header className="rounded-xl border border-slate-200/80 bg-white p-6 md:p-8">
        <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-start">
          <div className="min-w-0">
            <div className="mb-4 flex flex-wrap items-center gap-3">
              <span className="grid h-11 w-11 place-items-center rounded-lg bg-mint text-emerald">
                <BookOpenCheck className="h-6 w-6" aria-hidden="true" />
              </span>
              <span className={`rounded-full border px-3 py-1 text-xs font-black uppercase tracking-wide ${PRIORITY_STYLES[sheet.priority]}`}>
                Priorité {sheet.priority}
              </span>
            </div>
            <h2 id="reflex-sheet-title" className="text-2xl font-black tracking-tight md:text-3xl">{sheet.title}</h2>
            <p className="mt-3 max-w-3xl text-sm leading-relaxed text-slate-600">{sheet.summary}</p>
          </div>
          <dl className="shrink-0 space-y-2 rounded-lg bg-slate-50 p-4 text-xs text-slate-500 sm:max-w-64">
            <div className="flex gap-2"><UserRound className="h-4 w-4 shrink-0 text-emerald" aria-hidden="true" /><div><dt className="font-bold text-slate-700">Pilote conseillé</dt><dd className="mt-0.5">{sheet.owner}</dd></div></div>
            <div className="flex gap-2"><Clock3 className="h-4 w-4 shrink-0 text-emerald" aria-hidden="true" /><div><dt className="font-bold text-slate-700">Dernière révision</dt><dd className="mt-0.5">{reviewedAt}</dd></div></div>
          </dl>
        </div>
      </header>

      <section aria-labelledby="procedure-title">
        <div className="mb-4">
          <h3 id="procedure-title" className="text-lg font-black">Procédure chronologique</h3>
          <p className="mt-1 text-sm text-slate-500">Commencez par contenir. Conservez les traces avant de nettoyer ou restaurer.</p>
        </div>
        <ol className="grid gap-4 xl:grid-cols-3">
          {sheet.sections.map((section, sectionIndex) => (
            <li key={section.title} className="rounded-xl border border-slate-200/80 bg-white p-5">
              <div className="flex items-start justify-between gap-3">
                <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-ink text-sm font-black text-white">{sectionIndex + 1}</span>
                <span className="rounded-full bg-mint px-2.5 py-1 text-[11px] font-black text-emerald">{section.timeframe}</span>
              </div>
              <h4 className="mt-4 font-black">{section.title}</h4>
              <ul className="mt-4 space-y-3 text-sm leading-relaxed text-slate-600">
                {section.actions.map((action) => (
                  <li key={action} className="flex gap-2">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald" aria-hidden="true" />
                    <span>{action}</span>
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ol>
      </section>

      <div className="grid gap-4 lg:grid-cols-3">
        <InfoPanel title="Éléments à préserver" items={sheet.evidence_to_preserve} icon={Archive} tone="neutral" />
        <InfoPanel title="Quand escalader ?" items={sheet.escalation_criteria} icon={ShieldAlert} tone="warning" />
        <InfoPanel title="À ne pas faire" items={sheet.do_not} icon={AlertTriangle} tone="danger" />
      </div>

      <section className="rounded-xl border border-slate-200/80 bg-white p-5" aria-labelledby="references-title">
        <h3 id="references-title" className="font-black">Références officielles</h3>
        <p className="mt-1 text-xs leading-relaxed text-slate-500">Ces procédures synthétisent des recommandations publiques. Adaptez-les à votre infrastructure et à vos obligations.</p>
        <ul className="mt-4 grid gap-2 md:grid-cols-2">
          {sheet.references.map((reference) => (
            <li key={reference.url}>
              <a href={reference.url} target="_blank" rel="noreferrer" className="flex items-start justify-between gap-3 rounded-lg border border-slate-200 px-3 py-2.5 text-sm font-bold text-slate-700 transition hover:border-emerald hover:text-emerald">
                <span>{reference.label}</span><ArrowUpRight className="h-4 w-4 shrink-0" aria-hidden="true" />
              </a>
            </li>
          ))}
        </ul>
      </section>
    </article>
  )
}
