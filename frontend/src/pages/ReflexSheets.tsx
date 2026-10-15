import { useEffect, useState } from 'react'
import { ChevronRight, Info } from 'lucide-react'
import { getReflexSheets } from '../api/client'
import { ReflexSheetDetail } from '../components/ReflexSheetDetail'
import { ErrorState, LoadingState } from '../components/StateViews'
import type { ReflexSheet } from '../types'

const TYPE_LABELS: Record<string, string> = {
  phishing: 'Hameçonnage',
  malware: 'Malware',
  ransomware: 'Rançongiciel',
  brute_force: 'Force brute',
  vulnerability: 'Vulnérabilité',
  suspicious_ip: 'IP suspecte',
  account_compromise: 'Compte compromis',
  data_breach: 'Fuite de données',
  unknown: 'Menace non classifiée',
}

export function ReflexSheets() {
  const [sheets, setSheets] = useState<Record<string, ReflexSheet> | null>(null)
  const [selectedType, setSelectedType] = useState('phishing')
  const [error, setError] = useState(false)

  useEffect(() => {
    getReflexSheets().then(setSheets).catch(() => setError(true))
  }, [])

  if (error) return <ErrorState message="Impossible de charger les procédures de réponse à incident." />
  if (!sheets) return <LoadingState label="Chargement des fiches réflexes…" />

  const entries = Object.entries(sheets)
  const selectedSheet = sheets[selectedType] ?? entries[0]?.[1]

  if (!selectedSheet) return <ErrorState message="Aucune fiche réflexe n’est disponible." />

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-black uppercase tracking-[0.2em] text-emerald">Réponse à incident</p>
        <h1 className="mt-2 text-3xl font-black">Fiches réflexes opérationnelles</h1>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-500">
          Des procédures guidées pour les premières minutes d’un incident, avec les preuves à conserver et les situations qui exigent une assistance spécialisée.
        </p>
      </div>

      <div className="flex gap-3 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm leading-relaxed text-blue-900" role="note">
        <Info className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
        <p><strong>Avant d’agir :</strong> désignez une personne qui note les heures, décisions et actions. En cas d’incident critique, utilisez un canal de communication indépendant du système potentiellement compromis.</p>
      </div>

      <div className="grid items-start gap-6 lg:grid-cols-[260px_minmax(0,1fr)]">
        <nav className="rounded-xl border border-slate-200/80 bg-white p-2 lg:sticky lg:top-20" aria-label="Types de fiches réflexes">
          <p className="px-3 pb-2 pt-2 text-[11px] font-black uppercase tracking-wider text-slate-400">Choisir un incident</p>
          <div className="grid gap-1 sm:grid-cols-2 lg:grid-cols-1">
            {entries.map(([type, sheet]) => {
              const isSelected = selectedSheet === sheet
              return (
                <button
                  key={type}
                  type="button"
                  onClick={() => setSelectedType(type)}
                  aria-pressed={isSelected}
                  className={`flex w-full items-center justify-between gap-3 rounded-lg px-3 py-3 text-left transition ${isSelected ? 'bg-ink text-white' : 'text-slate-600 hover:bg-slate-50 hover:text-ink'}`}
                >
                  <span>
                    <span className="block text-sm font-bold">{TYPE_LABELS[type] ?? type.replace('_', ' ')}</span>
                    <span className={`mt-0.5 block text-[11px] capitalize ${isSelected ? 'text-slate-300' : 'text-slate-400'}`}>Priorité {sheet.priority}</span>
                  </span>
                  <ChevronRight className="h-4 w-4 shrink-0" aria-hidden="true" />
                </button>
              )
            })}
          </div>
        </nav>

        <ReflexSheetDetail sheet={selectedSheet} />
      </div>
    </div>
  )
}
