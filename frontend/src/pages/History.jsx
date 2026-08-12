import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'

const statusStyles = {
  submitted: 'bg-slate-100 text-slate-600',
  processing: 'bg-amber-100 text-amber-700',
  completed: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
}

const verdictStyles = {
  REAL: 'bg-green-600 text-white',
  FAKE: 'bg-red-600 text-white',
}

export default function History() {
  const [items, setItems] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    api
      .listSubmissions()
      .then((data) => active && setItems(data))
      .catch((err) => active && setError(err.message))
    return () => {
      active = false
    }
  }, [])

  if (error) {
    return (
      <div className="px-4 py-16">
        <div className="mx-auto max-w-2xl">
          <p className="alert-error">{error}</p>
        </div>
      </div>
    )
  }

  if (!items) {
    return (
      <div className="px-4 py-20 text-center text-slate-400">
        <span className="inline-block h-6 w-6 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
        <p className="mt-3 text-sm">Loading history...</p>
      </div>
    )
  }

  return (
    <div className="px-4 py-12">
      <div className="mx-auto max-w-3xl">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-slate-900">Verification history</h1>
          <Link to="/verify" className="btn-primary">Verify new</Link>
        </div>

        {items.length === 0 ? (
          <div className="card mt-8 p-8 text-center">
            <p className="text-slate-500">No submissions yet.</p>
            <Link to="/verify" className="btn-secondary mt-4">
              Verify your first news item
            </Link>
          </div>
        ) : (
          <ul className="mt-8 space-y-3">
            {items.map((item) => {
              const verdict = item.verification_result?.verdict
              return (
                <li key={item.submission_id}>
                  <Link
                    to={`/result/${item.submission_id}`}
                    className="card block p-4 transition hover:shadow-md"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium text-slate-800">
                          {item.input_type === 'text'
                            ? item.content?.slice(0, 90) || 'Text submission'
                            : item.url}
                        </p>
                        <p className="mt-1 font-mono text-xs text-slate-400">
                          {item.submission_id} · {new Date(item.created_at).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex shrink-0 items-center gap-2">
                        {verdict && (
                          <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${verdictStyles[verdict]}`}>
                            {verdict}
                          </span>
                        )}
                        <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${statusStyles[item.status]}`}>
                          {item.status}
                        </span>
                      </div>
                    </div>
                  </Link>
                </li>
              )
            })}
          </ul>
        )}
      </div>
    </div>
  )
}
