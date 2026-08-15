import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import VerificationChart from './VerificationChart'

describe('VerificationChart', () => {
  it('renders a no-data placeholder for empty data', () => {
    render(<VerificationChart type="pie" data={[]} />)
    expect(screen.getByText('No data')).toBeInTheDocument()
  })

  it('renders bars for the bar type', () => {
    render(<VerificationChart type="bar" data={[{ value: 'HIGH', count: 3 }]} />)
    expect(screen.getByText('Trust score distribution')).toBeInTheDocument()
    expect(screen.getByText('HIGH')).toBeInTheDocument()
  })

  it('renders a doughnut with a legend', () => {
    render(
      <VerificationChart
        type="doughnut"
        data={[{ value: 'REAL', count: 2 }, { value: 'FAKE', count: 1 }]}
      />,
    )
    expect(screen.getByText('AI prediction distribution')).toBeInTheDocument()
    expect(screen.getByText('REAL')).toBeInTheDocument()
    expect(screen.getByText('FAKE')).toBeInTheDocument()
  })

  it('renders a trend line and switches period', () => {
    const trend = {
      daily: [{ period: '2026-01-01', count: 1 }],
      weekly: [{ period: '2026-W01', count: 2 }],
    }
    render(<VerificationChart type="line" trend={trend} />)
    expect(screen.getByText('Verification trend')).toBeInTheDocument()
    expect(screen.getAllByText('2026-01-01').length).toBeGreaterThan(0)
    fireEvent.click(screen.getByRole('button', { name: 'weekly' }))
    expect(screen.getAllByText('2026-W01').length).toBeGreaterThan(0)
  })

  it('shows a message when there is no trend data', () => {
    render(<VerificationChart type="line" trend={{ daily: [] }} />)
    expect(screen.getByText('No trend data')).toBeInTheDocument()
  })
})
