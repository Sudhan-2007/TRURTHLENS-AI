import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import App from './App'
import { useAuth } from './context/AuthContext'

vi.mock('./context/AuthContext', () => ({ useAuth: vi.fn() }))
vi.mock('./api/client', () => ({ api: {} }))

function renderApp(path) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  )
}

describe('App routes', () => {
  it('renders the home page at /', () => {
    useAuth.mockReturnValue({ user: null, loading: false })
    renderApp('/')
    expect(
      screen.getByRole('heading', {
        name: /Verify the truth before you share it/i,
      }),
    ).toBeInTheDocument()
  })

  it('renders the login page at /login', () => {
    useAuth.mockReturnValue({ user: null, loading: false })
    renderApp('/login')
    expect(screen.getByText('Welcome back')).toBeInTheDocument()
  })

  it('redirects unknown routes to the home page', () => {
    useAuth.mockReturnValue({ user: null, loading: false })
    renderApp('/does-not-exist')
    expect(
      screen.getByRole('heading', {
        name: /Verify the truth before you share it/i,
      }),
    ).toBeInTheDocument()
  })

  it('redirects protected routes to login when unauthenticated', () => {
    useAuth.mockReturnValue({ user: null, loading: false })
    renderApp('/profile')
    expect(screen.getByText('Welcome back')).toBeInTheDocument()
  })

  it('renders protected content when authenticated', () => {
    useAuth.mockReturnValue({ user: { email: 'a@example.com' }, loading: false })
    renderApp('/profile')
    expect(screen.getByRole('heading', { name: 'Profile' })).toBeInTheDocument()
  })
})
