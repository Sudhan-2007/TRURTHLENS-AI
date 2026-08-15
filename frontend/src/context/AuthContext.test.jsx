import { act, renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from '../api/client'
import { AuthProvider, useAuth } from './AuthContext'

vi.mock('../api/client', () => ({
  api: {
    me: vi.fn(),
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    updateMe: vi.fn(),
  },
}))

const USER = { email: 'a@example.com', name: 'Ada' }

function renderAuth() {
  return renderHook(() => useAuth(), { wrapper: AuthProvider })
}

describe('AuthProvider', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    window.dispatchEvent(new Event('auth:unauthorized'))
  })

  it('resolves to a logged-out state when no token exists', async () => {
    const { result } = renderAuth()
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.user).toBeNull()
  })

  it('restores the user from an existing token', async () => {
    localStorage.setItem('token', 'abc')
    vi.mocked(api.me).mockResolvedValue(USER)
    const { result } = renderAuth()
    await waitFor(() => expect(result.current.user).toEqual(USER))
    expect(result.current.loading).toBe(false)
  })

  it('clears a stale token when the profile fetch fails', async () => {
    localStorage.setItem('token', 'stale')
    vi.mocked(api.me).mockRejectedValue(new Error('401'))
    const { result } = renderAuth()
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(localStorage.getItem('token')).toBeNull()
    expect(result.current.user).toBeNull()
  })

  it('clears the user on an auth:unauthorized event', async () => {
    localStorage.setItem('token', 'abc')
    vi.mocked(api.me).mockResolvedValue(USER)
    const { result } = renderAuth()
    await waitFor(() => expect(result.current.user).toEqual(USER))
    act(() => {
      window.dispatchEvent(new Event('auth:unauthorized'))
    })
    await waitFor(() => expect(result.current.user).toBeNull())
  })

  it('logs in, stores the token, and loads the profile', async () => {
    vi.mocked(api.login).mockResolvedValue({ access_token: 'tok' })
    vi.mocked(api.me).mockResolvedValue(USER)
    const { result } = renderAuth()
    await waitFor(() => expect(result.current.loading).toBe(false))
    let returned
    await act(async () => {
      returned = await result.current.login('a@example.com', 'pw')
    })
    expect(localStorage.getItem('token')).toBe('tok')
    expect(result.current.user).toEqual(USER)
    expect(returned).toEqual(USER)
  })

  it('registers and returns the user id', async () => {
    vi.mocked(api.register).mockResolvedValue({ user_id: 'u1' })
    const { result } = renderAuth()
    await waitFor(() => expect(result.current.loading).toBe(false))
    let id
    await act(async () => {
      id = await result.current.register('Ada', 'a@example.com', 'pw')
    })
    expect(id).toBe('u1')
  })

  it('logs out and clears state even if the server call fails', async () => {
    vi.mocked(api.logout).mockRejectedValue(new Error('down'))
    const { result } = renderAuth()
    await waitFor(() => expect(result.current.loading).toBe(false))
    await act(async () => {
      await result.current.logout()
    })
    expect(localStorage.getItem('token')).toBeNull()
    expect(result.current.user).toBeNull()
  })

  it('updates the profile and refreshes the user', async () => {
    vi.mocked(api.updateMe).mockResolvedValue({ ...USER, name: 'Grace' })
    const { result } = renderAuth()
    await waitFor(() => expect(result.current.loading).toBe(false))
    let updated
    await act(async () => {
      updated = await result.current.updateProfile({ name: 'Grace' })
    })
    expect(updated.name).toBe('Grace')
    expect(result.current.user.name).toBe('Grace')
  })

  it('throws when used outside the provider', () => {
    expect(() => renderHook(() => useAuth())).toThrow(
      'useAuth must be used within AuthProvider',
    )
  })
})
