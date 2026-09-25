import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api/client'
import { statusStyles, verificationStyles, verdictStyles } from '../constants/styles'
import EvidenceList from '../components/result/EvidenceList'
import Explanation from '../components/result/Explanation'
import TrustScore from '../components/result/TrustScore'
import FeedbackModal from '../components/result/FeedbackModal'

const verificationBarStyles = {
  SUPPORTED: 'bg-green-500',
  CONTRADICTED: 'bg-red-500',
  PARTIALLY_SUPPORTED: 'bg-amber-500',
  UNVERIFIED: 'bg-slate-300',
}

function VerdictCard({ result }) {
  const verdict = result?.verdict
  const confidence = result?.confidence ?? 0

  return (
    <div className={`rounded-xl border p-5 ${verdict === 'REAL' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
      <div className="flex items-center justify-between">
        <span className={`rounded-full px-4 py-1.5 text-lg font-bold ${verdictStyles[verdict]}`}>
          {verdict === 'REAL' ? 'Likely REAL' : 'Likely FAKE'}
        </span>
        <span className="text-2xl font-bold text-slate-800">{Math.round(confidence * 100)}%</span>
      </div>

      <div className="mt-3 h-2.5 w-full overflow-hidden rounded-full bg-slate-200">
        <div
          className={`h-full rounded-full ${verdict === 'REAL' ? 'bg-green-500' : 'bg-red-500'}`}
          style={{ width: `${confidence * 100}%` }}
        />
      </div>
      <p className="mt-1 text-xs text-slate-500">Model confidence</p>

      <p className="mt-3 text-sm leading-relaxed text-slate-700">{result?.summary}</p>

      <div className="mt-3 grid grid-cols-2 gap-2 border-t border-slate-200 pt-3 text-xs text-slate-500">
        <p>Model</p>
        <p>{result?.model_name}</p>
        <p>Version</p>
        <p>v{result?.model_version}</p>
        <p>Analysis time</p>
        <p>{result?.processing_time_ms} ms</p>
      </div>
    </div>
  )
}

function VerificationCard({ verification, evidence, onRun, running }) {
  if (!verification) {
    return (
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold text-slate-700">Official source verification</p>
          <button onClick={onRun} disabled={running} className="btn-primary px-3 py-1.5 text-xs">
            {running ? 'Verifying...' : 'Verify against official sources'}
          </button>
        </div>
        <p className="mt-2 text-xs text-slate-500">
          Cross-check this claim against trusted government, fact-check, and reputable news sources.
        </p>
      </div>
    )
  }

  const status = verification.verification_status
  const confidence = verification.verification_confidence ?? 0
  const isVerified = status !== 'UNVERIFIED'

  return (
    <div className="rounded-xl border border-slate-200 p-5">
      <div className="flex items-center justify-between">
        <span className={`rounded-full border px-4 py-1.5 text-sm font-bold ${verificationStyles[status]}`}>
          {status}
        </span>
        <span className="text-2xl font-bold text-slate-800">{Math.round(confidence * 100)}%</span>
      </div>

      <div className="mt-3 h-2.5 w-full overflow-hidden rounded-full bg-slate-200">
        <div
          className={`h-full rounded-full ${verificationBarStyles[status]}`}
          style={{ width: `${Math.min(confidence * 100, 100)}%` }}
        />
      </div>
      <p className="mt-1 text-xs text-slate-500">Verification confidence</p>

      <div className="mt-3 grid grid-cols-3 gap-2 border-t border-slate-200 pt-3 text-center text-xs text-slate-500">
        <div>
          <p className="text-base font-bold text-slate-800">{verification.evidence_count}</p>
          <p>Evidence items</p>
        </div>
        <div>
          <p className="text-base font-bold text-slate-800">{verification.official_source_count}</p>
          <p>Official sources</p>
        </div>
        <div>
          <p className="text-base font-bold text-slate-800">
            {Math.round((verification.average_similarity ?? 0) * 100)}%
          </p>
          <p>Avg similarity</p>
        </div>
      </div>

      {isVerified ? (
        <EvidenceList items={evidence} />
      ) : (
        <p className="mt-3 rounded-lg bg-slate-50 p-3 text-xs leading-relaxed text-slate-500">
          No trusted evidence matching this claim was found. This does not mean the claim is false —
          absence of evidence is not proof either way.
        </p>
      )}
    </div>
  )
}

export default function Result() {
  const { submissionId } = useParams()
  const navigate = useNavigate()
  const [submission, setSubmission] = useState(null)
  const [verification, setVerification] = useState(null)
  const [evidence, setEvidence] = useState([])
  const [verificationLoading, setVerificationLoading] = useState(false)
  const [trustScore, setTrustScore] = useState(null)
  const [trustScoreLoading, setTrustScoreLoading] = useState(false)
  const [explanation, setExplanation] = useState(null)
  const [explanationLoading, setExplanationLoading] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false)

  async function loadVerification() {
    try {
      const data = await api.getVerification(submissionId)
      setVerification(data)
      try {
        const ev = await api.getEvidence(submissionId)
        setEvidence(ev.evidence || [])
      } catch {
        setEvidence([])
      }
    } catch {
      setVerification(null)
    }
  }

  async function loadTrustScore() {
    const data = await api.getTrustScore(submissionId).catch(() => null)
    setTrustScore(data)
    return data
  }

  async function loadExplanation() {
    const data = await api.getExplanation(submissionId).catch(() => null)
    setExplanation(data)
  }

  async function handleVerify() {
    setVerificationLoading(true)
    try {
      await api.runVerification(submissionId)
      await loadVerification()
    } catch (err) {
      setError(err.message)
    } finally {
      setVerificationLoading(false)
    }
  }

  async function handleTrustScore() {
    setTrustScoreLoading(true)
    try {
      await api.runTrustScore(submissionId)
      await loadTrustScore()
    } catch (err) {
      setError(err.message)
    } finally {
      setTrustScoreLoading(false)
    }
  }

  async function handleExplanation() {
    setExplanationLoading(true)
    try {
      await api.runExplanation(submissionId)
      await loadExplanation()
    } catch (err) {
      setError(err.message)
    } finally {
      setExplanationLoading(false)
    }
  }

  useEffect(() => {
    let active = true

    async function load() {
      try {
        const data = await api.getSubmission(submissionId)
        if (!active) return
        setSubmission(data)
        if (data.status === 'submitted' || data.status === 'processing') {
          setTimeout(load, 2500)
          return
        }
        const result = await api.getVerification(submissionId).catch(() => null)
        if (!active) return
        setVerification(result)
        if (result) {
          const ev = await api.getEvidence(submissionId).catch(() => null)
          if (active) setEvidence(ev?.evidence || [])
        }
        const ts = await api.getTrustScore(submissionId).catch(() => null)
        if (active) setTrustScore(ts)
        const ex = await api.getExplanation(submissionId).catch(() => null)
        if (active) setExplanation(ex)
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

  const handleShareToX = () => {
    const verdict = submission?.verification_result?.verdict === 'REAL' ? 'REAL' : 'FAKE'
    const confidence = Math.round((submission?.verification_result?.confidence || 0) * 100)
    
    let text = `I just analyzed a news claim on TruthLens AI! 🔍\n\n`
    if (submission?.verification_result) {
      text = `TruthLens AI analyzed this claim and found it to be ${verdict} with ${confidence}% confidence! 🔍\n\n`
    }
    
    const url = window.location.href
    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`
    
    window.open(twitterUrl, '_blank')
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
            <p className="label">
              {submission.input_type === 'text' ? 'News text' : submission.input_type === 'account' ? 'Social Media Profile' : 'News URL'}
            </p>
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
              <div className="mt-1">
                <VerdictCard result={submission.verification_result} />
              </div>
            </div>
          )}

          {!isProcessing && (
            <div>
              <p className="label">Official source verification</p>
              <div className="mt-1">
                <VerificationCard
                  verification={verification}
                  evidence={evidence}
                  onRun={handleVerify}
                  running={verificationLoading}
                />
              </div>
            </div>
          )}

          {!isProcessing && (
            <div>
              <p className="label">Trust score</p>
              <div className="mt-1">
                <TrustScore
                  score={trustScore}
                  onRun={handleTrustScore}
                  running={trustScoreLoading}
                />
              </div>
            </div>
          )}

          {!isProcessing && (
            <div>
              <p className="label">Why this result?</p>
              <div className="mt-1">
                <Explanation
                  explanation={explanation}
                  onRun={handleExplanation}
                  running={explanationLoading}
                />
              </div>
            </div>
          )}
        </div>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <button onClick={handleShareToX} className="btn-primary bg-black hover:bg-gray-800 border-none flex items-center gap-2">
            <svg viewBox="0 0 24 24" aria-hidden="true" className="h-4 w-4 fill-current"><g><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 22.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"></path></g></svg>
            Share on X
          </button>
          <Link to="/verify" className="btn-secondary">Verify another</Link>
          <button onClick={() => setIsFeedbackOpen(true)} className="btn-secondary">
            Report Issue
          </button>
          <button onClick={handleDelete} className="btn-secondary text-red-600 hover:bg-red-50">
            Delete
          </button>
        </div>
      </div>
      
      <FeedbackModal 
        isOpen={isFeedbackOpen} 
        onClose={() => setIsFeedbackOpen(false)} 
        submissionId={submissionId} 
      />
    </div>
  )
}
