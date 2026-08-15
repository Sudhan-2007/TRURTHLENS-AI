import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, useNavigate } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import Register from './Register'
import { useAuth } from '../context/AuthContext'

vi.mock('../context/AuthContext', () => ({ useAuth: vi.fn() }))
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, useNavigate: vi.fn() }
})

function fillForm(name, email, password, confirm) {
  fireEvent.change(screen.getByLabelText('Name'), { target: { value: name } })
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: email } })
  fireEvent.change(screen.getByLabelText('Password'), { target: { value: password } })
  fireEvent.change(screen.getByLabelText('Confirm password'), {
    target: { value: confirm },
  })
}

function renderRegister() {
  return render(
    <MemoryRouter>
      <Register />
    </MemoryRouter>,
  )
}

describe('Register', () => {
  it('registers, logs in, and navigates to the profile', async () => {
    const register = vi.fn().mockResolvedValue({ user_id: 'u1' })
    const login = vi.fn().mockResolvedValue({ email: 'a@example.com' })
    useAuth.mockReturnValue({ register, login })
    const navigate = vi.fn()
    useNavigate.mockReturnValue(navigate)

    renderRegister()
    fillForm('Ada', 'a@example.com', 'password123', 'password123')
    fireEvent.click(screen.getByRole('button', { name: 'Create account' }))

    await waitFor(() =>
      expect(register).toHaveBeenCalledWith('Ada', 'a@example.com', 'password123'),
    )
    expect(login).toHaveBeenCalledWith('a@example.com', 'password123')
    expect(navigate).toHaveBeenCalledWith('/profile')
  })

  it('rejects mismatched passwords without calling the api', () => {
    const register = vi.fn()
    useAuth.mockReturnValue({ register, login: vi.fn() })
    useNavigate.mockReturnValue(vi.fn())

    renderRegister()
    fillForm('Ada', 'a@example.com', 'password123', 'different')
    fireEvent.click(screen.getByRole('button', { name: 'Create account' }))

    expect(screen.getByText('Passwords do not match')).toBeInTheDocument()
    expect(register).not.toHaveBeenCalled()
  })

  it('shows the error returned by the api', async () => {
    const register = vi
      .fn()
      .mockRejectedValue(new Error('An account with this email already exists'))
    useAuth.mockReturnValue({ register, login: vi.fn() })
    useNavigate.mockReturnValue(vi.fn())

    renderRegister()
    fillForm('Ada', 'a@example.com', 'password123', 'password123')
    fireEvent.click(screen.getByRole('button', { name: 'Create account' }))

    await waitFor(() =>
      expect(
        screen.getByText('An account with this email already exists'),
      ).toBeInTheDocument(),
    )
  })
})
