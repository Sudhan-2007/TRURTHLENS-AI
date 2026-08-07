import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'

export default function Profile() {
  const { user, updateProfile, logout } = useAuth()
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

  return (
    <div className="px-4 py-12">
      <div className="mx-auto max-w-md">
        <div className="card p-8">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-slate-900">Profile</h1>
            <span
              className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
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

          {message && <p className="alert-success">{message}</p>}
          {error && <p className="alert-error">{error}</p>}

          <form onSubmit={handleSave} className="mt-6 space-y-4">
            <div>
              <label className="label" htmlFor="name">Name</label>
              <input
                id="name"
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="label" htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="label" htmlFor="password">
                New password <span className="font-normal text-slate-400">(optional)</span>
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
                placeholder="Leave blank to keep current"
              />
            </div>
            <button type="submit" disabled={saving} className="btn-primary w-full py-2.5">
              {saving ? 'Saving...' : 'Save changes'}
            </button>
          </form>

          <button onClick={logout} className="btn-secondary mt-4 w-full py-2.5">
            Log out
          </button>
        </div>
      </div>
    </div>
  )
}
