import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import Profile from './Profile'
import { useAuth } from '../context/AuthContext'

vi.mock('../context/AuthContext', () => ({ useAuth: vi.fn() }))

const USER = {
  name: 'Ada',
  email: 'ada@example.com',
  role: 'user',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

describe('Profile', () => {
  it('renders nothing when there is no user', () => {
    useAuth.mockReturnValue({ user: null })
    const { container } = render(<Profile />)
    expect(container).toBeEmptyDOMElement()
  })

  it('prefills the form and saves profile changes', async () => {
    const updateProfile = vi.fn().mockResolvedValue({ ...USER, name: 'Grace' })
    const logout = vi.fn()
    useAuth.mockReturnValue({ user: USER, updateProfile, logout })

    render(<Profile />)
    expect(screen.getByLabelText('Name').value).toBe('Ada')
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Grace' } })
    fireEvent.click(screen.getByText('Save changes'))

    await waitFor(() =>
      expect(updateProfile).toHaveBeenCalledWith({ name: 'Grace', email: 'ada@example.com' }),
    )
    expect(screen.getByText('Profile updated successfully')).toBeInTheDocument()
  })

  it('shows the error when saving fails', async () => {
    const updateProfile = vi
      .fn()
      .mockRejectedValue(new Error('An account with this email already exists'))
    useAuth.mockReturnValue({
      user: USER,
      updateProfile,
      logout: vi.fn(),
    })

    render(<Profile />)
    fireEvent.click(screen.getByText('Save changes'))
    await waitFor(() =>
      expect(
        screen.getByText('An account with this email already exists'),
      ).toBeInTheDocument(),
    )
  })

  it('calls logout', () => {
    const logout = vi.fn()
    useAuth.mockReturnValue({ user: USER, updateProfile: vi.fn(), logout })
    render(<Profile />)
    fireEvent.click(screen.getByText('Log out'))
    expect(logout).toHaveBeenCalled()
  })
})
