const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function getToken() {
  return localStorage.getItem('token')
}

async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers })

  if (res.status === 204) return null

  const data = await res.json().catch(() => null)

  if (!res.ok) {
    const detail = data?.detail
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg).join(', ')
      : detail || `Request failed (${res.status})`
    throw new Error(message)
  }
  return data
}

export const api = {
  register: (payload) => request('/api/auth/register', { method: 'POST', body: JSON.stringify(payload) }),
  login: (payload) => request('/api/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  logout: () => request('/api/auth/logout', { method: 'POST' }),
  me: () => request('/api/users/me'),
  updateMe: (payload) => request('/api/users/me', { method: 'PUT', body: JSON.stringify(payload) }),
  submitText: (content) => request('/api/news/submit', { method: 'POST', body: JSON.stringify({ input_type: 'text', content }) }),
  submitUrl: (url) => request('/api/news/submit-url', { method: 'POST', body: JSON.stringify({ input_type: 'url', url }) }),
  getSubmission: (submissionId) => request(`/api/news/${submissionId}`),
  deleteSubmission: (submissionId) => request(`/api/news/${submissionId}`, { method: 'DELETE' }),
  listSubmissions: (limit = 20) => request(`/api/news/history?limit=${limit}`),
  modelInfo: () => request('/api/ai/model-info'),
  runVerification: (submissionId) => request(`/api/verification/${submissionId}`, { method: 'POST' }),
  getVerification: (submissionId) => request(`/api/verification/${submissionId}`),
  getEvidence: (submissionId) => request(`/api/verification/${submissionId}/evidence`),
  listSources: () => request('/api/sources'),
  runTrustScore: (submissionId) => request(`/api/trust-score/${submissionId}`, { method: 'POST' }),
  getTrustScore: (submissionId) => request(`/api/trust-score/${submissionId}`),
  runExplanation: (submissionId) => request(`/api/explanation/${submissionId}`, { method: 'POST' }),
  getExplanation: (submissionId) => request(`/api/explanation/${submissionId}`),
  getUserDashboard: () => request('/api/dashboard/user'),
  getUserStatistics: () => request('/api/dashboard/user/statistics'),
  getAdminDashboard: () => request('/api/dashboard/admin'),
  getAdminStatistics: () => request('/api/dashboard/admin/statistics'),
  getHistory: (params) => {
    const search = new URLSearchParams()
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined) search.set(key, value)
    })
    const qs = search.toString()
    return request(`/api/history${qs ? `?${qs}` : ''}`)
  },
  getHistoryDetail: (submissionId) => request(`/api/history/${submissionId}`),
  listUsers: () => request('/api/users'),
  healthDb: () => request('/api/health/db'),
}
