import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import Layout from '../Layout'
import { useAuth } from '../../context/AuthContext'

vi.mock('../../context/AuthContext', () => ({ useAuth: vi.fn() }))

describe('Layout', () => {
  it('renders the navbar, outlet content, and footer', () => {
    useAuth.mockReturnValue({ user: { email: 'a@example.com' } })
    render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<div>page body</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    )
    expect(screen.getByText('page body')).toBeInTheDocument()
    expect(screen.getByRole('navigation')).toBeInTheDocument()
    expect(screen.getByRole('contentinfo')).toBeInTheDocument()
  })
})
