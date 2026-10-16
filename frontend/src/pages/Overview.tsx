import { useEffect, useState, type PointerEvent as ReactPointerEvent } from 'react'
import { Link } from 'react-router-dom'
import { AlertTriangle, ArrowRight, BellRing, Pause, Play, Radar, ShieldAlert, ShieldCheck } from 'lucide-react'
import { getAlerts, getStats, getThreats } from '../api/client'
import { ErrorState, LoadingState } from '../components/StateViews'
import { RiskBadge } from '../components/RiskBadge'
import { StatCard } from '../components/StatCard'
import type { Alert, Stats, Threat } from '../types'

const ALERT_LEVELS = { critical: 'Critique', high: 'Élevée' }

export function Overview() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [threats, setThreats] = useState<Threat[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [error, setError] = useState(false)
  const [motionEnabled, setMotionEnabled] = useState(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return true
    return !window.matchMedia('(prefers-reduced-motion: reduce)').matches
  })

  useEffect(() => {
    Promise.all([getStats(), getThreats(), getAlerts()])
      .then(([statsData, threatsData, alertsData]) => {
        setStats(statsData)
        setThreats(threatsData.slice(0, 5))
        setAlerts(alertsData.slice(0, 3))
      })
      .catch(() => setError(true))
  }, [])

  if (error) return <ErrorState />
  if (!stats) return <LoadingState />

  const hasUrgentThreats = stats.critical > 0

  const moveHero = (event: ReactPointerEvent<HTMLElement>) => {
    if (!motionEnabled || event.pointerType === 'touch') return
    const bounds = event.currentTarget.getBoundingClientRect()
    const x = ((event.clientX - bounds.left) / bounds.width - 0.5) * 14
    const y = ((event.clientY - bounds.top) / bounds.height - 0.5) * 14
    event.currentTarget.style.setProperty('--overview-x', `${x}px`)
    event.currentTarget.style.setProperty('--overview-y', `${y}px`)
  }

  const resetHero = (event: ReactPointerEvent<HTMLElement>) => {
    event.currentTarget.style.setProperty('--overview-x', '0px')
    event.currentTarget.style.setProperty('--overview-y', '0px')
  }

  return (
    <div className="space-y-7">
      <section
        className={`overview-hero relative isolate min-h-[17rem] overflow-hidden rounded-2xl bg-ink text-white shadow-[0_24px_55px_rgba(24,35,31,0.14)] ${motionEnabled ? '' : 'overview-hero--paused'}`}
        onPointerMove={moveHero}
        onPointerLeave={resetHero}
      >
        <img
          src="/images/login/threat-analysis.jpg"
          alt="Analyse visuelle d’une cartographie de cybermenaces"
          className="overview-hero-image absolute inset-0 h-full w-full object-cover"
        />
        <div className="overview-hero-shade absolute inset-0" aria-hidden="true" />
        <div className="overview-hero-scan absolute inset-y-0 left-0 w-px" aria-hidden="true" />

        <div className="overview-hero-content relative z-10 grid min-h-[17rem] gap-8 p-6 sm:p-8 lg:grid-cols-[1fr_auto] lg:items-end lg:p-10">
          <div className="max-w-3xl self-center">
            <div className="mb-4 flex items-center gap-2.5">
              <span className="relative flex h-2.5 w-2.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-lime opacity-50" />
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-lime" />
              </span>
              <p className="text-[11px] font-black uppercase tracking-[0.22em] text-lime">Centre de veille · Surveillance active</p>
            </div>
            <h1 className="text-balance max-w-3xl text-3xl font-black tracking-tight sm:text-4xl lg:text-[2.7rem] lg:leading-[1.08]">
              Bonjour. Voici ce qui demande votre attention.
            </h1>
            <p className="mt-4 max-w-2xl text-sm leading-relaxed text-slate-200 sm:text-base">
              Sentinel PME regroupe les signaux utiles et les classe pour vous aider à décider quoi traiter en premier.
            </p>
            <Link to="/threats" className="group mt-6 inline-flex items-center justify-center gap-2 rounded-lg bg-lime px-5 py-3 text-sm font-black text-ink transition duration-300 hover:-translate-y-0.5 hover:bg-white hover:shadow-xl">
              Voir les menaces <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </div>

          <div className="flex items-end justify-between gap-4 lg:flex-col lg:items-end">
            <div className="min-w-[11rem] rounded-xl border border-white/15 bg-black/20 px-4 py-3 backdrop-blur-md">
              <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-300">Priorité actuelle</p>
              <p className="mt-1 text-3xl font-black text-white">{stats.critical}</p>
              <p className="text-xs text-slate-300">menaces critiques à qualifier</p>
            </div>
            <button
              type="button"
              aria-pressed={motionEnabled}
              aria-label={motionEnabled ? 'Désactiver l’animation du fond' : 'Activer l’animation du fond'}
              onClick={() => setMotionEnabled((enabled) => !enabled)}
              className="inline-flex h-10 items-center gap-2 rounded-full border border-white/20 bg-black/20 px-3 text-xs font-bold text-white/90 backdrop-blur-md transition hover:border-lime hover:text-lime"
            >
              {motionEnabled ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
              <span className="hidden sm:inline">Animation</span>
            </button>
          </div>
        </div>
      </section>

      <section
        className={`flex flex-col gap-2 rounded-xl border px-4 py-3 text-sm sm:flex-row sm:items-center sm:justify-between ${hasUrgentThreats ? 'border-red-200 bg-red-50 text-red-900' : 'border-emerald/20 bg-mint/60 text-emerald'}`}
        aria-label="Résumé prioritaire"
      >
        <p className="font-semibold">
          {hasUrgentThreats
            ? `${stats.critical} menace${stats.critical > 1 ? 's critiques' : ' critique'} à vérifier maintenant.`
            : 'Aucune menace critique en attente. Continuez la surveillance.'}
        </p>
        <Link to="/alerts" className="inline-flex items-center gap-1 font-bold underline-offset-4 hover:underline">
          Ouvrir les alertes <ArrowRight className="h-4 w-4" />
        </Link>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard label="Menaces suivies" value={stats.total} icon={Radar} tone="bg-mint text-emerald" caption="Tous les indicateurs collectés" eyebrow="Total" />
        <StatCard label="Critiques" value={stats.critical} icon={ShieldAlert} tone="bg-red-50 text-red-600" caption="À vérifier immédiatement" eyebrow="Priorité 1" />
        <StatCard label="Élevées" value={stats.high} icon={AlertTriangle} tone="bg-orange-50 text-orange-600" caption="À traiter dans la journée" eyebrow="À traiter" />
        <StatCard label="Moyennes" value={stats.medium} icon={ShieldCheck} tone="bg-amber-50 text-amber-600" caption="À garder sous surveillance" eyebrow="Suivi" />
        <StatCard label="Alertes" value={stats.alerts} icon={BellRing} tone="bg-violet-50 text-violet-600" caption="Dans la file de traitement" eyebrow="File SOC" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.6fr_1fr]">
        <div className="overflow-hidden rounded-xl border border-slate-200/80 bg-white">
          <div className="flex items-center justify-between border-b border-slate-100 px-6 py-5">
            <div>
              <h2 className="font-black">Derniers indicateurs</h2>
              <p className="text-xs text-slate-400">Les signaux les plus récemment observés</p>
            </div>
            <Link to="/threats" className="text-sm font-bold text-emerald hover:underline">Tout voir</Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[620px] text-left text-sm">
              <thead className="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-400">
                <tr><th className="px-6 py-3">Indicateur</th><th className="px-4 py-3">Source</th><th className="px-4 py-3">Risque</th><th className="px-6 py-3 text-right">Score</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {threats.map((threat) => (
                  <tr key={threat.id} className="transition hover:bg-slate-50">
                    <td className="max-w-xs px-6 py-4">
                      <Link to={`/threats/${threat.id}`} className="block truncate font-bold text-ink hover:text-emerald">{threat.indicator}</Link>
                      <span className="text-xs uppercase text-slate-400">{threat.indicator_type} · {threat.threat_type.replace('_', ' ')}</span>
                    </td>
                    <td className="px-4 py-4 text-xs font-bold uppercase text-slate-500">{threat.source}</td>
                    <td className="px-4 py-4"><RiskBadge level={threat.risk_level} /></td>
                    <td className="px-6 py-4 text-right text-lg font-black">{threat.risk_score}</td>
                  </tr>
                ))}
                {!threats.length && (
                  <tr><td colSpan={4} className="px-6 py-10 text-center text-sm text-slate-400">Aucun indicateur collecté pour le moment.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded-xl bg-ink p-6 text-white">
          <div className="mb-6 flex items-start justify-between">
            <div><p className="text-xs font-black uppercase tracking-widest text-lime">À traiter</p><h2 className="mt-1 text-xl font-black">Alertes récentes</h2></div>
            <BellRing className="text-lime" />
          </div>
          <div className="space-y-3">
            {alerts.length ? alerts.map((alert) => (
              <div key={alert.id} className="rounded-lg border border-white/10 bg-white/5 p-4">
                <div className="mb-2 flex items-center justify-between gap-3">
                  <span className={`text-xs font-black uppercase ${alert.level === 'critical' ? 'text-red-300' : 'text-orange-300'}`}>{ALERT_LEVELS[alert.level]}</span>
                  <span className="text-[11px] text-slate-400">{new Date(alert.created_at).toLocaleDateString('fr-FR')}</span>
                </div>
                <p className="line-clamp-2 text-sm leading-relaxed text-slate-300">{alert.message}</p>
              </div>
            )) : <p className="rounded-lg border border-white/10 p-4 text-sm text-slate-400">Aucune alerte en attente.</p>}
          </div>
          <Link to="/alerts" className="mt-5 flex items-center justify-center gap-2 rounded-lg bg-lime px-4 py-3 text-sm font-black text-ink hover:bg-white">
            Ouvrir le centre d’alertes <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>
    </div>
  )
}
