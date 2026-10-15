import { useEffect, useState } from 'react'
import { BellRing, Check, FlaskConical, Pencil, Send } from 'lucide-react'
import { acknowledgeAlert, createTestAlert, getAlertSiemEvent, getAlerts, updateAlert } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { ErrorState, LoadingState } from '../components/StateViews'
import type { Alert, AlertStatus } from '../types'

const STATUS_LABELS: Record<AlertStatus, string> = {
  new: 'Nouvelle',
  investigating: 'En cours d’analyse',
  resolved: 'Résolue',
  false_positive: 'Faux positif',
}

const STATUS_STYLES: Record<AlertStatus, string> = {
  new: 'bg-slate-100 text-slate-600',
  investigating: 'bg-blue-50 text-blue-600',
  resolved: 'bg-emerald/10 text-emerald',
  false_positive: 'bg-slate-100 text-slate-400',
}

const LEVEL_LABELS = { critical: 'Critique', high: 'Élevée' }

function downloadJson(filename: string, data: unknown) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

export function Alerts() {
  const { canWrite } = useAuth()
  const [alerts, setAlerts] = useState<Alert[] | null>(null)
  const [error, setError] = useState(false)
  const [busyId, setBusyId] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [statusDraft, setStatusDraft] = useState<AlertStatus>('investigating')
  const [assignedToDraft, setAssignedToDraft] = useState('')
  const [notesDraft, setNotesDraft] = useState('')

  const load = () => getAlerts().then(setAlerts).catch(() => setError(true))
  useEffect(() => {
    void load()
  }, [])

  const test = () => createTestAlert().then(load).catch(() => setError(true))

  const acknowledge = async (id: string) => {
    setBusyId(id)
    try {
      await acknowledgeAlert(id)
      await load()
    } catch {
      setError(true)
    } finally {
      setBusyId(null)
    }
  }

  const startEditing = (alert: Alert) => {
    setEditingId(alert.id)
    setStatusDraft(alert.status === 'new' ? 'investigating' : alert.status)
    setAssignedToDraft(alert.assigned_to ?? '')
    setNotesDraft(alert.resolution_notes ?? '')
  }

  const saveSoc = async (id: string) => {
    setBusyId(id)
    try {
      await updateAlert(id, {
        status: statusDraft,
        assigned_to: assignedToDraft.trim() || null,
        resolution_notes: notesDraft.trim() || null,
      })
      setEditingId(null)
      await load()
    } catch {
      setError(true)
    } finally {
      setBusyId(null)
    }
  }

  const exportSiem = async (id: string) => {
    try {
      const event = await getAlertSiemEvent(id)
      downloadJson(`sentinel-pme-alert-${id}.json`, event)
    } catch {
      setError(true)
    }
  }

  if (error) return <ErrorState />
  if (!alerts) return <LoadingState />

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-xs font-black uppercase tracking-[0.2em] text-emerald">Early warning</p>
          <h1 className="mt-2 text-3xl font-black">Centre d’alertes · vue SOC</h1>
          <p className="mt-2 text-sm text-slate-500">
            Les menaces à score élevé ou critique apparaissent automatiquement ici. Statut,
            assignation et export SIEM permettent un traitement façon mini-SOC.
          </p>
        </div>
        {canWrite && (
          <button
            onClick={test}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-ink px-5 py-3 text-sm font-bold text-white hover:bg-emerald"
          >
            <FlaskConical className="h-4 w-4" /> Générer une alerte test
          </button>
        )}
      </div>

      <section className="grid gap-4">
        {alerts.map((alert) => {
          const alertStatus: AlertStatus = alert.status ?? 'new'
          const isResolved = alertStatus === 'resolved' || alertStatus === 'false_positive'
          const isEditing = editingId === alert.id
          return (
            <article
              key={alert.id}
              className={`rounded-xl border border-slate-200/80 border-l-4 bg-white p-5 ${isResolved ? 'opacity-60' : ''} ${alert.level === 'critical' ? 'border-l-red-500' : 'border-l-orange-400'}`}
            >
              <div className="flex flex-col items-start gap-4 sm:flex-row">
                <span
                  className={`shrink-0 rounded-lg p-3 ${alert.level === 'critical' ? 'bg-red-50 text-red-600' : 'bg-orange-50 text-orange-600'}`}
                >
                  <BellRing className="h-5 w-5" />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-3">
                    <h2 className="font-black">{alert.title}</h2>
                    <span
                      className={`text-xs font-black uppercase ${alert.level === 'critical' ? 'text-red-600' : 'text-orange-600'}`}
                    >
                      {LEVEL_LABELS[alert.level]}
                    </span>
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${STATUS_STYLES[alertStatus]}`}>
                      {STATUS_LABELS[alertStatus]}
                    </span>
                    {alert.assigned_to && (
                      <span className="rounded-full bg-mint px-2.5 py-0.5 text-xs font-bold text-emerald">
                        Assignée à {alert.assigned_to}
                      </span>
                    )}
                  </div>
                  <p className="mt-2 break-words text-sm leading-relaxed text-slate-600">{alert.message}</p>
                  {alert.resolution_notes && (
                    <p className="mt-2 rounded-xl bg-slate-50 p-3 text-xs leading-relaxed text-slate-500">
                      Note d’analyse : {alert.resolution_notes}
                    </p>
                  )}
                  <p className="mt-3 text-xs text-slate-400">
                    {new Date(alert.created_at).toLocaleString('fr-FR')} · canal {alert.channel}
                  </p>

                  {isEditing && (
                    <div className="mt-4 grid gap-3 rounded-xl border border-slate-200 p-4 sm:grid-cols-2">
                      <label className="text-xs font-bold text-slate-500">
                        Statut
                        <select
                          value={statusDraft}
                          onChange={(event) => setStatusDraft(event.target.value as AlertStatus)}
                          className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                        >
                          <option value="investigating">En cours d’analyse</option>
                          <option value="resolved">Résolue</option>
                          <option value="false_positive">Faux positif</option>
                        </select>
                      </label>
                      <label className="text-xs font-bold text-slate-500">
                        Assigné à
                        <input
                          value={assignedToDraft}
                          onChange={(event) => setAssignedToDraft(event.target.value)}
                          placeholder="analyste@entreprise.com"
                          className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                        />
                      </label>
                      <label className="col-span-full text-xs font-bold text-slate-500">
                        Notes d’analyse
                        <textarea
                          value={notesDraft}
                          onChange={(event) => setNotesDraft(event.target.value)}
                          rows={2}
                          className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                        />
                      </label>
                      <div className="col-span-full flex justify-end gap-2">
                        <button
                          onClick={() => setEditingId(null)}
                          className="rounded-xl px-3 py-2 text-xs font-bold text-slate-500 hover:bg-slate-50"
                        >
                          Annuler
                        </button>
                        <button
                          onClick={() => saveSoc(alert.id)}
                          disabled={busyId === alert.id}
                          className="inline-flex items-center gap-2 rounded-xl bg-ink px-4 py-2 text-xs font-bold text-white hover:bg-emerald disabled:opacity-50"
                        >
                          <Send className="h-3.5 w-3.5" /> Enregistrer
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                <div className="grid w-full shrink-0 grid-cols-1 gap-2 sm:w-auto">
                  <button
                    onClick={() => exportSiem(alert.id)}
                    className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-bold text-slate-600 transition hover:bg-slate-50"
                  >
                    Exporter SIEM
                  </button>
                  {canWrite && !isEditing && (
                    <button
                      onClick={() => startEditing(alert)}
                      className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-bold text-slate-600 transition hover:bg-slate-50"
                    >
                      <Pencil className="h-4 w-4" /> Statut / assignation
                    </button>
                  )}
                  {canWrite && !isResolved && (
                    <button
                      onClick={() => acknowledge(alert.id)}
                      disabled={busyId === alert.id}
                      className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-bold text-slate-600 transition hover:bg-slate-50 disabled:opacity-50"
                    >
                      <Check className="h-4 w-4" /> Acquitter
                    </button>
                  )}
                </div>
              </div>
            </article>
          )
        })}
        {!alerts.length && (
          <div className="rounded-2xl bg-white p-12 text-center text-slate-400">Aucune alerte enregistrée.</div>
        )}
      </section>
    </div>
  )
}
