import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Profile() {
  const { user, updateProfile, logout } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (user) {
      setName(user.name)
      setEmail(user.email)
    }
  }, [user])

  if (!user) return null

  async function handleSave(e) {
    e.preventDefault()
    setError('')
    setMessage('')
    setSaving(true)
    try {
      const payload = { name, email }
      if (password) payload.password = password
      await updateProfile(payload)
      setPassword('')
      setMessage('Profile updated successfully')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-md mx-auto">
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold">Profile</h1>
            <span
              className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                user.role === 'admin'
                  ? 'bg-purple-100 text-purple-700'
                  : 'bg-slate-100 text-slate-600'
              }`}
            >
              {user.role}
            </span>
          </div>

          <dl className="mt-4 grid grid-cols-2 gap-2 text-sm">
            <dt className="text-slate-500">Account created</dt>
            <dd>{new Date(user.created_at).toLocaleDateString()}</dd>
            <dt className="text-slate-500">Last updated</dt>
            <dd>{new Date(user.updated_at).toLocaleDateString()}</dd>
          </dl>

          {message && (
            <p className="mt-4 text-sm bg-green-50 text-green-700 border border-green-200 rounded-lg px-3 py-2">
              {message}
            </p>
          )}
          {error && (
            <p className="mt-4 text-sm bg-red-50 text-red-700 border border-red-200 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <form onSubmit={handleSave} className="mt-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700">Name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">
                New password <span className="font-normal text-slate-400">(optional)</span>
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Leave blank to keep current"
              />
            </div>
            <button
              type="submit"
              disabled={saving}
              className="w-full rounded-lg bg-blue-600 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save changes'}
            </button>
          </form>

          <button
            onClick={handleLogout}
            className="mt-4 w-full rounded-lg border border-slate-300 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50"
          >
            Log out
          </button>
        </div>
      </div>
    </div>
  )
}
