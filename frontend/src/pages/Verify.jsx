import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { api } from '../api/client'

const TEXT_MIN = 20
const TEXT_MAX = 10000
const URL_MAX = 2048

export default function Verify() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [inputType, setInputType] = useState('text')
  const [content, setContent] = useState('')
  const [url, setUrl] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const activeLength = inputType === 'text' ? content.length : url.length

  function handleClear() {
    setContent('')
    setUrl('')
    setError('')
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (inputType === 'text') {
      const len = content.trim().length
      if (len < TEXT_MIN) {
        setError(`News text must be at least ${TEXT_MIN} characters.`)
        return
      }
    } else {
      const trimmed = url.trim()
      if (!/^https?:\/\/.+\..+/.test(trimmed)) {
        setError('Enter a valid URL starting with http:// or https://')
        return
      }
    }

    setLoading(true)
    try {
      const result =
        inputType === 'text'
          ? await api.submitText(content)
          : await api.submitUrl(url)
      navigate(`/result/${result.submission_id}`, { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="px-4 py-12">
      <div className="mx-auto max-w-2xl">
        <h1 className="text-2xl font-bold text-slate-900">Verify news</h1>
        <p className="mt-1 text-sm text-slate-500">
          {user ? `Signed in as ${user.name}. ` : ''}Submit a claim and let TruthLens AI check it.
        </p>

        <div className="mt-6 card p-6 sm:p-8">
          <div className="inline-flex rounded-lg border border-slate-200 bg-slate-100 p-1">
            <button
              type="button"
              onClick={() => { setInputType('text'); setError('') }}
              className={`rounded-md px-4 py-1.5 text-sm font-semibold transition ${
                inputType === 'text' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              News text
            </button>
            <button
              type="button"
              onClick={() => { setInputType('url'); setError('') }}
              className={`rounded-md px-4 py-1.5 text-sm font-semibold transition ${
                inputType === 'url' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              News URL
            </button>
          </div>

          {error && <p className="alert-error">{error}</p>}

          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            {inputType === 'text' ? (
              <div>
                <label className="label" htmlFor="content">News text</label>
                <textarea
                  id="content"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={8}
                  placeholder="Paste or type the news claim or article content..."
                  className="input mt-2 resize-y font-normal"
                />
                <div className="mt-1 text-right text-xs text-slate-400">
                  <span className={content.length > TEXT_MAX ? 'font-semibold text-red-500' : ''}>
                    {content.length}
                  </span>
                  / {TEXT_MAX}
                </div>
              </div>
            ) : (
              <div>
                <label className="label" htmlFor="url">News URL</label>
                <input
                  id="url"
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com/news/article"
                  className="input mt-2"
                />
                <div className="mt-1 text-right text-xs text-slate-400">{url.length} / {URL_MAX}</div>
              </div>
            )}

            <div className="flex flex-wrap items-center justify-between gap-3">
              <button type="button" onClick={handleClear} className="btn-secondary">
                Clear
              </button>
              <div className="flex items-center gap-3">
                {loading && (
                  <span className="inline-flex items-center gap-2 text-sm text-slate-500">
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
                    Analyzing...
                  </span>
                )}
                <button type="submit" disabled={loading || activeLength === 0} className="btn-primary px-6 py-2.5">
                  Verify
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
