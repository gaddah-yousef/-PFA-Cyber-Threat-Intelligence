import { useEffect, useState } from 'react'
import axios from 'axios'
import { CheckCircle2, Database, ExternalLink, KeyRound, Loader2, PlayCircle } from 'lucide-react'
import { getCollectors, runCollector } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { ErrorState, LoadingState } from '../components/StateViews'
import type { Collector } from '../types'

const SOURCE_INFO: Record<string, { label: string; description: string; env?: string; helpUrl?: string }> = {
  sample: { label: 'Jeu de démonstration', description: 'Données locales utiles pour découvrir la plateforme.' },
  urlhaus: {
    label: 'URLhaus',
    description: 'URLs malveillantes de l’export communautaire URLhaus v2.',
    env: 'URLHAUS_AUTH_KEY',
    helpUrl: 'https://auth.abuse.ch/',
  },
  nvd: { label: 'NVD + EPSS + CISA KEV', description: 'CVE récentes enrichies avec leur probabilité d’exploitation et les exploitations actives connues.', env: 'NVD_API_KEY' },
  abuseipdb: { label: 'AbuseIPDB', description: 'Adresses IP associées à des activités malveillantes.', env: 'ABUSEIPDB_API_KEY' },
  otx: { label: 'AlienVault OTX', description: 'Indicateurs partagés dans les pulses OTX.', env: 'OTX_API_KEY' },
}

type Feedback = { tone: 'success' | 'error'; message: string }

export function Sources() {
  const { canWrite } = useAuth()
  const [collectors, setCollectors] = useState<Collector[] | null>(null)
  const [error, setError] = useState(false)
  const [running, setRunning] = useState<string | null>(null)
  const [feedback, setFeedback] = useState<Feedback | null>(null)

  const load = () => getCollectors()
    .then((data) => {
      setCollectors(data)
      setError(false)
    })
    .catch(() => setError(true))

  useEffect(() => { void load() }, [])

  const run = async (name: string) => {
    setRunning(name)
    setFeedback(null)
    try {
      const result = await runCollector(name)
      const label = SOURCE_INFO[name]?.label ?? name
      setFeedback({
        tone: 'success',
        message: `${label} : ${result.threats_processed} menace${result.threats_processed > 1 ? 's' : ''} traitée${result.threats_processed > 1 ? 's' : ''}.`,
      })
      await load()
    } catch (error) {
      const apiMessage = axios.isAxiosError(error) && typeof error.response?.data?.detail === 'string'
        ? error.response.data.detail
        : null
      setFeedback({
        tone: 'error',
        message: apiMessage ?? `La collecte ${SOURCE_INFO[name]?.label ?? name} a échoué. Vérifiez la clé API et les journaux du backend.`,
      })
    } finally {
      setRunning(null)
    }
  }

  if (error) return <ErrorState message="Impossible de récupérer l’état des sources." />
  if (!collectors) return <LoadingState label="Vérification des sources…" />

  const configuredCount = collectors.filter((collector) => collector.configured).length

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-black uppercase tracking-[0.2em] text-emerald">Collecte</p>
        <h1 className="mt-2 text-3xl font-black">Sources de veille</h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-500">
          {configuredCount} source{configuredCount > 1 ? 's' : ''} prête{configuredCount > 1 ? 's' : ''}. Lancez une collecte manuelle pour tester une connexion ou laissez le planificateur travailler automatiquement.
        </p>
      </div>

      {feedback && (
        <div
          role={feedback.tone === 'error' ? 'alert' : 'status'}
          className={`rounded-xl border px-4 py-3 text-sm font-semibold ${feedback.tone === 'success' ? 'border-emerald/20 bg-mint text-emerald' : 'border-red-200 bg-red-50 text-red-800'}`}
        >
          {feedback.message}
        </div>
      )}

      <section className="grid gap-4 md:grid-cols-2">
        {collectors.map((collector) => {
          const info = SOURCE_INFO[collector.name] ?? { label: collector.name, description: 'Source de renseignement cyber.' }
          const needsKey = collector.requires_api_key && !collector.configured
          return (
            <article key={collector.name} className="rounded-xl border border-slate-200/80 bg-white p-5">
              <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
                <div className="flex items-start gap-3">
                  <span className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-mint text-emerald">
                    <Database className="h-5 w-5" />
                  </span>
                  <div>
                    <h2 className="font-black">{info.label}</h2>
                    <p className="mt-1 text-xs leading-relaxed text-slate-500">{info.description}</p>
                  </div>
                </div>
                <span className={`inline-flex w-fit items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold ${needsKey ? 'bg-amber-50 text-amber-700' : 'bg-emerald/10 text-emerald'}`}>
                  {needsKey ? <KeyRound className="h-3.5 w-3.5" /> : <CheckCircle2 className="h-3.5 w-3.5" />}
                  {needsKey ? 'À configurer' : 'Prête'}
                </span>
              </div>

              {needsKey && info.env && (
                <div className="mt-4 rounded-lg bg-amber-50 px-3 py-2 text-xs leading-relaxed text-amber-800">
                  Ajoutez <code className="font-bold">{info.env}</code> dans <code className="font-bold">backend/.env</code>, puis redémarrez l’API.
                  {info.helpUrl && <a href={info.helpUrl} target="_blank" rel="noreferrer" className="ml-2 inline-flex items-center gap-1 font-black underline">Obtenir la clé gratuite <ExternalLink className="h-3 w-3" /></a>}
                </div>
              )}

              <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
                <div>
                  <dt className="text-xs text-slate-400">Menaces enregistrées</dt>
                  <dd className="mt-1 font-bold">{collector.threat_count}</dd>
                </div>
                <div>
                  <dt className="text-xs text-slate-400">Dernière collecte</dt>
                  <dd className="mt-1 text-xs font-bold sm:text-sm">
                    {collector.last_collected_at ? new Date(collector.last_collected_at).toLocaleString('fr-FR') : 'Jamais lancée'}
                  </dd>
                </div>
              </dl>

              {canWrite && (
                <button
                  onClick={() => run(collector.name)}
                  disabled={Boolean(running) || needsKey}
                  className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-ink px-4 py-2.5 text-sm font-bold text-white transition hover:bg-emerald disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
                >
                  {running === collector.name ? <Loader2 className="h-4 w-4 animate-spin" /> : <PlayCircle className="h-4 w-4" />}
                  {running === collector.name ? 'Collecte en cours…' : 'Lancer la collecte'}
                </button>
              )}
            </article>
          )
        })}
      </section>
    </div>
  )
}
