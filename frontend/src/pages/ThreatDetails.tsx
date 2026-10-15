import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, CalendarClock, Database, ShieldAlert, ShieldCheck, TrendingUp } from 'lucide-react'
import { explainThreat, getThreat } from '../api/client'
import { RiskBadge } from '../components/RiskBadge'
import { ErrorState, LoadingState } from '../components/StateViews'
import type { RiskBreakdown, Threat } from '../types'

const FACTOR_LABELS: Record<string, string> = {
  severity: 'Sévérité de la source',
  indicator_type: 'Type d’indicateur',
  threat_type: 'Type de menace',
  source_reliability: 'Fiabilité de la source',
  cve_bonus: 'Bonus CVE',
  known_exploited: 'Exploitation active connue',
  epss_likelihood: 'Probabilité d’exploitation EPSS',
  targets_smes: 'Cible les PME',
  recency: 'Récence',
  multi_source_corroboration: 'Corroboration multi-sources',
}

const formatProbability = (value: number) => new Intl.NumberFormat('fr-FR', {
  style: 'percent',
  maximumFractionDigits: 1,
}).format(value)

const formatPercentile = (value: number) => `${new Intl.NumberFormat('fr-FR', {
  maximumFractionDigits: 1,
}).format(value * 100)}e percentile`

