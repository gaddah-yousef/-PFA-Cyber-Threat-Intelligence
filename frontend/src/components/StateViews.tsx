import { LoaderCircle, RadioTower } from 'lucide-react'

export function LoadingState({ label = 'Chargement des signaux…' }: { label?: string }) {
  return (
    <div className="flex min-h-64 items-center justify-center text-slate-500" role="status" aria-live="polite">
      <LoaderCircle className="mr-3 h-5 w-5 animate-spin" aria-hidden="true" /> {label}
    </div>
  )
}

export function ErrorState({ message = 'L’API ne répond pas.' }: { message?: string }) {
  return (
    <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-800" role="alert">
      <div className="mb-2 flex items-center gap-2 font-bold"><RadioTower className="h-5 w-5" aria-hidden="true" /> Connexion interrompue</div>
      <p className="text-sm leading-relaxed">{message} Vérifiez que le backend écoute sur le port 8000, puis actualisez la page.</p>
    </div>
  )
}
