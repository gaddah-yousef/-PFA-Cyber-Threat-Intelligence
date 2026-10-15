import { useState, type FormEvent } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { CheckCircle2, LogIn, ShieldCheck } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'

export function Login() {
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (isAuthenticated) {
    const redirectTo = (location.state as { from?: string } | null)?.from ?? '/'
    return <Navigate to={redirectTo} replace />
  }

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/', { replace: true })
    } catch {
      setError('Email ou mot de passe incorrect.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="grid min-h-screen bg-canvas lg:grid-cols-[1.1fr_0.9fr]">
      <section className="hidden bg-ink p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-xl bg-lime text-ink"><ShieldCheck className="h-6 w-6" strokeWidth={2.5} /></span>
          <div><p className="font-black">Sentinel PME</p><p className="text-xs text-slate-400">Veille cyber simplifiée</p></div>
        </div>
        <div className="max-w-xl">
          <p className="text-xs font-black uppercase tracking-[0.2em] text-lime">Pensé pour les petites équipes</p>
          <h1 className="mt-4 text-4xl font-black leading-tight">Comprendre le risque, puis agir sans perdre de temps.</h1>
          <ul className="mt-8 space-y-4 text-sm text-slate-300">
            <li className="flex items-center gap-3"><CheckCircle2 className="h-5 w-5 text-lime" /> Indicateurs centralisés et classés par priorité</li>
            <li className="flex items-center gap-3"><CheckCircle2 className="h-5 w-5 text-lime" /> Score expliqué avec des actions concrètes</li>
            <li className="flex items-center gap-3"><CheckCircle2 className="h-5 w-5 text-lime" /> Suivi des alertes dans une vue SOC légère</li>
          </ul>
        </div>
        <p className="text-xs text-slate-500">Projet PFA · Plateforme de Threat Intelligence pour PME</p>
      </section>

      <section className="flex items-center justify-center p-6 sm:p-10">
        <form onSubmit={onSubmit} className="w-full max-w-sm rounded-xl border border-slate-200/80 bg-white p-7 sm:p-8">
          <div className="mb-7">
            <span className="mb-5 grid h-11 w-11 place-items-center rounded-xl bg-mint text-emerald lg:hidden"><ShieldCheck className="h-6 w-6" strokeWidth={2.5} /></span>
            <p className="text-xs font-black uppercase tracking-[0.2em] text-emerald">Espace sécurisé</p>
            <h2 className="mt-2 text-2xl font-black">Bienvenue</h2>
            <p className="mt-2 text-sm leading-relaxed text-slate-500">Connectez-vous pour accéder au centre de veille de votre PME.</p>
          </div>
          <label className="mb-4 block text-sm font-semibold text-slate-600">
            Adresse email
            <input
              type="email"
              required
              autoFocus
              autoComplete="username"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-1.5 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-emerald"
              placeholder="vous@entreprise.com"
            />
          </label>
          <label className="mb-5 block text-sm font-semibold text-slate-600">
            Mot de passe
            <input
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-1.5 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-emerald"
              placeholder="••••••••"
            />
          </label>
          {error && <p className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm font-semibold text-red-700" role="alert">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-ink px-5 py-3 text-sm font-bold text-white transition hover:bg-emerald disabled:cursor-wait disabled:opacity-60"
          >
            <LogIn className="h-4 w-4" /> {loading ? 'Connexion…' : 'Se connecter'}
          </button>
        </form>
      </section>
    </main>
  )
}
