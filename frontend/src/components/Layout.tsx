import { useEffect, useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  BellRing,
  BookOpenCheck,
  CircleHelp,
  Database,
  Gauge,
  LogOut,
  Menu,
  MonitorCog,
  Radar,
  ShieldCheck,
  Users,
  X,
} from 'lucide-react'
import { getCollectors } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import type { Collector } from '../types'

const nav = [
  { to: '/', label: 'Vue d’ensemble', icon: Gauge },
  { to: '/threats', label: 'Menaces', icon: Radar },
  { to: '/alerts', label: 'Alertes', icon: BellRing },
  { to: '/assets', label: 'Parc informatique', icon: MonitorCog },
  { to: '/reflex-sheets', label: 'Fiches réflexes', icon: BookOpenCheck },
  { to: '/sources', label: 'Sources', icon: Database },
  { to: '/users', label: 'Utilisateurs', icon: Users, adminOnly: true },
  { to: '/about', label: 'À propos', icon: CircleHelp },
]

const ROLE_LABELS: Record<string, string> = {
  admin: 'Administrateur',
  analyst: 'Analyste',
  viewer: 'Responsable PME',
}

export function Layout() {
  const [open, setOpen] = useState(false)
  const [collectors, setCollectors] = useState<Collector[] | null>(null)
  const [collectorError, setCollectorError] = useState(false)
  const { email, role, logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    let active = true
    getCollectors()
      .then((data) => {
        if (active) setCollectors(data)
      })
      .catch(() => {
        if (active) setCollectorError(true)
      })
    return () => { active = false }
  }, [])

  const onLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  const initials = (email ?? '?').slice(0, 2).toUpperCase()
  const sourcesToConfigure = collectors?.filter(
    (collector) => collector.requires_api_key && !collector.configured,
  ).length ?? 0
  const activeSources = collectors?.filter((collector) => collector.configured).length ?? 0
  const latestCollection = collectors
    ?.map((collector) => collector.last_collected_at)
    .filter((date): date is string => Boolean(date))
    .sort((a, b) => new Date(b).getTime() - new Date(a).getTime())[0]
  const latestCollectionLabel = latestCollection
    ? new Intl.DateTimeFormat('fr-FR', {
        dateStyle: 'short',
        timeStyle: 'short',
      }).format(new Date(latestCollection))
    : 'aucune collecte'
  const sourceStatus = collectorError
    ? 'État des sources indisponible'
    : collectors
      ? sourcesToConfigure > 0
        ? `${sourcesToConfigure} source${sourcesToConfigure > 1 ? 's' : ''} à configurer · dernière collecte ${latestCollectionLabel}`
        : `Dernière collecte : ${latestCollectionLabel}`
      : 'Vérification des sources…'

  const sidebar = (
    <aside className="flex h-full flex-col bg-ink px-5 py-6 text-white">
      <div className="mb-10 flex items-center justify-between">
        <NavLink to="/" className="flex items-center gap-3" onClick={() => setOpen(false)}>
          <span className="grid h-11 w-11 place-items-center rounded-xl bg-lime text-ink">
            <ShieldCheck className="h-6 w-6" strokeWidth={2.5} />
          </span>
          <span>
            <strong className="block text-base">Sentinel PME</strong>
            <small className="text-xs text-slate-400">Veille cyber simplifiée</small>
          </span>
        </NavLink>
        <button className="lg:hidden" onClick={() => setOpen(false)} aria-label="Fermer le menu"><X /></button>
      </div>
      <p className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">Surveillance</p>
      <nav className="space-y-1" aria-label="Navigation principale">
        {nav.filter((item) => !item.adminOnly || role === 'admin').map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            onClick={() => setOpen(false)}
            className={({ isActive }) => `flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-semibold transition ${isActive ? 'bg-white/10 text-lime' : 'text-slate-300 hover:bg-white/5 hover:text-white'}`}
          >
            <Icon className="h-5 w-5" /> {label}
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto rounded-xl border border-white/10 bg-white/5 p-4">
        <div className="mb-2 flex items-center gap-2 text-sm font-bold text-mint">
          <span className={`h-2 w-2 rounded-full ${collectorError ? 'bg-amber-400' : 'bg-lime'}`} />
          Surveillance active
        </div>
        <p className="text-xs leading-relaxed text-slate-400">
          {collectors
            ? `${activeSources} source${activeSources > 1 ? 's' : ''} prête${activeSources > 1 ? 's' : ''} à collecter.`
            : 'Connexion aux sources en cours.'}
        </p>
      </div>
    </aside>
  )

  return (
    <div className="min-h-screen bg-canvas text-ink">
      <div className="fixed inset-y-0 left-0 hidden w-64 lg:block">{sidebar}</div>
      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button className="absolute inset-0 bg-black/50" onClick={() => setOpen(false)} aria-label="Fermer le menu" />
          <div className="relative h-full w-72">{sidebar}</div>
        </div>
      )}
      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200/70 bg-canvas/90 px-5 backdrop-blur md:px-8">
          <button className="rounded-lg p-2 lg:hidden" onClick={() => setOpen(true)} aria-label="Ouvrir le menu"><Menu /></button>
          <div className="hidden min-w-0 items-center gap-2 text-sm text-slate-500 sm:flex" role="status" title={sourceStatus}>
            <span className={`h-2 w-2 shrink-0 rounded-full ${collectorError || sourcesToConfigure > 0 ? 'bg-amber-500' : 'bg-emerald'}`} />
            <span className="truncate">{sourceStatus}</span>
          </div>
          <div className="ml-auto flex items-center gap-3">
            <div className="hidden text-right sm:block">
              <p className="text-xs font-bold leading-tight">{email}</p>
              <p className="text-[11px] leading-tight text-slate-400">{role ? ROLE_LABELS[role] : ''}</p>
            </div>
            <div className="grid h-9 w-9 place-items-center rounded-full bg-ink text-xs font-bold text-white">{initials}</div>
            <button
              onClick={onLogout}
              aria-label="Se déconnecter"
              title="Se déconnecter"
              className="grid h-9 w-9 place-items-center rounded-full border border-slate-200 text-slate-500 transition hover:bg-slate-50 hover:text-red-600"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </header>
        <main className="mx-auto max-w-[1500px] p-5 md:p-8"><Outlet /></main>
      </div>
    </div>
  )
}
