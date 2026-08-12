import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import StatsCard from '../dashboard/StatsCard'

describe('StatsCard', () => {
  it('renders label, value, and optional subtext', () => {
    render(<StatsCard label="Total submissions" value={12} sub="across all sources" />)
    expect(screen.getByText('Total submissions')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
    expect(screen.getByText('across all sources')).toBeInTheDocument()
  })

  it('does not render subtext when omitted', () => {
    const { container } = render(<StatsCard label="Active users" value={3} />)
    expect(container.textContent).not.toContain('undefined')
  })

  it('applies an accent class when provided', () => {
    render(<StatsCard label="Fake" value={5} accent="text-red-600" />)
    expect(screen.getByText('5')).toHaveClass('text-red-600')
  })
})
