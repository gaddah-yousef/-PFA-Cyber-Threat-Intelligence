import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { Users } from './Users'

const { getUsers, createUser, updateUser } = vi.hoisted(() => ({
  getUsers: vi.fn(),
  createUser: vi.fn(),
  updateUser: vi.fn(),
}))

vi.mock('../api/client', () => ({ getUsers, createUser, updateUser }))

describe('Users', () => {
  beforeEach(() => {
    getUsers.mockResolvedValue([])
    createUser.mockReset()
    updateUser.mockReset()
  })

  it('crée un compte depuis le formulaire administrateur', async () => {
    createUser.mockResolvedValue({
      id: 'u1', email: 'analyste@test.local', role: 'analyst', is_active: true,
      created_at: '2026-10-15T00:00:00Z',
    })
    render(<Users />)
    const user = userEvent.setup()
    await screen.findByText('Nouveau compte')
    await user.type(screen.getByLabelText('Email'), 'analyste@test.local')
    await user.type(screen.getByLabelText('Mot de passe temporaire'), 'SuperSecret1')
    await user.selectOptions(screen.getByLabelText('Rôle'), 'analyst')
    await user.click(screen.getByRole('button', { name: 'Créer le compte' }))

    await waitFor(() => expect(createUser).toHaveBeenCalledWith({
      email: 'analyste@test.local', password: 'SuperSecret1', role: 'analyst',
    }))
    expect(await screen.findByText('analyste@test.local')).toBeInTheDocument()
  })
})
