import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import Navbar from '../Navbar'
import { useAuth } from '../../context/AuthContext'

vi.mock('../../context/AuthContext', () => ({
  useAuth: vi.fn(),
}))

function renderNav() {
  return render(
    <MemoryRouter>
      <Navbar />
    </MemoryRouter>,
  )
}

describe('Navbar', () => {
  it('shows sign-in and get-started links when logged out', () => {
    useAuth.mockReturnValue({ user: null, logout: vi.fn() })
    renderNav()
    expect(screen.getByText('Sign in')).toBeInTheDocument()
    expect(screen.getByText('Get started')).toBeInTheDocument()
    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument()
  })

  it('shows core navigation links when logged in', () => {
    useAuth.mockReturnValue({
      user: { email: 'u@example.com', role: 'user' },
      logout: vi.fn(),
    })
    renderNav()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Verify news')).toBeInTheDocument()
    expect(screen.getByText('History')).toBeInTheDocument()
    expect(screen.queryByText('Admin')).not.toBeInTheDocument()
  })

  it('shows the Admin link only for admins', () => {
    useAuth.mockReturnValue({
      user: { email: 'a@example.com', role: 'admin' },
      logout: vi.fn(),
    })
    renderNav()
    expect(screen.getByText('Admin')).toBeInTheDocument()
  })

  it('calls logout on click', () => {
    const logout = vi.fn().mockResolvedValue(undefined)
    useAuth.mockReturnValue({ user: { email: 'u@example.com', role: 'user' }, logout })
    renderNav()
    fireEvent.click(screen.getByText('Log out'))
    expect(logout).toHaveBeenCalledTimes(1)
  })
})
