import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import HistoryTable from '../history/HistoryTable'

const items = [
  {
    submission_id: 'TL-001',
    created_at: '2026-08-14T10:00:00Z',
    ai_prediction: 'REAL',
    verification_status: 'SUPPORTED',
    trust_level: 'HIGH',
    status: 'completed',
    input_type: 'text',
    content: 'A sufficiently long sample article about a new scientific finding.',
  },
  {
    submission_id: 'TL-002',
    created_at: '2026-08-13T10:00:00Z',
    ai_prediction: null,
    verification_status: null,
    trust_level: null,
    status: 'processing',
    input_type: 'url',
    url: 'https://example.com/story',
  },
]

function renderTable(props) {
  return render(
    <MemoryRouter>
      <HistoryTable items={items} onDelete={vi.fn()} {...props} />
    </MemoryRouter>,
  )
}

describe('HistoryTable', () => {
  it('shows the empty state when there are no items', () => {
    render(
      <MemoryRouter>
        <HistoryTable items={[]} onDelete={vi.fn()} />
      </MemoryRouter>,
    )
    expect(screen.getByText('No submissions match your filters.')).toBeInTheDocument()
  })

  it('renders the column headers', () => {
    renderTable()
    ;['Submission', 'Date', 'Prediction', 'Verification', 'Trust', 'Status'].forEach(
      (header) => expect(screen.getByText(header)).toBeInTheDocument(),
    )
  })

  it('renders prediction and trust badges from item data', () => {
    renderTable()
    expect(screen.getByText('REAL')).toBeInTheDocument()
    expect(screen.getByText('HIGH')).toBeInTheDocument()
    expect(screen.getByText('SUPPORTED')).toBeInTheDocument()
  })

  it('links each submission to its result page', () => {
    renderTable()
    const link = screen.getByRole('link', { name: /TL-001/ })
    expect(link.getAttribute('href')).toBe('/result/TL-001')
  })

  it('calls onDelete with the item', () => {
    const onDelete = vi.fn()
    render(
      <MemoryRouter>
        <HistoryTable items={items} onDelete={onDelete} />
      </MemoryRouter>,
    )
    fireEvent.click(screen.getAllByText('Delete')[0])
    expect(onDelete).toHaveBeenCalledWith(items[0])
  })
})
