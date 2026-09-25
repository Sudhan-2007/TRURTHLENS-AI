import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { api } from '../api/client'

export default function ResetPassword() {
  const { token } = useParams()
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess('')
    
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }
    
    setLoading(true)
    try {
      const response = await api.resetPassword(token, password)
      setSuccess(response.message || 'Password has been reset successfully.')
      setTimeout(() => navigate('/login'), 3000)
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4 py-16">
      <div className="card w-full max-w-sm p-8">
        <h1 className="text-center text-2xl font-bold text-slate-900">Reset Password</h1>
        <p className="mt-1 text-center text-sm text-slate-500">
          Enter your new password below.
        </p>

        {error && <p className="alert-error">{error}</p>}
        {success && <p className="alert-success">{success} Redirecting to login...</p>}

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="label" htmlFor="password">New Password</label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input"
              placeholder="••••••••"
            />
          </div>
          <div>
            <label className="label" htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="input"
              placeholder="••••••••"
            />
          </div>
          
          <button type="submit" disabled={loading} className="btn-primary w-full py-2.5">
            {loading ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>
        
        <p className="mt-4 text-center text-sm text-slate-500">
          <Link to="/login" className="font-medium text-blue-600 hover:underline">
            Back to Login
          </Link>
        </p>
      </div>
    </div>
  )
}
