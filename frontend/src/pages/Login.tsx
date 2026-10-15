import { useEffect, useState, type FormEvent, type PointerEvent as ReactPointerEvent } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { CheckCircle2, LogIn, Pause, Play, ShieldCheck } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'

const LOGIN_SCENES = [
  {
    src: '/images/login/threat-analysis.jpg',
    alt: 'Loupe analysant une cartographie de cybermenaces',
    label: 'Analyse des menaces',
    title: 'Détecter le signal avant qu’il ne devienne un incident.',
  },
  {
    src: '/images/login/identity-protection.jpg',
    alt: 'Cadenas numériques protégeant une empreinte digitale',
    label: 'Protection des identités',
    title: 'Protéger chaque accès sensible de votre PME.',
  },
  {
    src: '/images/login/cyber-security.jpg',
    alt: 'Réseau numérique illustrant la cybersécurité',
    label: 'Veille continue',
    title: 'Garder une longueur d’avance, même avec une petite équipe.',
  },
] as const

export function Login() {
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [activeScene, setActiveScene] = useState(0)
  const [isPlaying, setIsPlaying] = useState(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return true
    return !window.matchMedia('(prefers-reduced-motion: reduce)').matches
  })

  useEffect(() => {
    if (!isPlaying) return undefined
    const timer = window.setInterval(() => {
      setActiveScene((current) => (current + 1) % LOGIN_SCENES.length)
    }, 7000)
    return () => window.clearInterval(timer)
  }, [isPlaying])

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

  const moveScene = (event: ReactPointerEvent<HTMLElement>) => {
    if (event.pointerType === 'touch') return
    const bounds = event.currentTarget.getBoundingClientRect()
    const x = ((event.clientX - bounds.left) / bounds.width - 0.5) * 18
    const y = ((event.clientY - bounds.top) / bounds.height - 0.5) * 18
    event.currentTarget.style.setProperty('--scene-x', `${x}px`)
    event.currentTarget.style.setProperty('--scene-y', `${y}px`)
  }

  const resetScene = (event: ReactPointerEvent<HTMLElement>) => {
    event.currentTarget.style.setProperty('--scene-x', '0px')
    event.currentTarget.style.setProperty('--scene-y', '0px')
  }

  const scene = LOGIN_SCENES[activeScene]

  return (
    <main className="grid min-h-screen bg-canvas lg:grid-cols-[1.12fr_0.88fr]">
      <section
        className="login-visual-panel relative flex min-h-[23rem] overflow-hidden bg-ink p-6 text-white sm:min-h-[27rem] sm:p-10 lg:min-h-screen lg:p-12"
        aria-label="Présentation de Sentinel PME"
        onPointerMove={moveScene}
        onPointerLeave={resetScene}
      >
        <div className="absolute inset-0">
          {LOGIN_SCENES.map((item, index) => (
            <img
              key={item.src}
              src={item.src}
              alt={index === activeScene ? item.alt : ''}
              data-login-scene
              aria-hidden={index !== activeScene}
              className={`login-scene ${index === activeScene ? 'login-scene--active' : ''}`}
            />
          ))}
          <div className="login-scene-overlay absolute inset-0" aria-hidden="true" />
          <div className="login-scan-line absolute inset-x-0 top-0" aria-hidden="true" />
        </div>

        <div className="relative z-10 flex w-full flex-col justify-between">
          <div className="flex items-center gap-3">
            <span className="grid h-11 w-11 place-items-center rounded-xl bg-lime text-ink shadow-[0_12px_30px_rgba(184,255,60,0.16)]">
              <ShieldCheck className="h-6 w-6" strokeWidth={2.5} />
            </span>
            <div>
              <p className="font-black">Sentinel PME</p>
              <p className="text-xs text-slate-300">Veille cyber simplifiée</p>
            </div>
          </div>

          <div className="max-w-xl py-8 lg:py-12">
            <div className="mb-4 flex items-center gap-3">
              <span className="h-px w-9 bg-lime" />
              <p className="text-[11px] font-black uppercase tracking-[0.22em] text-lime">
                Pensé pour les petites équipes
              </p>
            </div>
            <h1 className="max-w-lg text-balance text-3xl font-black leading-tight sm:text-4xl lg:text-5xl">
              Comprendre le risque, puis agir sans perdre de temps.
            </h1>
            <ul className="mt-7 hidden space-y-3.5 text-sm text-slate-200 sm:block">
              <li className="flex items-center gap-3"><CheckCircle2 className="h-5 w-5 shrink-0 text-lime" /> Indicateurs centralisés et classés par priorité</li>
              <li className="flex items-center gap-3"><CheckCircle2 className="h-5 w-5 shrink-0 text-lime" /> Score expliqué avec des actions concrètes</li>
              <li className="flex items-center gap-3"><CheckCircle2 className="h-5 w-5 shrink-0 text-lime" /> Suivi des alertes dans une vue SOC légère</li>
            </ul>
          </div>

          <div className="flex items-end justify-between gap-4">
            <div className="min-w-0">
              <p className="text-[10px] font-black uppercase tracking-[0.2em] text-lime">
                {String(activeScene + 1).padStart(2, '0')} / {String(LOGIN_SCENES.length).padStart(2, '0')} · {scene.label}
              </p>
              <p className="mt-1 hidden max-w-md text-sm font-semibold leading-snug text-white/90 sm:block">
                {scene.title}
              </p>
            </div>

            <div className="flex shrink-0 items-center gap-2" aria-label="Choisir une scène">
              {LOGIN_SCENES.map((item, index) => (
                <button
                  key={item.label}
                  type="button"
                  aria-label={`Afficher la scène ${item.label}`}
                  aria-pressed={activeScene === index}
                  onClick={() => setActiveScene(index)}
                  className={`login-scene-control ${activeScene === index ? 'login-scene-control--active' : ''}`}
                >
                  <span className="sr-only">{item.label}</span>
                </button>
              ))}
              <button
                type="button"
                onClick={() => setIsPlaying((playing) => !playing)}
                className="ml-1 grid h-9 w-9 place-items-center rounded-full border border-white/30 bg-black/20 text-white transition hover:border-lime hover:text-lime"
                aria-label={isPlaying ? 'Mettre le diaporama en pause' : 'Relancer le diaporama'}
              >
                {isPlaying ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
              </button>
            </div>
          </div>
        </div>
      </section>

      <section className="login-form-panel flex items-center justify-center p-6 sm:p-10">
        <form onSubmit={onSubmit} className="login-form-card w-full max-w-sm rounded-2xl border border-slate-200/80 bg-white p-7 shadow-[0_28px_70px_rgba(24,35,31,0.09)] sm:p-8">
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
              className="mt-1.5 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-emerald focus:ring-4 focus:ring-emerald/10"
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
              className="mt-1.5 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-emerald focus:ring-4 focus:ring-emerald/10"
              placeholder="••••••••"
            />
          </label>
          {error && <p className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm font-semibold text-red-700" role="alert">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="group flex w-full items-center justify-center gap-2 rounded-lg bg-ink px-5 py-3 text-sm font-bold text-white transition hover:-translate-y-0.5 hover:bg-emerald hover:shadow-lg disabled:cursor-wait disabled:opacity-60"
          >
            <LogIn className="h-4 w-4 transition-transform group-hover:translate-x-0.5" /> {loading ? 'Connexion…' : 'Se connecter'}
          </button>
          <p className="mt-5 text-center text-[11px] leading-relaxed text-slate-400">
            Accès réservé aux utilisateurs autorisés · Connexion journalisée
          </p>
        </form>
      </section>
    </main>
  )
}
