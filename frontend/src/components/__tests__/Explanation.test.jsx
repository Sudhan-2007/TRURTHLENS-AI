import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import Explanation from '../result/Explanation'

const explanation = {
  overall_result: 'The claim is broadly supported by official sources.',
  components: {
    trust_level: 'HIGH',
    final_score: 82,
    prediction: 'REAL',
    confidence: 0.91,
    model_name: 'DistilBERT',
    model_version: '1.0.0',
    verification_status: 'SUPPORTED',
    verification_confidence: 0.84,
  },
  trust_score_explanation: 'High agreement across all evidence channels.',
  ai_explanation: 'The model found strong linguistic alignment with reliable reporting.',
  verification_explanation: 'Two official sources corroborate the claim.',
  evidence_summary: [],
  source_references: [],
  limitations: ['Limits of automated verification'],
  explanation_version: '1.1',
}

describe('Explanation', () => {
  it('shows the empty state with a generate button', () => {
    const onRun = vi.fn()
    render(<Explanation explanation={null} onRun={onRun} running={false} />)
    expect(screen.getByText('Why this result?')).toBeInTheDocument()
    expect(screen.getByText('Generate explanation')).toBeInTheDocument()
  })

  it('triggers onRun when the button is clicked', () => {
    const onRun = vi.fn()
    render(<Explanation explanation={null} onRun={onRun} running={false} />)
    fireEvent.click(screen.getByText('Generate explanation'))
    expect(onRun).toHaveBeenCalledTimes(1)
  })

  it('disables the button while running', () => {
    render(<Explanation explanation={null} onRun={vi.fn()} running />)
    expect(screen.getByText('Generating...')).toBeDisabled()
  })

  it('renders the overall result, badges, and confidence', () => {
    render(<Explanation explanation={explanation} onRun={vi.fn()} running={false} />)
    expect(screen.getByText(explanation.overall_result)).toBeInTheDocument()
    expect(screen.getByText('HIGH')).toBeInTheDocument()
    expect(screen.getByText('82/100')).toBeInTheDocument()
    expect(screen.getByText('Likely REAL')).toBeInTheDocument()
    expect(screen.getByText('91% confidence · DistilBERT v1.0.0')).toBeInTheDocument()
  })

  it('renders the limitations list', () => {
    render(<Explanation explanation={explanation} onRun={vi.fn()} running={false} />)
    expect(screen.getByText('Limitations')).toBeInTheDocument()
    expect(screen.getByText('Limits of automated verification')).toBeInTheDocument()
  })
})
