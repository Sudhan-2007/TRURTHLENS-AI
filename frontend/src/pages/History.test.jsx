import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from '../api/client'
import History from './History'

vi.mock('../api/client', () => ({
  api: {
    getHistory: vi.fn(),
    deleteSubmission: vi.fn(),
  },
}))

function renderHistory() {
  return render(
    <MemoryRouter>
      <History />
    </MemoryRouter>,
  )
}

const ITEMS = [
  {
    submission_id: 'TL-1',
    status: 'completed',
    created_at: '2026-01-01T00:00:00Z',
    input_type: 'text',
    content: 'Some content',
    ai_prediction: 'REAL',
    verification_status: 'SUPPORTED',
    trust_level: 'HIGH',
    final_score: 85,
  },
]

describe('History', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows a loading state on first load', () => {
    api.getHistory.mockReturnValue(new Promise(() => {}))
    renderHistory()
    expect(screen.getByText('Loading history...')).toBeInTheDocument()
  })

  it('renders history items and the total', async () => {
    api.getHistory.mockResolvedValue({ items: ITEMS, total: 1 })
    renderHistory()
    await waitFor(() => expect(screen.getByText('TL-1')).toBeInTheDocument())
    expect(screen.getByText('1 submission(s)')).toBeInTheDocument()
  })

  it('shows an error when loading fails', async () => {
    api.getHistory.mockRejectedValue(new Error('boom'))
    renderHistory()
    await waitFor(() => expect(screen.getByText('boom')).toBeInTheDocument())
  })

  it('applies the search term on submit', async () => {
    api.getHistory.mockResolvedValue({ items: [], total: 0 })
    renderHistory()
    await waitFor(() => expect(api.getHistory).toHaveBeenCalledTimes(1))
    fireEvent.change(screen.getByPlaceholderText('Search content or URL'), {
      target: { value: 'climate' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Search' }))
    await waitFor(() =>
      expect(api.getHistory).toHaveBeenCalledWith(
        expect.objectContaining({ search: 'climate' }),
      ),
    )
  })

  it('deletes a submission after confirmation', async () => {
    api.getHistory.mockResolvedValue({ items: ITEMS, total: 1 })
    api.deleteSubmission.mockResolvedValue(null)
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    renderHistory()
    await waitFor(() => expect(screen.getByText('TL-1')).toBeInTheDocument())

    fireEvent.click(screen.getByText('Delete'))
    await waitFor(() => expect(api.deleteSubmission).toHaveBeenCalledWith('TL-1'))
  })

  it('shows pagination when there is more than one page', async () => {
    const many = Array.from({ length: 20 }, (_, i) => ({
      submission_id: `TL-${i}`,
      status: 'completed',
      created_at: '2026-01-01T00:00:00Z',
    }))
    api.getHistory.mockResolvedValue({ items: many, total: 25 })
    renderHistory()
    await waitFor(() => expect(screen.getByText('Page 1 of 2')).toBeInTheDocument())
    fireEvent.click(screen.getByText('Next'))
    await waitFor(() => expect(screen.getByText('Page 2 of 2')).toBeInTheDocument())
  })
})
