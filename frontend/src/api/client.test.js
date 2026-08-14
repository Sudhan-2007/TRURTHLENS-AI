import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from './client'

function mockFetch(status, body = {}, ok = status < 400) {
  const res = {
    ok,
    status,
    json: vi.fn().mockResolvedValue(body),
  }
  global.fetch = vi.fn().mockResolvedValue(res)
  return res
}

function listenForUnauthorized() {
  const listener = vi.fn()
  window.addEventListener('auth:unauthorized', listener)
  return () => window.removeEventListener('auth:unauthorized', listener)
}

describe('api client', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('attaches the bearer token from localStorage', async () => {
    localStorage.setItem('token', 'abc123')
    mockFetch(200, { ok: true })
    await api.me()
    const [, options] = global.fetch.mock.calls[0]
    expect(options.headers.Authorization).toBe('Bearer abc123')
  })

  it('returns parsed JSON on success', async () => {
    mockFetch(200, { email: 'u@example.com' })
    const data = await api.me()
    expect(data).toEqual({ email: 'u@example.com' })
  })

  it('returns null for 204 responses', async () => {
    const res = mockFetch(204)
    res.json = vi.fn().mockRejectedValue(new Error('no body'))
    const data = await api.logout()
    expect(data).toBeNull()
  })

  it('throws a readable error and invalidates the session on 401', async () => {
    mockFetch(401, { detail: 'Invalid or expired token' }, false)
    const off = listenForUnauthorized()
    localStorage.setItem('token', 'stale')
    await expect(api.me()).rejects.toThrow('Invalid or expired token')
    expect(localStorage.getItem('token')).toBeNull()
    off()
  })

  it('dispatches auth:unauthorized on a stale session', async () => {
    mockFetch(401, { detail: 'nope' }, false)
    const off = listenForUnauthorized()
    await expect(api.me()).rejects.toThrow('nope')
    off()
  })

  it('does not invalidate the session on a login 401', async () => {
    mockFetch(401, { detail: 'Incorrect email or password' }, false)
    const listener = vi.fn()
    window.addEventListener('auth:unauthorized', listener)
    localStorage.setItem('token', 'keepme')
    await expect(api.login({ email: 'x@example.com', password: 'wrong' })).rejects.toThrow(
      'Incorrect email or password',
    )
    expect(listener).not.toHaveBeenCalled()
    expect(localStorage.getItem('token')).toBe('keepme')
  })

  it('joins validation detail arrays into one message', async () => {
    mockFetch(
      422,
      {
        detail: [{ msg: 'email is not valid' }, { msg: 'password too weak' }],
      },
      false,
    )
    await expect(api.register({})).rejects.toThrow('email is not valid, password too weak')
  })
})
