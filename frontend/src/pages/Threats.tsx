import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FilterX, Search, ShieldCheck } from 'lucide-react'
import { getThreatsPage } from '../api/client'
import { RiskBadge } from '../components/RiskBadge'
import { ErrorState, LoadingState } from '../components/StateViews'
import type { Threat } from '../types'

const EMPTY_FILTERS = { search: '', risk_level: '', threat_type: '', source: '' }

export function Threats() {
  const [threats, setThreats] = useState<Threat[]>([])
  const [total, setTotal] = useState(0)
  const [filters, setFilters] = useState(EMPTY_FILTERS)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setLoading(true)
      setError(false)
      const params = Object.fromEntries(Object.entries(filters).filter(([, value]) => value))
      getThreatsPage(params)
        .then(({ items, total: totalCount }) => {
          setThreats(items)
          setTotal(totalCount)
        })
        .catch(() => setError(true))
        .finally(() => setLoading(false))
    }, 200)
    return () => window.clearTimeout(timer)
  }, [filters])

  if (error) return <ErrorState message="Impossible de charger le registre des menaces." />

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-black uppercase tracking-[0.2em] text-emerald">Indicateurs</p>
        <h1 className="mt-2 text-3xl font-black">Registre des menaces</h1>
        <p className="mt-2 text-sm text-slate-500">Recherchez une IP, un domaine ou une CVE, puis ouvrez la fiche pour comprendre son score.</p>
      </div>

      <section className="rounded-xl border border-slate-200/80 bg-white p-4" aria-label="Filtres des menaces">
        <div className="grid gap-3 lg:grid-cols-[2fr_1fr_1fr_1fr_auto] lg:items-end">
          <label className="text-xs font-bold text-slate-500">
            Rechercher
            <span className="relative mt-1 block">
              <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" aria-hidden="true" />
              <input
                value={filters.search}
                onChange={(event) => setFilters({ ...filters, search: event.target.value })}
                placeholder="IP, domaine, CVE…"
                className="w-full rounded-lg border border-slate-200 py-2.5 pl-10 pr-3 text-sm font-normal outline-none focus:border-emerald"
              />
            </span>
          </label>
          <label className="text-xs font-bold text-slate-500">
            Niveau de risque
            <select value={filters.risk_level} onChange={(event) => setFilters({ ...filters, risk_level: event.target.value })} className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm font-normal outline-none focus:border-emerald">
              <option value="">Tous</option><option value="critical">Critique</option><option value="high">Élevé</option><option value="medium">Moyen</option><option value="low">Faible</option>
            </select>
          </label>
          <label className="text-xs font-bold text-slate-500">
            Type de menace
            <select value={filters.threat_type} onChange={(event) => setFilters({ ...filters, threat_type: event.target.value })} className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm font-normal outline-none focus:border-emerald">
              <option value="">Tous</option><option value="phishing">Phishing</option><option value="malware">Malware</option><option value="ransomware">Ransomware</option><option value="brute_force">Force brute</option><option value="vulnerability">Vulnérabilité</option>
            </select>
          </label>
          <label className="text-xs font-bold text-slate-500">
            Source
            <select value={filters.source} onChange={(event) => setFilters({ ...filters, source: event.target.value })} className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm font-normal outline-none focus:border-emerald">
              <option value="">Toutes</option><option value="sample">Démonstration</option><option value="nvd">NVD</option><option value="urlhaus">URLhaus</option><option value="abuseipdb">AbuseIPDB</option><option value="otx">OTX</option>
            </select>
          </label>
          <button
            onClick={() => setFilters(EMPTY_FILTERS)}
            className="inline-flex h-[42px] items-center justify-center gap-2 rounded-lg border border-slate-200 px-3 text-sm font-bold text-slate-600 hover:bg-slate-50"
            aria-label="Réinitialiser les filtres"
          >
            <FilterX className="h-4 w-4" /> <span className="lg:sr-only">Réinitialiser</span>
          </button>
        </div>
      </section>

      {loading ? <LoadingState label="Recherche des indicateurs…" /> : (
        <section className="overflow-hidden rounded-xl border border-slate-200/80 bg-white">
          <div className="border-b border-slate-100 px-6 py-4 text-sm font-bold">
            {total} menace{total > 1 ? 's' : ''} au total{threats.length !== total && ` · ${threats.length} affichée${threats.length > 1 ? 's' : ''}`}
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[900px] text-left text-sm">
              <thead className="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-400">
                <tr><th className="px-6 py-3">Indicateur</th><th className="px-4 py-3">Type</th><th className="px-4 py-3">Source</th><th className="px-4 py-3">Sévérité</th><th className="px-4 py-3">Risque</th><th className="px-6 py-3 text-right">Score</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {threats.map((threat) => (
                  <tr key={threat.id} className="hover:bg-slate-50">
                    <td className="max-w-sm px-6 py-4">
                      <Link to={`/threats/${threat.id}`} className="block truncate font-bold hover:text-emerald">{threat.indicator}</Link>
                      {threat.known_exploited && <span className="mt-1 inline-flex items-center gap-1 rounded-full bg-red-50 px-2 py-0.5 text-[10px] font-black uppercase text-red-700"><ShieldCheck className="h-3 w-3" /> CISA KEV</span>}
                      <span className="block text-xs text-slate-400">Observé le {new Date(threat.first_seen).toLocaleString('fr-FR')}</span>
                    </td>
                    <td className="px-4 py-4"><span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-bold uppercase">{threat.indicator_type}</span><p className="mt-1 text-xs text-slate-400">{threat.threat_type.replace('_', ' ')}</p></td>
                    <td className="px-4 py-4 text-xs font-black uppercase text-slate-500">{threat.source}</td>
                    <td className="px-4 py-4 capitalize">{threat.severity}</td>
                    <td className="px-4 py-4"><RiskBadge level={threat.risk_level} /></td>
                    <td className="px-6 py-4 text-right text-xl font-black">{threat.risk_score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!threats.length && (
              <div className="p-12 text-center">
                <p className="text-sm text-slate-500">Aucun indicateur ne correspond à ces filtres.</p>
                <button onClick={() => setFilters(EMPTY_FILTERS)} className="mt-3 text-sm font-bold text-emerald hover:underline">Effacer les filtres</button>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  )
}
