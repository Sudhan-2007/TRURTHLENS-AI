import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import TrustScore from '../result/TrustScore'

describe('TrustScore', () => {
  it('shows the empty state with a calculate button', () => {
    const onRun = vi.fn()
    render(<TrustScore score={null} onRun={onRun} running={false} />)
    expect(screen.getByText('Trust score')).toBeInTheDocument()
    expect(screen.getByText('Calculate trust score')).toBeInTheDocument()
  })

  it('triggers onRun when the button is clicked', () => {
    const onRun = vi.fn()
    render(<TrustScore score={null} onRun={onRun} running={false} />)
    fireEvent.click(screen.getByText('Calculate trust score'))
    expect(onRun).toHaveBeenCalledTimes(1)
  })

  it('renders the score, level, and component breakdown', () => {
    const score = {
      final_score: 72,
      trust_level: 'MEDIUM',
      score_version: '1.0',
      ai_score: 80,
      verification_score: 60,
      evidence_score: 75,
      source_reliability_score: 70,
      similarity_score: 65,
      explanation: 'Evidence-based estimate; not absolute proof.',
    }
    render(<TrustScore score={score} onRun={vi.fn()} running={false} />)
    expect(screen.getByText('MEDIUM')).toBeInTheDocument()
    expect(screen.getByText('72')).toBeInTheDocument()
    expect(screen.getByText('AI assessment')).toBeInTheDocument()
    expect(screen.getByText('Official verification')).toBeInTheDocument()
    expect(screen.getByText(score.explanation)).toBeInTheDocument()
    expect(screen.getByText(/v1\.0/)).toBeInTheDocument()
  })

  it('disables the button while running', () => {
    render(<TrustScore score={null} onRun={vi.fn()} running />)
    expect(screen.getByText('Calculating...')).toBeDisabled()
  })
})
