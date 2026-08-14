import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, useNavigate } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { api } from '../api/client'
import Verify from './Verify'
import { useAuth } from '../context/AuthContext'

vi.mock('../api/client', () => ({ api: { submitText: vi.fn(), submitUrl: vi.fn() } }))
vi.mock('../context/AuthContext', () => ({ useAuth: vi.fn() }))
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, useNavigate: vi.fn() }
})

const LONG_TEXT = 'A'.repeat(10001)

function renderVerify() {
  useAuth.mockReturnValue({ user: { name: 'Tester', email: 't@example.com' } })
  return render(
    <MemoryRouter>
      <Verify />
    </MemoryRouter>,
  )
}

describe('Verify', () => {
  it('rejects text shorter than the minimum', () => {
    renderVerify()
    fireEvent.change(screen.getByLabelText('News text'), { target: { value: 'too short' } })
    fireEvent.click(screen.getByText('Verify'))
    expect(screen.getByText('News text must be at least 20 characters.')).toBeInTheDocument()
    expect(api.submitText).not.toHaveBeenCalled()
  })

  it('rejects text longer than the maximum', () => {
    renderVerify()
    fireEvent.change(screen.getByLabelText('News text'), { target: { value: LONG_TEXT } })
    fireEvent.click(screen.getByText('Verify'))
    expect(screen.getByText('News text must be at most 10000 characters.')).toBeInTheDocument()
    expect(api.submitText).not.toHaveBeenCalled()
  })

  it('rejects a malformed URL', () => {
    renderVerify()
    fireEvent.click(screen.getByText('News URL'))
    fireEvent.change(screen.getByLabelText('News URL'), { target: { value: 'not-a-url' } })
    fireEvent.click(screen.getByText('Verify'))
    expect(
      screen.getByText('Enter a valid URL starting with http:// or https://'),
    ).toBeInTheDocument()
    expect(api.submitUrl).not.toHaveBeenCalled()
  })

  it('submits valid text and navigates to the result', async () => {
    api.submitText.mockResolvedValue({ submission_id: 'TL-000000000001-ABC' })
    const navigate = vi.fn()
    useNavigate.mockReturnValue(navigate)
    renderVerify()
    fireEvent.change(screen.getByLabelText('News text'), {
      target: { value: 'Global temperatures have increased by more than one degree.' },
    })
    fireEvent.click(screen.getByText('Verify'))
    await waitFor(() => expect(api.submitText).toHaveBeenCalledTimes(1))
    expect(navigate).toHaveBeenCalledWith('/result/TL-000000000001-ABC', { replace: true })
  })

  it('submits a valid URL and navigates to the result', async () => {
    api.submitUrl.mockResolvedValue({ submission_id: 'TL-000000000002-ABC' })
    const navigate = vi.fn()
    useNavigate.mockReturnValue(navigate)
    renderVerify()
    fireEvent.click(screen.getByText('News URL'))
    fireEvent.change(screen.getByLabelText('News URL'), {
      target: { value: 'https://example.com/news/story' },
    })
    fireEvent.click(screen.getByText('Verify'))
    await waitFor(() => expect(api.submitUrl).toHaveBeenCalledTimes(1))
    expect(navigate).toHaveBeenCalledWith('/result/TL-000000000002-ABC', { replace: true })
  })
})
