import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { api } from '../api/client'
import Result from './Result'

vi.mock('../api/client', () => ({
  api: {
    getSubmission: vi.fn(),
    getVerification: vi.fn(),
    getEvidence: vi.fn(),
    getTrustScore: vi.fn(),
    getExplanation: vi.fn(),
    runVerification: vi.fn(),
    runTrustScore: vi.fn(),
    runExplanation: vi.fn(),
    deleteSubmission: vi.fn(),
  },
}))

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal()
  return {
    ...actual,
    useParams: () => ({ submissionId: 'TL-1' }),
    useNavigate: () => vi.fn(),
  }
})

const COMPLETED = {
  submission_id: 'TL-1',
  status: 'completed',
  input_type: 'text',
  content: 'Some news text content.',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:01:00Z',
  verification_result: {
    verdict: 'REAL',
    confidence: 0.91,
    summary: 'Looks credible.',
    model_name: 'distilbert',
    model_version: '1.0.0',
    processing_time_ms: 42,
  },
}

const VERIFICATION = {
  verification_status: 'SUPPORTED',
  verification_confidence: 0.8,
  evidence_count: 2,
  official_source_count: 1,
  average_similarity: 0.7,
}

function renderResult() {
  return render(
    <MemoryRouter>
      <Result />
    </MemoryRouter>,
  )
}

describe('Result', () => {
  it('shows a loading state while the submission loads', () => {
    api.getSubmission.mockReturnValue(new Promise(() => {}))
    renderResult()
    expect(screen.getByText('Loading submission...')).toBeInTheDocument()
  })

  it('shows the error and a back link when loading fails', async () => {
    api.getSubmission.mockRejectedValue(new Error('Submission not found'))
    renderResult()
    await waitFor(() =>
      expect(screen.getByText('Submission not found')).toBeInTheDocument(),
    )
    expect(screen.getByText('Back to verification')).toBeInTheDocument()
  })

  it('renders a completed submission with all result cards', async () => {
    api.getSubmission.mockResolvedValue(COMPLETED)
    api.getVerification.mockResolvedValue(VERIFICATION)
    api.getEvidence.mockResolvedValue({ evidence: [] })
    api.getTrustScore.mockResolvedValue({ final_score: 85, trust_level: 'HIGH' })
    api.getExplanation.mockResolvedValue({ overall_result: 'REAL', limitations: [] })

    renderResult()
    await waitFor(() =>
      expect(screen.getByText('Verification result')).toBeInTheDocument(),
    )
    expect(screen.getByText(/Likely REAL/)).toBeInTheDocument()
    expect(screen.getByText('SUPPORTED')).toBeInTheDocument()
    expect(screen.getByText('Delete submission')).toBeInTheDocument()
  })

  it('runs verification when the button is clicked', async () => {
    api.getSubmission.mockResolvedValue(COMPLETED)
    api.getVerification.mockResolvedValue(null)
    api.runVerification.mockResolvedValue({})

    renderResult()
    await waitFor(() =>
      expect(screen.getByText('Verify against official sources')).toBeInTheDocument(),
    )
    fireEvent.click(screen.getByText('Verify against official sources'))

    await waitFor(() => expect(api.runVerification).toHaveBeenCalledWith('TL-1'))
    expect(api.getVerification).toHaveBeenCalledWith('TL-1')
  })

  it('deletes the submission and navigates back to verify', async () => {
    api.getSubmission.mockResolvedValue(COMPLETED)
    api.getVerification.mockResolvedValue(null)
    api.getTrustScore.mockResolvedValue(null)
    api.getExplanation.mockResolvedValue(null)
    api.deleteSubmission.mockResolvedValue(null)

    renderResult()
    await waitFor(() =>
      expect(screen.getByText('Delete submission')).toBeInTheDocument(),
    )
    fireEvent.click(screen.getByText('Delete submission'))
    await waitFor(() => expect(api.deleteSubmission).toHaveBeenCalledWith('TL-1'))
  })
})
