import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import EvidenceList from '../result/EvidenceList'

const items = [
  {
    label: 'SUPPORTED',
    status: 'SUPPORTED',
    similarity_score: 0.912,
    claim: 'Vaccination reduces hospitalization risk',
    meaning: 'Directly corroborates the claim',
    evidence_summary: 'A peer-reviewed study supports this finding.',
    source_url: 'https://example.com/study',
    source_name: 'Example Journal',
    source_domain: 'example.com',
  },
  {
    status: 'CONTRADICTED',
    evidence_summary: 'No matching official record found.',
  },
]

describe('EvidenceList', () => {
  it('shows the default empty message', () => {
    render(<EvidenceList items={[]} />)
    expect(
      screen.getByText(/No trusted evidence matching this claim/),
    ).toBeInTheDocument()
  })

  it('shows a custom empty message when provided', () => {
    render(<EvidenceList items={[]} emptyMessage="Nothing found." />)
    expect(screen.getByText('Nothing found.')).toBeInTheDocument()
  })

  it('renders status badge and similarity percentage', () => {
    render(<EvidenceList items={items} />)
    expect(screen.getByText('SUPPORTED')).toBeInTheDocument()
    expect(screen.getByText('91% match')).toBeInTheDocument()
  })

  it('renders the source as an external link', () => {
    render(<EvidenceList items={items} />)
    const link = screen.getByRole('link')
    expect(link.getAttribute('href')).toBe('https://example.com/study')
    expect(link.getAttribute('target')).toBe('_blank')
  })

  it('renders the claim prefix', () => {
    render(<EvidenceList items={items} />)
    expect(screen.getByText(/Claim: Vaccination reduces/)).toBeInTheDocument()
  })
})
