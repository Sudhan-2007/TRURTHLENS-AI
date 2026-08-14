import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import ProtectedRoute from '../ProtectedRoute'
import { useAuth } from '../../context/AuthContext'

vi.mock('../../context/AuthContext', () => ({
  useAuth: vi.fn(),
}))

function renderRoute() {
  return render(
    <MemoryRouter>
      <ProtectedRoute>
        <div>protected content</div>
      </ProtectedRoute>
    </MemoryRouter>,
  )
}

describe('ProtectedRoute', () => {
  it('shows a loading state while the session is resolving', () => {
    useAuth.mockReturnValue({ user: null, loading: true })
    renderRoute()
    expect(screen.getByText('Loading...')).toBeInTheDocument()
    expect(screen.queryByText('protected content')).not.toBeInTheDocument()
  })

  it('redirects to login when unauthenticated', () => {
    useAuth.mockReturnValue({ user: null, loading: false })
    renderRoute()
    expect(screen.queryByText('protected content')).not.toBeInTheDocument()
  })

  it('renders children when authenticated', () => {
    useAuth.mockReturnValue({ user: { email: 'a@example.com' }, loading: false })
    renderRoute()
    expect(screen.getByText('protected content')).toBeInTheDocument()
  })
})
