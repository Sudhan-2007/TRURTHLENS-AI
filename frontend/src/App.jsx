import { useEffect, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function App() {
  const [apiStatus, setApiStatus] = useState('checking')
  const [apiMessage, setApiMessage] = useState('')

  useEffect(() => {
    async function checkApi() {
      try {
        const res = await fetch(`${API_BASE_URL}/api/health`)
        const data = await res.json()
        setApiStatus(res.ok ? 'online' : 'error')
        setApiMessage(data.message || `HTTP ${res.status}`)
      } catch {
        setApiStatus('offline')
        setApiMessage('Unable to reach backend')
      }
    }
    checkApi()
  }, [])

  const statusStyles = {
    checking: 'bg-gray-200 text-gray-600',
    online: 'bg-green-100 text-green-700',
    offline: 'bg-red-100 text-red-700',
    error: 'bg-amber-100 text-amber-700',
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex items-center justify-center">
      <main className="max-w-xl w-full mx-4 bg-white rounded-2xl shadow-sm border border-slate-200 p-10 text-center">
        <h1 className="text-4xl font-bold tracking-tight">TruthLens AI</h1>
        <p className="mt-3 text-slate-500">
          AI-powered misinformation detection, verification, explanation and
          tracking platform
        </p>

        <div className="mt-8 flex items-center justify-center gap-3">
          <span className="text-sm font-medium text-slate-500">
            Backend status:
          </span>
          <span
            className={`px-3 py-1 rounded-full text-sm font-semibold ${statusStyles[apiStatus]}`}
          >
            {apiStatus}
          </span>
        </div>
        {apiMessage && (
          <p className="mt-2 text-sm text-slate-400">{apiMessage}</p>
        )}
      </main>
    </div>
  )
}

export default App
