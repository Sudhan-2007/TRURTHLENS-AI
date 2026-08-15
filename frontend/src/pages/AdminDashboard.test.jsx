import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { api } from '../api/client'
import AdminDashboard from './AdminDashboard'
import { useAuth } from '../context/AuthContext'

vi.mock('../api/client', () => ({
  api: {
    getAdminDashboard: vi.fn(),
    getAdminStatistics: vi.fn(),
    listSources: vi.fn(),
    listUsers: vi.fn(),
    healthDb: vi.fn(),
  },
}))
vi.mock('../context/AuthContext', () => ({ useAuth: vi.fn() }))

const OVERVIEW = {
  total_users: 10,
  active_users: 8,
  total_submissions: 40,
  completed_verifications: 30,
  failed_verifications: 1,
  fake_predictions: 5,
  real_predictions: 25,
  unverified_claims: 4,
  average_trust_score: 72,
  official_sources: 14,
}

const STATS = {
  verification_distribution: [{ value: 'SUPPORTED', count: 10 }],
  prediction_distribution: [{ value: 'REAL', count: 25 }],
  trust_score_distribution: [{ value: 'HIGH', count: 12 }],
  verification_trend: { daily: [{ period: '2026-01-01', count: 2 }] },
}

const SOURCES = [
  {
    name: 'WHO',
    domain: 'who.int',
    category: 'Health',
    source_type: 'official',
    trust_level: 'high',
  },
]

const USERS = [
  { id: 'u1', name: 'Ada', email: 'ada@example.com', role: 'admin', created_at: '2026-01-01T00:00:00Z' },
]

function renderAdmin(route = '/admin') {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <Routes>
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/dashboard" element={<div>user dashboard</div>} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('AdminDashboard', () => {
  it('redirects non-admin users to the user dashboard', () => {
    useAuth.mockReturnValue({ user: { role: 'user' } })
    renderAdmin()
    expect(screen.getByText('user dashboard')).toBeInTheDocument()
  })

  it('shows a loading state', () => {
    useAuth.mockReturnValue({ user: { role: 'admin' } })
    api.getAdminDashboard.mockReturnValue(new Promise(() => {}))
    api.getAdminStatistics.mockReturnValue(new Promise(() => {}))
    api.listSources.mockReturnValue(new Promise(() => {}))
    api.listUsers.mockReturnValue(new Promise(() => {}))
    api.healthDb.mockReturnValue(new Promise(() => {}))
    renderAdmin()
    expect(screen.getByText('Loading admin dashboard...')).toBeInTheDocument()
  })

  it('shows an error when loading fails', async () => {
    useAuth.mockReturnValue({ user: { role: 'admin' } })
    api.getAdminDashboard.mockRejectedValue(new Error('admin down'))
    api.getAdminStatistics.mockResolvedValue(STATS)
    api.listSources.mockResolvedValue(SOURCES)
    api.listUsers.mockResolvedValue(USERS)
    api.healthDb.mockResolvedValue(null)
    renderAdmin()
    await waitFor(() => expect(screen.getByText('admin down')).toBeInTheDocument())
  })

  it('renders the system overview, health, and tables', async () => {
    useAuth.mockReturnValue({ user: { role: 'admin' } })
    api.getAdminDashboard.mockResolvedValue(OVERVIEW)
    api.getAdminStatistics.mockResolvedValue(STATS)
    api.listSources.mockResolvedValue(SOURCES)
    api.listUsers.mockResolvedValue(USERS)
    api.healthDb.mockResolvedValue({ connected: true, mode: 'local', database: 'truthlens' })

    renderAdmin()
    await waitFor(() =>
      expect(screen.getByText('Admin dashboard')).toBeInTheDocument(),
    )
    expect(screen.getByText('Total users')).toBeInTheDocument()
    expect(screen.getAllByText('Database').length).toBeGreaterThan(0)
    expect(screen.getByText('WHO')).toBeInTheDocument()
    expect(screen.getByText('who.int')).toBeInTheDocument()
    expect(screen.getByText('Ada')).toBeInTheDocument()
    expect(screen.getByText('ada@example.com')).toBeInTheDocument()
  })
})
