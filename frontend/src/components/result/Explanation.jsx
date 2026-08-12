import {
  trustLevelStyles,
  verificationStyles,
  verdictStyles,
} from '../../constants/styles'
import EvidenceList from './EvidenceList'
import SourceList from './SourceList'

export default function Explanation({ explanation, onRun, running }) {
  if (!explanation) {
    return (
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold text-slate-700">Why this result?</p>
          <button onClick={onRun} disabled={running} className="btn-primary px-3 py-1.5 text-xs">
            {running ? 'Generating...' : 'Generate explanation'}
          </button>
        </div>
        <p className="mt-2 text-xs text-slate-500">
          A transparent, evidence-based explanation of the AI prediction, official verification,
          and trust score for this submission.
        </p>
      </div>
    )
  }

  const c = explanation.components || {}
  const confidence = c.confidence ?? 0
  const verificationConfidence = c.verification_confidence ?? 0
  const status = c.verification_status

  return (
    <div className="space-y-5">
      <div className="rounded-xl border border-slate-200 p-5">
        <p className="label">Overall result</p>
        <p className="mt-1 text-base font-medium leading-relaxed text-slate-800">
          {explanation.overall_result}
        </p>
      </div>

      <div className="rounded-xl border border-slate-200 p-5">
        <div className="flex items-center justify-between">
          <p className="label">Trust score</p>
          <span className={`rounded-full px-3 py-1 text-xs font-bold ${trustLevelStyles[c.trust_level]}`}>
            {c.trust_level}
          </span>
        </div>
        <p className="mt-1 text-2xl font-bold text-slate-800">{c.final_score}/100</p>
        <p className="mt-2 text-sm leading-relaxed text-slate-600">
          {explanation.trust_score_explanation}
        </p>
      </div>

      <div className="rounded-xl border border-slate-200 p-5">
        <div className="flex items-center justify-between">
          <p className="label">AI assessment</p>
          <span className={`rounded-full px-3 py-1 text-xs font-bold ${verdictStyles[c.prediction]}`}>
            {c.prediction === 'REAL' ? 'Likely REAL' : 'Likely FAKE'}
          </span>
        </div>
        <p className="mt-1 text-sm text-slate-500">
          {Math.round(confidence * 100)}% confidence · {c.model_name} v{c.model_version}
        </p>
        <p className="mt-2 text-sm leading-relaxed text-slate-600">{explanation.ai_explanation}</p>
      </div>

      <div className="rounded-xl border border-slate-200 p-5">
        <div className="flex items-center justify-between">
          <p className="label">Official verification</p>
          <span className={`rounded-full border px-3 py-1 text-xs font-bold ${verificationStyles[status]}`}>
            {status}
          </span>
        </div>
        <p className="mt-1 text-sm text-slate-500">
          {Math.round(verificationConfidence * 100)}% confidence
        </p>
        <p className="mt-2 text-sm leading-relaxed text-slate-600">
          {explanation.verification_explanation}
        </p>
      </div>

      <div className="rounded-xl border border-slate-200 p-5">
        <p className="label">Evidence</p>
        <EvidenceList items={explanation.evidence_summary} />
      </div>

      <div className="rounded-xl border border-slate-200 p-5">
        <p className="label">Sources</p>
        <SourceList sources={explanation.source_references} />
      </div>

      <div className="rounded-xl border border-slate-200 p-5">
        <p className="label">Why this result?</p>
        <p className="mt-2 text-sm leading-relaxed text-slate-600">{explanation.ai_explanation}</p>
        <p className="mt-2 text-sm leading-relaxed text-slate-600">
          {explanation.verification_explanation}
        </p>
        <p className="mt-2 text-sm leading-relaxed text-slate-600">
          {explanation.trust_score_explanation}
        </p>
      </div>

      <div className="rounded-xl border border-amber-200 bg-amber-50 p-5">
        <p className="label text-amber-700">Limitations</p>
        <ul className="mt-2 list-disc space-y-1 pl-4 text-xs leading-relaxed text-amber-800">
          {explanation.limitations.map((limit, i) => (
            <li key={i}>{limit}</li>
          ))}
        </ul>
      </div>

      <p className="text-center text-[11px] text-slate-400">
        Explanation v{explanation.explanation_version}
      </p>
    </div>
  )
}
