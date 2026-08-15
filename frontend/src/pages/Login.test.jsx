import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, useNavigate } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import Login from './Login'
import { useAuth } from '../context/AuthContext'

vi.mock('../context/AuthContext', () => ({ useAuth: vi.fn() }))
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, useNavigate: vi.fn() }
})

function renderLogin() {
  return render(
    <MemoryRouter>
      <Login />
    </MemoryRouter>,
  )
}

describe('Login', () => {
  it('logs in and navigates to the profile', async () => {
    const login = vi.fn().mockResolvedValue({ email: 'a@example.com' })
    useAuth.mockReturnValue({ login })
    const navigate = vi.fn()
    useNavigate.mockReturnValue(navigate)

    renderLogin()
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'a@example.com' },
    })
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: 'password123' },
    })
    fireEvent.click(screen.getByText('Sign in'))

    await waitFor(() => expect(login).toHaveBeenCalledWith('a@example.com', 'password123'))
    expect(navigate).toHaveBeenCalledWith('/profile')
  })

  it('shows a loading state while signing in', async () => {
    let resolveLogin
    const login = vi.fn(() => new Promise((resolve) => { resolveLogin = resolve }))
    useAuth.mockReturnValue({ login })
    useNavigate.mockReturnValue(vi.fn())

    renderLogin()
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'a@example.com' },
    })
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: 'password123' },
    })
    fireEvent.click(screen.getByText('Sign in'))

    expect(screen.getByText('Signing in...')).toBeInTheDocument()
    resolveLogin({})
    await waitFor(() => expect(screen.getByText('Sign in')).toBeInTheDocument())
  })

  it('renders the login error message', async () => {
    const login = vi.fn().mockRejectedValue(new Error('Incorrect email or password'))
    useAuth.mockReturnValue({ login })
    useNavigate.mockReturnValue(vi.fn())

    renderLogin()
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'a@example.com' },
    })
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: 'wrong' },
    })
    fireEvent.click(screen.getByText('Sign in'))

    await waitFor(() =>
      expect(screen.getByText('Incorrect email or password')).toBeInTheDocument(),
    )
  })
})
