import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function Logo() {
  return (
    <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white">
      <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="3.5" />
        <circle cx="12" cy="12" r="9" strokeDasharray="3 3" />
      </svg>
    </span>
  )
}

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/')
  }

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/85 backdrop-blur">
      <nav className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link to="/" className="flex items-center gap-2.5">
          <Logo />
          <span className="text-lg font-bold tracking-tight text-slate-900">
            TruthLens
          </span>
        </Link>

        <div className="flex items-center gap-3">
          {user ? (
            <>
              <Link
                to="/verify"
                className="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
              >
                Verify news
              </Link>
              <Link
                to="/history"
                className="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
              >
                History
              </Link>
              <Link
                to="/profile"
                className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
              >
                Profile
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                    user.role === 'admin'
                      ? 'bg-purple-100 text-purple-700'
                      : 'bg-slate-100 text-slate-500'
                  }`}
                >
                  {user.role}
                </span>
              </Link>
              <button onClick={handleLogout} className="btn-secondary">
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-secondary">
                Sign in
              </Link>
              <Link to="/register" className="btn-primary">
                Get started
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  )
}
