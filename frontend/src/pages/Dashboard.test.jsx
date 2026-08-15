import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { api } from '../api/client'
import Dashboard from './Dashboard'

vi.mock('../api/client', () => ({
  api: { getUserDashboard: vi.fn(), getUserStatistics: vi.fn() },
}))

const OVERVIEW = {
  total_submissions: 5,
  completed_verifications: 4,
  fake_predictions: 1,
  real_predictions: 3,
  unverified_claims: 1,
  average_trust_score: 70,
  recent_verifications: [
    {
      submission_id: 'TL-1',
      created_at: '2026-01-01T00:00:00Z',
      input_type: 'text',
      content: 'Some recent claim',
      ai_prediction: 'REAL',
      trust_level: 'HIGH',
    },
  ],
}

const STATS = {
  trust_score_distribution: [{ value: 'HIGH', count: 3 }],
  verification_distribution: [{ value: 'SUPPORTED', count: 2 }],
  prediction_distribution: [{ value: 'REAL', count: 3 }],
  verification_trend: { daily: [{ period: '2026-01-01', count: 1 }] },
}

function renderDashboard() {
  return render(
    <MemoryRouter>
      <Dashboard />
    </MemoryRouter>,
  )
}

describe('Dashboard', () => {
  it('shows a loading state', () => {
    api.getUserDashboard.mockReturnValue(new Promise(() => {}))
    api.getUserStatistics.mockReturnValue(new Promise(() => {}))
    renderDashboard()
    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument()
  })

  it('shows an error when loading fails', async () => {
    api.getUserDashboard.mockRejectedValue(new Error('dashboard down'))
    api.getUserStatistics.mockResolvedValue(STATS)
    renderDashboard()
    await waitFor(() => expect(screen.getByText('dashboard down')).toBeInTheDocument())
  })

  it('renders the overview stats and charts', async () => {
    api.getUserDashboard.mockResolvedValue(OVERVIEW)
    api.getUserStatistics.mockResolvedValue(STATS)
    renderDashboard()
    await waitFor(() => expect(screen.getByText('Dashboard')).toBeInTheDocument())
    expect(screen.getByText('Submissions')).toBeInTheDocument()
    expect(screen.getByText('Trust score distribution')).toBeInTheDocument()
    expect(screen.getByText('Verification distribution')).toBeInTheDocument()
    expect(screen.getByText('AI prediction distribution')).toBeInTheDocument()
    expect(screen.getByText('Verification trend')).toBeInTheDocument()
    expect(screen.getByText('Some recent claim')).toBeInTheDocument()
  })
})
