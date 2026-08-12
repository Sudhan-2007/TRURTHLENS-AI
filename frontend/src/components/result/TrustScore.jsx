import { trustBarStyles, trustLevelStyles } from '../../constants/styles'

export default function TrustScore({ score, onRun, running }) {
  if (!score) {
    return (
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold text-slate-700">Trust score</p>
          <button onClick={onRun} disabled={running} className="btn-primary px-3 py-1.5 text-xs">
            {running ? 'Calculating...' : 'Calculate trust score'}
          </button>
        </div>
        <p className="mt-2 text-xs text-slate-500">
          Combines the AI assessment, official verification, and evidence quality into one
          credibility indicator (0-100).
        </p>
      </div>
    )
  }

  const level = score.trust_level
  return (
    <div className="rounded-xl border border-slate-200 p-5">
      <div className="flex items-center justify-between">
        <span className={`rounded-full px-4 py-1.5 text-sm font-bold ${trustLevelStyles[level]}`}>
          {level}
        </span>
        <span className="text-3xl font-bold text-slate-800">{score.final_score}</span>
      </div>

      <div className="mt-3 h-3 w-full overflow-hidden rounded-full bg-slate-200">
        <div
          className={`h-full rounded-full ${trustBarStyles[level]}`}
          style={{ width: `${score.final_score}%` }}
        />
      </div>
      <p className="mt-1 text-xs text-slate-500">Trust score (0-100) · v{score.score_version}</p>

      <div className="mt-3 space-y-1.5 border-t border-slate-200 pt-3">
        {[
          ['AI assessment', score.ai_score],
          ['Official verification', score.verification_score],
          ['Evidence quality', score.evidence_score],
          ['Source reliability', score.source_reliability_score],
          ['Semantic similarity', score.similarity_score],
        ].map(([label, value]) => (
          <div key={label} className="flex items-center justify-between text-xs">
            <span className="text-slate-500">{label}</span>
            <span className="font-semibold text-slate-700">{Math.round(value)}</span>
          </div>
        ))}
      </div>

      <p className="mt-3 rounded-lg bg-slate-50 p-3 text-xs leading-relaxed text-slate-600">
        {score.explanation}
      </p>
    </div>
  )
}
