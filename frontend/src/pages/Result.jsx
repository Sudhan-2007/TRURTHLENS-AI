import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api/client'

const statusStyles = {
  submitted: 'bg-slate-100 text-slate-600',
  processing: 'bg-amber-100 text-amber-700',
  completed: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
}

export default function Result() {
  const { submissionId } = useParams()
  const navigate = useNavigate()
  const [submission, setSubmission] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true

    async function load() {
      try {
        const data = await api.getSubmission(submissionId)
        if (!active) return
        setSubmission(data)
        if (data.status === 'submitted' || data.status === 'processing') {
          setTimeout(load, 2500)
        }
      } catch (err) {
        if (active) {
          setError(err.message)
          setLoading(false)
        }
      }
    }

    load()
    return () => {
      active = false
    }
  }, [submissionId])

  async function handleDelete() {
    try {
      await api.deleteSubmission(submissionId)
      navigate('/verify', { replace: true })
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading && !submission) {
    return (
      <div className="px-4 py-20 text-center text-slate-400">
        <span className="inline-block h-6 w-6 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
        <p className="mt-3 text-sm">Loading submission...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-4 py-16">
        <div className="mx-auto max-w-md text-center">
          <p className="alert-error">{error}</p>
          <Link to="/verify" className="btn-secondary mt-6">Back to verification</Link>
        </div>
      </div>
    )
  }

  const isProcessing = submission.status === 'submitted' || submission.status === 'processing'

  return (
    <div className="px-4 py-12">
      <div className="mx-auto max-w-2xl">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-slate-900">Verification result</h1>
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[submission.status]}`}>
            {submission.status}
          </span>
        </div>

        <div className="mt-2 text-sm text-slate-400 font-mono">{submission.submission_id}</div>

        {isProcessing && (
          <div className="card mt-6 flex items-center gap-3 p-4">
            <span className="h-5 w-5 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
            <p className="text-sm text-slate-600">
              TruthLens AI is analyzing this submission...
            </p>
          </div>
        )}

        {submission.status === 'failed' && (
          <div className="card mt-6 border-red-200 p-4">
            <p className="text-sm text-red-700">
              Processing failed. Please try submitting again.
            </p>
          </div>
        )}

        <div className="card mt-6 space-y-4 p-6">
          <div>
            <p className="label">Input type</p>
            <p className="mt-1 text-sm capitalize text-slate-700">{submission.input_type}</p>
          </div>

          <div>
            <p className="label">{submission.input_type === 'text' ? 'News text' : 'News URL'}</p>
            {submission.input_type === 'text' ? (
              <p className="mt-1 whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-sm leading-relaxed text-slate-700">
                {submission.content}
              </p>
            ) : (
              <a
                href={submission.url}
                target="_blank"
                rel="noreferrer"
                className="mt-1 inline-block break-all text-sm text-blue-600 hover:underline"
              >
                {submission.url}
              </a>
            )}
          </div>

          <div className="grid grid-cols-2 gap-2 text-sm">
            <p className="text-slate-500">Submitted</p>
            <p>{new Date(submission.created_at).toLocaleString()}</p>
            <p className="text-slate-500">Last updated</p>
            <p>{new Date(submission.updated_at).toLocaleString()}</p>
          </div>

          {submission.verification_result && (
            <div>
              <p className="label">AI analysis</p>
              <p className="mt-1 rounded-lg bg-blue-50 p-3 text-sm text-slate-700">
                {submission.verification_result.summary || 'Analysis complete.'}
              </p>
            </div>
          )}
        </div>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <Link to="/verify" className="btn-primary">Verify another</Link>
          <button onClick={handleDelete} className="btn-secondary text-red-600 hover:bg-red-50">
            Delete submission
          </button>
        </div>
      </div>
    </div>
  )
}
