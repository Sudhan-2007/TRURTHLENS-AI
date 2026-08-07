import { Link, Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'

function Home() {
  const { user } = useAuth()
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <main className="max-w-xl w-full mx-4 bg-white rounded-2xl shadow-sm border border-slate-200 p-10 text-center">
        <h1 className="text-4xl font-bold tracking-tight">TruthLens AI</h1>
        <p className="mt-3 text-slate-500">
          AI-powered misinformation detection, verification, explanation and tracking platform
        </p>
        <div className="mt-8 flex items-center justify-center gap-3">
          {user ? (
            <Link
              to="/profile"
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
            >
              Go to profile
            </Link>
          ) : (
            <>
              <Link
                to="/login"
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
              >
                Sign in
              </Link>
              <Link
                to="/register"
                className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50"
              >
                Create account
              </Link>
            </>
          )}
        </div>
      </main>
    </div>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
