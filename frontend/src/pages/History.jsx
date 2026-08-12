import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import HistoryTable from '../components/history/HistoryTable'

const selectClass =
  'rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 focus:border-blue-500 focus:outline-none'

export default function History() {
  const [items, setItems] = useState(null)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const [limit] = useState(20)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [prediction, setPrediction] = useState('')
  const [verificationStatus, setVerificationStatus] = useState('')
  const [trustLevel, setTrustLevel] = useState('')
  const [sort, setSort] = useState('created_desc')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true)
    try {
      const data = await api.getHistory({
        search,
        prediction,
        verification_status: verificationStatus,
        trust_level: trustLevel,
        sort,
        limit,
        skip: page * limit,
      })
      setItems(data.items)
      setTotal(data.total)
      setError('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, prediction, verificationStatus, trustLevel, sort, page])

  function applySearch(e) {
    e.preventDefault()
    setPage(0)
    setSearch(searchInput)
  }

  async function handleDelete(item) {
    if (!window.confirm('Delete this submission?')) return
    try {
      await api.deleteSubmission(item.submission_id)
      if (items.length === 1 && page > 0) setPage(page - 1)
      else await load()
    } catch (err) {
      setError(err.message)
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / limit))

  return (
    <div className="px-4 py-12">
      <div className="mx-auto max-w-5xl">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Verification history</h1>
            <p className="mt-1 text-sm text-slate-500">{total} submission(s)</p>
          </div>
          <Link to="/verify" className="btn-primary">Verify new</Link>
        </div>

        <form onSubmit={applySearch} className="mt-6 flex flex-wrap items-end gap-3">
          <div className="min-w-[200px] flex-1">
            <p className="label">Search</p>
            <input
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Search content or URL"
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <p className="label">Prediction</p>
            <select value={prediction} onChange={(e) => { setPrediction(e.target.value); setPage(0) }} className={`mt-1 ${selectClass}`}>
              <option value="">All</option>
              <option value="REAL">REAL</option>
              <option value="FAKE">FAKE</option>
            </select>
          </div>
          <div>
            <p className="label">Verification</p>
            <select value={verificationStatus} onChange={(e) => { setVerificationStatus(e.target.value); setPage(0) }} className={`mt-1 ${selectClass}`}>
              <option value="">All</option>
              <option value="SUPPORTED">Supported</option>
              <option value="CONTRADICTED">Contradicted</option>
              <option value="PARTIALLY_SUPPORTED">Partially supported</option>
              <option value="UNVERIFIED">Unverified</option>
            </select>
          </div>
          <div>
            <p className="label">Trust level</p>
            <select value={trustLevel} onChange={(e) => { setTrustLevel(e.target.value); setPage(0) }} className={`mt-1 ${selectClass}`}>
              <option value="">All</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="LOW">LOW</option>
              <option value="VERY_LOW">VERY_LOW</option>
            </select>
          </div>
          <div>
            <p className="label">Sort</p>
            <select value={sort} onChange={(e) => { setSort(e.target.value); setPage(0) }} className={`mt-1 ${selectClass}`}>
              <option value="created_desc">Newest first</option>
              <option value="created_asc">Oldest first</option>
            </select>
          </div>
          <button type="submit" className="btn-secondary">Search</button>
        </form>

        {error && <p className="alert-error mt-6">{error}</p>}

        <div className="mt-6">
          {loading && !items ? (
            <div className="py-16 text-center text-slate-400">
              <span className="inline-block h-6 w-6 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
              <p className="mt-3 text-sm">Loading history...</p>
            </div>
          ) : (
            <HistoryTable items={items} onDelete={handleDelete} />
          )}
        </div>

        {totalPages > 1 && (
          <div className="mt-6 flex items-center justify-center gap-3">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="btn-secondary disabled:cursor-not-allowed disabled:opacity-40"
            >
              Previous
            </button>
            <span className="text-sm text-slate-500">
              Page {page + 1} of {totalPages}
            </span>
            <button
              onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
              disabled={page >= totalPages - 1}
              className="btn-secondary disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
