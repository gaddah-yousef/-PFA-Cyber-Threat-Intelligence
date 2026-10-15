import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { FileUp, Globe2, MonitorCog, Plus, Server, ShieldAlert, X } from 'lucide-react'
import { Link } from 'react-router-dom'
import { createAsset, getAssetsPage, getAssetStats, importAssetsCsv } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { ErrorState, LoadingState } from '../components/StateViews'
import type { Asset, AssetCriticality, AssetInput, AssetStats } from '../types'

const EMPTY_FORM: AssetInput = {
  hostname: '', ip_address: '', asset_type: 'server', operating_system: '', environment: 'production',
  criticality: 'medium', internet_exposed: false, owner: '', description: '',
}

const CRITICALITY_LABELS: Record<AssetCriticality, string> = {
  low: 'Faible', medium: 'Moyenne', high: 'Élevée', critical: 'Critique',
}

export function Assets() {
  const { canWrite } = useAuth()
  const [assets, setAssets] = useState<Asset[] | null>(null)
  const [stats, setStats] = useState<AssetStats | null>(null)
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState<AssetInput>(EMPTY_FORM)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [feedback, setFeedback] = useState('')

  const load = useCallback(async (query = '') => {
    try {
      const params: Record<string, string> = { limit: '500' }
      if (query) params.search = query
      const [page, summary] = await Promise.all([getAssetsPage(params), getAssetStats()])
      setAssets(page.items)
      setStats(summary)
      setError('')
    } catch {
      setError('Impossible de charger le parc informatique.')
    }
  }, [])

  useEffect(() => { void load() }, [load])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    try {
      await createAsset({ ...form, ip_address: form.ip_address || null, owner: form.owner || null, description: form.description || null })
      setForm(EMPTY_FORM)
      setShowForm(false)
      setFeedback('Actif ajouté au parc informatique.')
      await load(search)
    } catch {
      setError('Création impossible. Vérifiez le hostname, l’adresse IP et les doublons.')
    } finally {
      setBusy(false)
    }
  }

  const importCsv = async (file?: File) => {
    if (!file) return
    setBusy(true)
    try {
      const report = await importAssetsCsv(file)
      setFeedback(`${report.created} actif(s) importé(s), ${report.skipped} doublon(s), ${report.error_count} erreur(s).`)
      await load(search)
    } catch {
      setError('Import impossible. Utilisez un CSV UTF-8 de 500 lignes maximum.')
    } finally {
      setBusy(false)
    }
  }

  if (!assets && !error) return <LoadingState label="Chargement du parc informatique…" />
  if (!assets) return <ErrorState message={error} />

  const cards = [
    { label: 'Actifs suivis', value: stats?.total ?? 0, icon: MonitorCog },
    { label: 'Critiques', value: stats?.critical ?? 0, icon: ShieldAlert },
    { label: 'Exposés à Internet', value: stats?.internet_exposed ?? 0, icon: Globe2 },
    { label: 'Avec CVE confirmée', value: stats?.with_confirmed_vulnerabilities ?? 0, icon: Server },
  ]

  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div>
          <p className="text-xs font-black uppercase tracking-[0.2em] text-emerald">Surface d’attaque réelle</p>
          <h1 className="mt-2 text-3xl font-black">Parc informatique</h1>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-500">Reliez les serveurs, postes et applications de la PME aux vulnérabilités qui les concernent réellement.</p>
        </div>
        {canWrite && <div className="flex flex-wrap gap-2">
          <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-bold hover:bg-slate-50">
            <FileUp className="h-4 w-4" /> Importer un CSV
            <input className="sr-only" type="file" accept=".csv,text/csv" disabled={busy} onChange={(event) => void importCsv(event.target.files?.[0])} />
          </label>
          <button onClick={() => setShowForm(true)} className="inline-flex items-center gap-2 rounded-xl bg-ink px-4 py-3 text-sm font-bold text-white hover:bg-emerald"><Plus className="h-4 w-4" /> Ajouter un actif</button>
        </div>}
      </header>

      {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>}
      {feedback && <div role="status" className="rounded-xl border border-emerald/20 bg-mint px-4 py-3 text-sm font-semibold text-emerald">{feedback}</div>}

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map(({ label, value, icon: Icon }) => <article key={label} className="rounded-2xl border border-slate-200/70 bg-white p-5"><Icon className="mb-5 h-5 w-5 text-emerald" /><p className="text-xs font-bold uppercase tracking-wide text-slate-400">{label}</p><p className="mt-2 text-3xl font-black">{value}</p></article>)}
      </section>

      <section className="overflow-hidden rounded-2xl border border-slate-200/70 bg-white">
        <div className="flex flex-col gap-3 border-b border-slate-100 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div><h2 className="font-black">Inventaire des actifs</h2><p className="text-xs text-slate-400">{assets.length} actif(s) affiché(s)</p></div>
          <form className="flex gap-2" onSubmit={(event) => { event.preventDefault(); void load(search) }}><label className="sr-only" htmlFor="asset-search">Rechercher un actif</label><input id="asset-search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Hostname ou adresse IP" className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm sm:w-64" /><button className="rounded-lg bg-slate-100 px-3 py-2 text-xs font-bold">Rechercher</button></form>
        </div>
        <div className="overflow-x-auto"><table className="w-full min-w-[850px] text-left text-sm"><thead className="bg-slate-50 text-[11px] uppercase tracking-wide text-slate-400"><tr><th className="px-5 py-3">Actif</th><th className="px-5 py-3">Système</th><th className="px-5 py-3">Contexte</th><th className="px-5 py-3">Logiciels</th><th className="px-5 py-3">Vulnérabilités</th></tr></thead><tbody>
          {assets.map((asset) => <tr key={asset.id} className="border-t border-slate-100 hover:bg-slate-50/60"><td className="px-5 py-4"><Link to={`/assets/${asset.id}`} className="font-black text-ink hover:text-emerald">{asset.hostname}</Link><p className="mt-1 text-xs text-slate-400">{asset.ip_address || 'IP non renseignée'} {asset.internet_exposed && '· exposé Internet'}</p></td><td className="px-5 py-4"><p className="font-semibold">{asset.operating_system}</p><p className="text-xs text-slate-400">{asset.asset_type.replace('_', ' ')}</p></td><td className="px-5 py-4"><span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-bold">{CRITICALITY_LABELS[asset.criticality]}</span><p className="mt-2 text-xs text-slate-400">{asset.environment}</p></td><td className="px-5 py-4 font-bold">{asset.software_count}</td><td className="px-5 py-4"><p className="font-bold text-red-600">{asset.confirmed_vulnerabilities} confirmée{asset.confirmed_vulnerabilities > 1 ? 's' : ''}</p><p className="text-xs text-amber-600">{asset.potential_vulnerabilities} à vérifier</p></td></tr>)}
        </tbody></table></div>
        {!assets.length && <p className="p-10 text-center text-sm text-slate-400">Aucun actif. Ajoutez le premier équipement de la PME ou importez un CSV.</p>}
      </section>

      {showForm && <div className="fixed inset-0 z-50 grid place-items-center bg-ink/60 p-4"><form onSubmit={submit} className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-white p-6 shadow-2xl"><div className="mb-5 flex items-center justify-between"><div><h2 className="text-xl font-black">Nouvel actif</h2><p className="text-xs text-slate-400">Les champs marqués sont nécessaires au suivi.</p></div><button type="button" onClick={() => setShowForm(false)} aria-label="Fermer"><X /></button></div><div className="grid gap-4 sm:grid-cols-2">
        <label className="text-sm font-bold">Nom de l'actif *<input required value={form.hostname} onChange={(e) => setForm({ ...form, hostname: e.target.value })} placeholder="srv-web-01" className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 font-normal" /></label>
        <label className="text-sm font-bold">Adresse IP<input value={form.ip_address ?? ''} onChange={(e) => setForm({ ...form, ip_address: e.target.value })} placeholder="192.0.2.10" className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 font-normal" /></label>
        <label className="text-sm font-bold">Type<select value={form.asset_type} onChange={(e) => setForm({ ...form, asset_type: e.target.value as AssetInput['asset_type'] })} className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 font-normal"><option value="server">Serveur</option><option value="workstation">Poste</option><option value="network_device">Équipement réseau</option><option value="application">Application</option><option value="cloud_resource">Ressource cloud</option><option value="other">Autre</option></select></label>
        <label className="text-sm font-bold">Système d'exploitation *<input required value={form.operating_system} onChange={(e) => setForm({ ...form, operating_system: e.target.value })} placeholder="Ubuntu Server 24.04" className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 font-normal" /></label>
        <label className="text-sm font-bold">Environnement<select value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value as AssetInput['environment'] })} className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 font-normal"><option value="production">Production</option><option value="development">Développement</option><option value="testing">Test</option></select></label>
        <label className="text-sm font-bold">Criticité<select value={form.criticality} onChange={(e) => setForm({ ...form, criticality: e.target.value as AssetCriticality })} className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 font-normal"><option value="low">Faible</option><option value="medium">Moyenne</option><option value="high">Élevée</option><option value="critical">Critique</option></select></label>
        <label className="text-sm font-bold">Responsable<input value={form.owner ?? ''} onChange={(e) => setForm({ ...form, owner: e.target.value })} placeholder="Équipe infrastructure" className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 font-normal" /></label>
        <label className="flex items-center gap-2 self-end rounded-lg bg-amber-50 p-3 text-sm font-bold text-amber-800"><input type="checkbox" checked={form.internet_exposed} onChange={(e) => setForm({ ...form, internet_exposed: e.target.checked })} /> Accessible depuis Internet</label>
      </div><div className="mt-6 flex justify-end gap-2"><button type="button" onClick={() => setShowForm(false)} className="rounded-xl px-4 py-2 text-sm font-bold text-slate-500">Annuler</button><button disabled={busy} className="rounded-xl bg-ink px-5 py-2.5 text-sm font-bold text-white disabled:opacity-50">Enregistrer l'actif</button></div></form></div>}
    </div>
  )
}
