import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import SourceList from '../result/SourceList'

const sources = [
  {
    name: 'WHO',
    domain: 'who.int',
    trust_level: 'HIGH',
    category: 'health',
    publication_date: '2026-03-01',
    url: 'https://www.who.int/news',
    title: 'WHO statement',
  },
  {
    name: 'Example News',
    domain: 'example.com',
    trust_level: 'MEDIUM',
    url: 'https://example.com/a',
  },
]

describe('SourceList', () => {
  it('shows the default empty message', () => {
    render(<SourceList sources={[]} />)
    expect(screen.getByText('No trusted source references are available.')).toBeInTheDocument()
  })

  it('shows a custom message when sources is undefined', () => {
    render(<SourceList sources={undefined} />)
    expect(screen.getByText('No trusted source references are available.')).toBeInTheDocument()
  })

  it('renders source name, domain, trust level, and category', () => {
    render(<SourceList sources={sources} />)
    expect(screen.getByText('WHO')).toBeInTheDocument()
    expect(screen.getByText('who.int · HIGH trust · health · published 2026-03-01')).toBeInTheDocument()
    expect(screen.getByText('Example News')).toBeInTheDocument()
    expect(screen.getByText('example.com · MEDIUM trust · source')).toBeInTheDocument()
  })

  it('links to the source URL in a new tab', () => {
    render(<SourceList sources={sources} />)
    const link = screen.getByText('WHO statement')
    expect(link).toHaveAttribute('href', 'https://www.who.int/news')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noreferrer')
  })

  it('falls back to the URL as the link title', () => {
    render(<SourceList sources={sources} />)
    expect(screen.getByText('https://example.com/a')).toHaveAttribute(
      'href',
      'https://example.com/a',
    )
  })
})
