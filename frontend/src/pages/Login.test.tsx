import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as client from '../api/client'
import { AuthProvider } from '../auth/AuthContext'
import { Login } from './Login'

vi.mock('../api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/client')>()
  return { ...actual, login: vi.fn() }
})

describe('Login', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('affiche une erreur si les identifiants sont invalides', async () => {
    vi.mocked(client.login).mockRejectedValueOnce(new Error('unauthorized'))
    render(
      <MemoryRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </MemoryRouter>,
    )

    await userEvent.type(screen.getByLabelText(/email/i), 'admin@pme-cyber.local')
    await userEvent.type(screen.getByLabelText(/mot de passe/i), 'wrong')
    await userEvent.click(screen.getByRole('button', { name: /se connecter/i }))

    expect(await screen.findByText(/email ou mot de passe incorrect/i)).toBeInTheDocument()
  })

  it("connecte l'utilisateur avec des identifiants valides", async () => {
    vi.mocked(client.login).mockResolvedValueOnce({
      access_token: 'token-123',
      token_type: 'bearer',
      role: 'admin',
      email: 'admin@pme-cyber.local',
    })
    render(
      <MemoryRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </MemoryRouter>,
    )

    await userEvent.type(screen.getByLabelText(/email/i), 'admin@pme-cyber.local')
    await userEvent.type(screen.getByLabelText(/mot de passe/i), 'ChangeMe123!')
    await userEvent.click(screen.getByRole('button', { name: /se connecter/i }))

    await waitFor(() =>
      expect(client.login).toHaveBeenCalledWith('admin@pme-cyber.local', 'ChangeMe123!'),
    )
  })

  it('permet de parcourir les trois scènes de cybersécurité', async () => {
    const { container } = render(
      <MemoryRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </MemoryRouter>,
    )

    expect(container.querySelectorAll('[data-login-scene]')).toHaveLength(3)
    expect(screen.getByRole('button', { name: /mettre le diaporama en pause/i })).toBeInTheDocument()

    const identityScene = screen.getByRole('button', {
      name: /afficher la scène protection des identités/i,
    })
    await userEvent.click(identityScene)

    expect(identityScene).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByText(/protéger chaque accès sensible/i)).toBeInTheDocument()
  })
})
