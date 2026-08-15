import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import RecentActivity from './RecentActivity'

describe('RecentActivity', () => {
  it('shows an empty message', () => {
    render(
      <MemoryRouter>
        <RecentActivity items={[]} />
      </MemoryRouter>,
    )
    expect(screen.getByText('No recent verifications yet.')).toBeInTheDocument()
  })

  it('renders items with verdict and trust badges', () => {
    const items = [
      {
        submission_id: 'TL-1',
        created_at: '2026-01-01T00:00:00Z',
        input_type: 'text',
        content: 'Some recent claim text',
        ai_prediction: 'REAL',
        trust_level: 'HIGH',
      },
    ]
    render(
      <MemoryRouter>
        <RecentActivity items={items} />
      </MemoryRouter>,
    )
    expect(screen.getByText('Some recent claim text')).toBeInTheDocument()
    expect(screen.getByText('REAL')).toBeInTheDocument()
    expect(screen.getByText('HIGH')).toBeInTheDocument()
  })

  it('links each item to its result page', () => {
    const items = [
      {
        submission_id: 'TL-2',
        created_at: '2026-01-01T00:00:00Z',
        input_type: 'url',
        url: 'https://example.com/news',
      },
    ]
    render(
      <MemoryRouter>
        <RecentActivity items={items} />
      </MemoryRouter>,
    )
    expect(screen.getByText('https://example.com/news')).toBeInTheDocument()
    expect(screen.getByRole('link')).toHaveAttribute('href', '/result/TL-2')
  })
})