export function ThreatDetails() {
  const { id = '' } = useParams()
  const [threat, setThreat] = useState<Threat | null>(null)
  const [breakdown, setBreakdown] = useState<RiskBreakdown | null>(null)
  const [error, setError] = useState(false)
  useEffect(() => {
    getThreat(id).then(setThreat).catch(() => setError(true))
    explainThreat(id).then(setBreakdown).catch(() => undefined)
  }, [id])
  if (error) return <ErrorState message="Cette menace est introuvable ou l’API ne répond pas." />
  if (!threat) return <LoadingState />
  const actions = threat.recommended_action.split(' ; ')
  const factorEntries = Object.entries(breakdown?.factors ?? {}).sort((a, b) => b[1] - a[1])
  const hasVulnerabilityIntelligence = threat.indicator_type === 'cve' && (
    threat.epss_score != null || threat.known_exploited
  )
  return <div className="space-y-6">
    <Link to="/threats" className="inline-flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-emerald"><ArrowLeft className="h-4 w-4" /> Retour aux menaces</Link>
    <section className="overflow-hidden rounded-3xl bg-ink p-7 text-white shadow-soft md:p-9"><div className="flex flex-col justify-between gap-6 md:flex-row md:items-start"><div className="min-w-0"><div className="mb-4 flex items-center gap-3"><RiskBadge level={threat.risk_level} /><span className="text-xs font-bold uppercase tracking-widest text-slate-400">{threat.indicator_type} · {threat.source}</span></div><h1 className="break-all text-2xl font-black md:text-4xl">{threat.indicator}</h1><p className="mt-4 max-w-3xl leading-relaxed text-slate-300">{threat.description || 'Aucune description disponible.'}</p></div><div className="shrink-0 rounded-2xl border border-white/10 bg-white/5 p-5 text-center"><p className="text-xs font-bold uppercase tracking-widest text-slate-400">Score de risque</p><p className="mt-1 text-5xl font-black text-lime">{threat.risk_score}</p><p className="text-xs text-slate-400">sur 100</p></div></div><div className="mt-7 h-2 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-lime" style={{ width: `${threat.risk_score}%` }} /></div></section>
    {hasVulnerabilityIntelligence && (
      <section className="rounded-2xl border border-emerald/15 bg-white p-6 shadow-soft">
        <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="flex items-center gap-2 font-black"><ShieldCheck className="h-5 w-5 text-emerald" /> Priorisation de la vulnérabilité</h2>
            <p className="mt-1 text-sm text-slate-500">Probabilité d’exploitation et présence dans le catalogue officiel CISA.</p>
          </div>
          {threat.known_exploited && <span className="rounded-full bg-red-50 px-3 py-1 text-xs font-black uppercase tracking-wide text-red-700 ring-1 ring-red-200">CISA KEV · exploitation confirmée</span>}
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {threat.epss_score != null && (
            <div className="rounded-xl bg-slate-50 p-4">
              <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-slate-500"><TrendingUp className="h-4 w-4 text-emerald" /> Score EPSS</p>
              <p className="mt-2 text-3xl font-black text-ink">{formatProbability(threat.epss_score)}</p>
              {threat.epss_percentile != null && <p className="mt-1 text-sm font-semibold text-slate-500">{formatPercentile(threat.epss_percentile)}</p>}
              <p className="mt-3 text-xs leading-relaxed text-slate-500">Probabilité estimée d’exploitation dans les 30 prochains jours. Ce signal complète le score CVSS.</p>
            </div>
          )}
          {threat.known_exploited && (
            <div className="rounded-xl border border-red-100 bg-red-50/60 p-4">
              <p className="text-xs font-bold uppercase tracking-wide text-red-700">Action prioritaire CISA</p>
              <p className="mt-2 text-sm font-semibold leading-relaxed text-ink">{threat.kev_required_action || 'Appliquer les mesures de réduction recommandées par l’éditeur.'}</p>
              <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-xs text-slate-500">
                {threat.kev_due_date && <span>Échéance : <strong>{new Date(`${threat.kev_due_date}T00:00:00Z`).toLocaleDateString('fr-FR', { timeZone: 'UTC' })}</strong></span>}
                {threat.kev_ransomware_use && <span>Rançongiciel : <strong>{threat.kev_ransomware_use === 'Known' ? 'usage connu' : 'non confirmé'}</strong></span>}
              </div>
            </div>
          )}
        </div>
      </section>
    )}
    <div className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
      <section className="rounded-2xl bg-white p-6 shadow-soft"><h2 className="mb-5 flex items-center gap-2 font-black"><Database className="h-5 w-5 text-emerald" /> Informations techniques</h2><dl className="grid grid-cols-2 gap-4 text-sm"><div><dt className="text-xs text-slate-400">Type de menace</dt><dd className="mt-1 font-bold capitalize">{threat.threat_type.replace('_', ' ')}</dd></div><div><dt className="text-xs text-slate-400">Sévérité source</dt><dd className="mt-1 font-bold capitalize">{threat.severity}</dd></div><div><dt className="text-xs text-slate-400">Première observation</dt><dd className="mt-1 font-bold">{new Date(threat.first_seen).toLocaleString('fr-FR')}</dd></div><div><dt className="text-xs text-slate-400">Dernière observation</dt><dd className="mt-1 font-bold">{new Date(threat.last_seen).toLocaleString('fr-FR')}</dd></div></dl><div className="mt-6 rounded-xl bg-slate-50 p-4 text-xs leading-relaxed text-slate-500"><CalendarClock className="mb-2 h-5 w-5 text-emerald" />Le score combine la sévérité, le type d’indicateur, la menace, la fiabilité de la source, l’exploitation connue, le ciblage PME et la récence.</div></section>
      <section className="rounded-2xl bg-white p-6 shadow-soft"><h2 className="mb-5 flex items-center gap-2 font-black"><ShieldAlert className="h-5 w-5 text-emerald" /> Fiche réflexe recommandée</h2><ol className="space-y-3">{actions.map((action, index) => <li key={action} className="flex gap-3 rounded-xl border border-slate-100 p-3"><span className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-mint text-xs font-black text-emerald">{index + 1}</span><span className="pt-1 text-sm font-semibold">{action}</span></li>)}</ol></section>
    </div>
    {factorEntries.length > 0 && (
      <section className="rounded-2xl bg-white p-6 shadow-soft">
        <h2 className="mb-1 font-black">Pourquoi ce score ?</h2>
        <p className="mb-5 text-sm text-slate-500">
          Détail des points attribués par le moteur de scoring, facteur par facteur.
        </p>
        <div className="space-y-3">
          {factorEntries.map(([factor, points]) => (
            <div key={factor}>
              <div className="mb-1 flex items-center justify-between text-xs font-bold text-slate-500">
                <span>{FACTOR_LABELS[factor] ?? factor}</span>
                <span>{points} pts</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-emerald"
                  style={{ width: `${Math.min(Math.max(points, 0), 50) * 2}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </section>
    )}
  </div>
}
