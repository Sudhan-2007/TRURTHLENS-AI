import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import Footer from '../Footer'

describe('Footer', () => {
  it('renders the brand and copyright', () => {
    render(<Footer />)
    expect(screen.getByRole('contentinfo')).toBeInTheDocument()
    expect(screen.getByText(/verify before you share/)).toBeInTheDocument()
    expect(screen.getByText(/All rights reserved/)).toBeInTheDocument()
  })
})
