import { useEffect, useState, type FormEvent } from 'react'
import axios from 'axios'
import { UserPlus, UsersRound } from 'lucide-react'
import { createUser, getUsers, updateUser } from '../api/client'
import { ErrorState, LoadingState } from '../components/StateViews'
import type { User, UserRole } from '../types'

const ROLE_LABELS: Record<UserRole, string> = {
  admin: 'Administrateur',
  analyst: 'Analyste SOC',
  viewer: 'Lecture seule',
}

export function Users() {
  const [users, setUsers] = useState<User[] | null>(null)
  const [loadError, setLoadError] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<UserRole>('viewer')
  const [submitting, setSubmitting] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)

  const load = () => getUsers()
    .then((data) => { setUsers(data); setLoadError(false) })
    .catch(() => setLoadError(true))

  useEffect(() => { void load() }, [])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setSubmitting(true)
    setFeedback(null)
    try {
      const created = await createUser({ email, password, role })
      setUsers((current) => current ? [created, ...current] : [created])
      setEmail('')
      setPassword('')
      setRole('viewer')
      setFeedback('Le compte a été créé. Il peut se connecter immédiatement.')
    } catch (error) {
      const detail = axios.isAxiosError(error) ? error.response?.data?.detail : null
      setFeedback(typeof detail === 'string' ? detail : 'Impossible de créer le compte.')
    } finally {
      setSubmitting(false)
    }
  }

  const changeUser = async (user: User, changes: Partial<Pick<User, 'role' | 'is_active'>>) => {
    try {
      const updated = await updateUser(user.id, changes)
      setUsers((current) => current?.map((item) => item.id === updated.id ? updated : item) ?? [])
      setFeedback('Les droits du compte ont été mis à jour.')
    } catch (error) {
      const detail = axios.isAxiosError(error) ? error.response?.data?.detail : null
      setFeedback(typeof detail === 'string' ? detail : 'La mise à jour a échoué.')
    }
  }

  if (loadError) return <ErrorState message="Impossible de charger les utilisateurs." />
  if (!users) return <LoadingState label="Chargement des comptes…" />

  return (
    <div className="space-y-6">
      <header>
        <p className="text-xs font-black uppercase tracking-[0.2em] text-emerald">Administration</p>
        <h1 className="mt-2 text-3xl font-black">Utilisateurs et accès</h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-500">
          Donnez uniquement les droits nécessaires : lecture pour la direction, analyse pour le SOC et administration pour les responsables de la plateforme.
        </p>
      </header>

      {feedback && <div role="status" className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold">{feedback}</div>}

      <section className="grid gap-6 xl:grid-cols-[360px_1fr]">
        <form onSubmit={submit} className="h-fit rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-5 flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-mint text-emerald"><UserPlus className="h-5 w-5" /></span>
            <div><h2 className="font-black">Nouveau compte</h2><p className="text-xs text-slate-500">Création réservée aux administrateurs</p></div>
          </div>
          <label className="mb-4 block text-sm font-bold">Email
            <input className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 font-normal" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </label>
          <label className="mb-4 block text-sm font-bold">Mot de passe temporaire
            <input className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 font-normal" type="password" autoComplete="new-password" minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} required />
          </label>
          <label className="mb-5 block text-sm font-bold">Rôle
            <select className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 font-normal" value={role} onChange={(event) => setRole(event.target.value as UserRole)}>
              {Object.entries(ROLE_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
          <button disabled={submitting} className="w-full rounded-lg bg-ink px-4 py-2.5 text-sm font-black text-white disabled:opacity-50">{submitting ? 'Création…' : 'Créer le compte'}</button>
        </form>

        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center gap-3 border-b border-slate-100 p-5"><UsersRound className="h-5 w-5 text-emerald" /><h2 className="font-black">{users.length} compte{users.length > 1 ? 's' : ''}</h2></div>
          <div className="divide-y divide-slate-100">
            {users.map((user) => (
              <article key={user.id} className="grid gap-4 p-5 sm:grid-cols-[1fr_180px_130px] sm:items-center">
                <div><p className="font-black">{user.email}</p><p className="mt-1 text-xs text-slate-400">Créé le {new Date(user.created_at).toLocaleDateString('fr-FR')}</p></div>
                <select aria-label={`Rôle de ${user.email}`} className="rounded-lg border border-slate-200 px-3 py-2 text-sm" value={user.role} onChange={(event) => void changeUser(user, { role: event.target.value as UserRole })}>
                  {Object.entries(ROLE_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select>
                <button onClick={() => void changeUser(user, { is_active: !user.is_active })} className={`rounded-lg px-3 py-2 text-sm font-black ${user.is_active ? 'bg-emerald/10 text-emerald' : 'bg-slate-100 text-slate-500'}`}>{user.is_active ? 'Compte actif' : 'Compte désactivé'}</button>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
