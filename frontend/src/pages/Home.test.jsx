import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import Home from './Home'

describe('Home', () => {
  it('renders the hero, features, and CTAs', () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>,
    )
    expect(
      screen.getByRole('heading', {
        name: /Verify the truth before you share it/i,
      }),
    ).toBeInTheDocument()
    expect(screen.getByText('Detect')).toBeInTheDocument()
    expect(screen.getByText('Verify')).toBeInTheDocument()
    expect(screen.getByText('Explain')).toBeInTheDocument()
    expect(screen.getByText('Track')).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Start verifying free' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Create your account' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'How it works' }),
    ).toBeInTheDocument()
  })
})
