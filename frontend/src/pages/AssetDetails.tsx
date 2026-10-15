import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { ArrowLeft, CheckCircle2, CircleHelp, Globe2, PackagePlus, ShieldAlert, XCircle } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { createAssetSoftware, getAsset, getAssetSoftware, getAssetVulnerabilities } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { ErrorState, LoadingState } from '../components/StateViews'
import type { Asset, AssetVulnerability, Software, SoftwareInput } from '../types'

const EMPTY_SOFTWARE: SoftwareInput = { name: '', vendor: '', version: '', cpe: '', purl: '' }
const STATUS = {
  confirmed: { label: 'Confirmée', style: 'bg-red-50 text-red-700', icon: ShieldAlert },
  potential: { label: 'À vérifier', style: 'bg-amber-50 text-amber-700', icon: CircleHelp },
  not_affected: { label: 'Non affecté', style: 'bg-emerald/10 text-emerald', icon: CheckCircle2 },
}

export function AssetDetails() {
  const { id = '' } = useParams()
  const { canWrite } = useAuth()
  const [asset, setAsset] = useState<Asset | null>(null)
  const [software, setSoftware] = useState<Software[]>([])
  const [vulnerabilities, setVulnerabilities] = useState<AssetVulnerability[]>([])
  const [form, setForm] = useState<SoftwareInput>(EMPTY_SOFTWARE)
  const [showForm, setShowForm] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(false)

  const load = useCallback(async () => {
    try {
      const [assetData, softwareData, matches] = await Promise.all([getAsset(id), getAssetSoftware(id), getAssetVulnerabilities(id)])
      setAsset(assetData); setSoftware(softwareData); setVulnerabilities(matches); setError(false)
    } catch { setError(true) }
  }, [id])
  useEffect(() => { void load() }, [load])

  const submit = async (event: FormEvent) => {
    event.preventDefault(); setBusy(true)
    try {
      await createAssetSoftware(id, { ...form, vendor: form.vendor || null, cpe: form.cpe || null, purl: form.purl || null })
      setForm(EMPTY_SOFTWARE); setShowForm(false); await load()
    } catch { setError(true) } finally { setBusy(false) }
  }

  if (error && !asset) return <ErrorState message="Impossible de charger cet actif." />
  if (!asset) return <LoadingState label="Analyse de l’actif…" />

  return <div className="space-y-6">
    <Link to="/assets" className="inline-flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-emerald"><ArrowLeft className="h-4 w-4" /> Retour au parc</Link>
    <header className="rounded-2xl bg-ink p-6 text-white md:p-8"><div className="flex flex-col justify-between gap-5 md:flex-row md:items-start"><div><div className="flex flex-wrap items-center gap-2"><span className="rounded-full bg-white/10 px-3 py-1 text-xs font-bold uppercase">{asset.asset_type.replace('_', ' ')}</span>{asset.internet_exposed && <span className="inline-flex items-center gap-1 rounded-full bg-amber-400/20 px-3 py-1 text-xs font-bold text-amber-300"><Globe2 className="h-3.5 w-3.5" /> Exposé Internet</span>}</div><h1 className="mt-4 text-3xl font-black">{asset.hostname}</h1><p className="mt-2 text-sm text-slate-300">{asset.ip_address || 'Adresse IP non renseignée'} · {asset.operating_system}</p></div><dl className="grid grid-cols-2 gap-4 text-sm"><div><dt className="text-xs text-slate-400">Criticité</dt><dd className="mt-1 font-black capitalize">{asset.criticality}</dd></div><div><dt className="text-xs text-slate-400">Responsable</dt><dd className="mt-1 font-black">{asset.owner || 'Non assigné'}</dd></div></dl></div></header>

    <section className="rounded-2xl border border-slate-200/70 bg-white p-5"><div className="mb-5 flex items-center justify-between"><div><h2 className="font-black">Logiciels installés</h2><p className="text-xs text-slate-400">Renseignez le CPE 2.3 quand il est connu pour améliorer la précision.</p></div>{canWrite && <button onClick={() => setShowForm(!showForm)} className="inline-flex items-center gap-2 rounded-xl bg-ink px-4 py-2.5 text-sm font-bold text-white hover:bg-emerald"><PackagePlus className="h-4 w-4" /> Ajouter un logiciel</button>}</div>
      {showForm && <form onSubmit={submit} className="mb-5 grid gap-3 rounded-xl bg-slate-50 p-4 md:grid-cols-2"><label className="text-xs font-bold">Nom du logiciel *<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm font-normal" /></label><label className="text-xs font-bold">Version *<input required value={form.version} onChange={(e) => setForm({ ...form, version: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm font-normal" /></label><label className="text-xs font-bold">Éditeur<input value={form.vendor ?? ''} onChange={(e) => setForm({ ...form, vendor: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm font-normal" /></label><label className="text-xs font-bold">CPE 2.3<input value={form.cpe ?? ''} onChange={(e) => setForm({ ...form, cpe: e.target.value })} placeholder="cpe:2.3:a:vendor:product:version:*:*:*:*:*:*:*" className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm font-normal" /></label><div className="col-span-full flex justify-end gap-2"><button type="button" onClick={() => setShowForm(false)} className="px-3 py-2 text-xs font-bold text-slate-500">Annuler</button><button disabled={busy} className="rounded-lg bg-ink px-4 py-2 text-xs font-bold text-white">Enregistrer le logiciel</button></div></form>}
      <div className="grid gap-3 md:grid-cols-2">{software.map((item) => <article key={item.id} className="rounded-xl border border-slate-200 p-4"><div className="flex justify-between gap-3"><div><h3 className="font-black">{item.name}</h3><p className="text-xs text-slate-400">{item.vendor || 'Éditeur inconnu'} · version {item.version}</p></div>{item.cpe ? <CheckCircle2 className="h-5 w-5 text-emerald" aria-label="CPE renseigné" /> : <CircleHelp className="h-5 w-5 text-amber-500" aria-label="CPE manquant" />}</div>{item.cpe && <code className="mt-3 block break-all rounded bg-slate-50 p-2 text-[10px] text-slate-500">{item.cpe}</code>}</article>)}</div>{!software.length && <p className="py-8 text-center text-sm text-slate-400">Aucun logiciel inventorié.</p>}
    </section>

    <section className="rounded-2xl border border-slate-200/70 bg-white p-5"><div className="mb-5"><h2 className="font-black">Vulnérabilités associées</h2><p className="text-xs leading-relaxed text-slate-400">Une correspondance « confirmée » repose sur un CPE et une version compatibles. « À vérifier » signale une information incomplète ou une configuration NVD complexe.</p></div><div className="space-y-3">{vulnerabilities.map((match) => { const state = STATUS[match.matching_status]; const Icon = state.icon; return <article key={match.id} className="rounded-xl border border-slate-200 p-4"><div className="flex flex-col justify-between gap-3 sm:flex-row"><div><div className="flex flex-wrap items-center gap-2"><h3 className="font-black">{match.cve_id}</h3><span className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-bold ${state.style}`}><Icon className="h-3.5 w-3.5" /> {state.label}</span><span className="text-xs font-black uppercase text-slate-400">score {match.risk_score}/100</span></div><p className="mt-2 text-sm font-semibold">{match.software_name} {match.software_version}</p><p className="mt-1 text-xs leading-relaxed text-slate-500">{match.matching_reason}</p></div><Link to={`/threats/${match.threat_id}`} className="h-fit text-xs font-bold text-emerald hover:underline">Voir la CVE</Link></div></article> })}</div>{!vulnerabilities.length && <div className="py-10 text-center"><XCircle className="mx-auto mb-2 h-7 w-7 text-slate-300" /><p className="text-sm text-slate-400">Aucune correspondance CVE détectée avec les données disponibles.</p></div>}
    </section>
  </div>
}
