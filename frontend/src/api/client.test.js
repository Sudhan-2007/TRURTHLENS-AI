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

  it('falls back to a generic message when no detail is present', async () => {
    mockFetch(500, {}, false)
    await expect(api.me()).rejects.toThrow('Request failed (500)')
  })

  it('builds history queries without params', async () => {
    mockFetch(200, { items: [] })
    await api.getHistory()
    expect(global.fetch.mock.calls[0][0]).toContain('/api/history')
  })

  it('covers the remaining read endpoints', async () => {
    const calls = [
      [() => api.listSubmissions(5), '/api/news/history?limit=5'],
      [() => api.listSubmissions(), '/api/news/history?limit=20'],
      [() => api.getSubmission('TL-1'), '/api/news/TL-1'],
      [() => api.modelInfo(), '/api/ai/model-info'],
      [() => api.getVerification('TL-1'), '/api/verification/TL-1'],
      [() => api.getEvidence('TL-1'), '/api/verification/TL-1/evidence'],
      [() => api.listSources(), '/api/sources'],
      [() => api.getTrustScore('TL-1'), '/api/trust-score/TL-1'],
      [() => api.getExplanation('TL-1'), '/api/explanation/TL-1'],
      [() => api.getUserDashboard(), '/api/dashboard/user'],
      [() => api.getUserStatistics(), '/api/dashboard/user/statistics'],
      [() => api.getAdminDashboard(), '/api/dashboard/admin'],
      [() => api.getAdminStatistics(), '/api/dashboard/admin/statistics'],
      [() => api.getHistoryDetail('TL-1'), '/api/history/TL-1'],
      [() => api.listUsers(), '/api/users'],
      [() => api.healthDb(), '/api/health/db'],
      [() => api.getHistory({ prediction: 'REAL' }), '/api/history?prediction=REAL'],
      [() => api.getHistory({ prediction: 'REAL', search: '', limit: 20 }), '/api/history?prediction=REAL&limit=20'],
      [() => api.getHistory({}), '/api/history'],
    ]
    for (const [invoke, url] of calls) {
      mockFetch(200, { ok: true })
      await invoke()
      expect(global.fetch).toHaveBeenCalledTimes(1)
      expect(global.fetch.mock.calls[0][0]).toContain(url)
      const options = global.fetch.mock.calls[0][1] ?? {}
      expect(options.method ?? 'GET').toBe('GET')
    }
  })

  it('covers the remaining write endpoints', async () => {
    mockFetch(201, { submission_id: 'TL-1' })
    await api.submitText('some news text content')
    expect(global.fetch.mock.calls[0][0]).toContain('/api/news/submit')
    expect(global.fetch.mock.calls[0][1]).toMatchObject({ method: 'POST' })

    mockFetch(201, {})
    await api.submitUrl('https://example.com/news')
    expect(global.fetch.mock.calls[0][0]).toContain('/api/news/submit-url')
    expect(global.fetch.mock.calls[0][1]).toMatchObject({ method: 'POST' })

    mockFetch(200, {})
    await api.updateMe({ name: 'X' })
    expect(global.fetch.mock.calls[0][0]).toContain('/api/users/me')
    expect(global.fetch.mock.calls[0][1]).toMatchObject({ method: 'PUT' })

    mockFetch(204)
    expect(await api.deleteSubmission('TL-1')).toBeNull()
    expect(global.fetch.mock.calls[0][0]).toContain('/api/news/TL-1')
    expect(global.fetch.mock.calls[0][1]).toMatchObject({ method: 'DELETE' })

    mockFetch(200, {})
    await api.runVerification('TL-1')
    expect(global.fetch.mock.calls[0][0]).toContain('/api/verification/TL-1')
    expect(global.fetch.mock.calls[0][1]).toMatchObject({ method: 'POST' })

    mockFetch(200, {})
    await api.runTrustScore('TL-1')
    expect(global.fetch.mock.calls[0][0]).toContain('/api/trust-score/TL-1')
    expect(global.fetch.mock.calls[0][1]).toMatchObject({ method: 'POST' })

    mockFetch(200, {})
    await api.runExplanation('TL-1')
    expect(global.fetch.mock.calls[0][0]).toContain('/api/explanation/TL-1')
    expect(global.fetch.mock.calls[0][1]).toMatchObject({ method: 'POST' })
  })
})
