import { createContext, useContext, useEffect, useState } from 'react'
import { api } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!localStorage.getItem('token')) {
      setLoading(false)
      return
    }
    api
      .me()
      .then(setUser)
      .catch(() => localStorage.removeItem('token'))
      .finally(() => setLoading(false))
  }, [])

  async function login(email, password) {
    const { access_token } = await api.login({ email, password })
    localStorage.setItem('token', access_token)
    const me = await api.me()
    setUser(me)
    return me
  }

  async function register(name, email, password) {
    const { user_id } = await api.register({ name, email, password })
    return user_id
  }

  async function logout() {
    try {
      await api.logout()
    } catch {
      // ignore server errors on logout
    }
    localStorage.removeItem('token')
    setUser(null)
  }

  async function updateProfile(payload) {
    const updated = await api.updateMe(payload)
    setUser(updated)
    return updated
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, login, register, logout, updateProfile }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
