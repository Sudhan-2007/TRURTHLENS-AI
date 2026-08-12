import { verificationStyles } from '../../constants/styles'

export default function EvidenceList({ items, emptyMessage }) {
  if (!items?.length) {
    return (
      <p className="mt-2 text-sm leading-relaxed text-slate-500">
        {emptyMessage ||
          'No trusted evidence matching this claim was found. This does not mean the claim is false.'}
      </p>
    )
  }

  return (
    <div className="mt-2 space-y-2">
      {items.map((item, i) => {
        const status = item.evidence_status || item.status
        const similarity = item.similarity_score
        return (
          <div key={i} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
            <div className="flex flex-wrap items-center gap-2">
              <span
                className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${verificationStyles[status]}`}
              >
                {item.label || status}
              </span>
              {similarity != null && (
                <span className="text-xs font-semibold text-slate-700">
                  {Math.round(similarity * 100)}% match
                </span>
              )}
            </div>
            {item.claim && <p className="mt-1.5 text-xs italic text-slate-500">Claim: {item.claim}</p>}
            {item.meaning && <p className="mt-1 text-[11px] text-slate-400">{item.meaning}</p>}
            <p className="mt-1.5 text-sm leading-relaxed text-slate-700">
              {item.evidence_summary}
            </p>
            {item.source_url && (
              <a
                href={item.source_url}
                target="_blank"
                rel="noreferrer"
                className="mt-1.5 inline-block text-xs text-blue-600 hover:underline"
              >
                {item.source_name} ({item.source_domain})
              </a>
            )}
          </div>
        )
      })}
    </div>
  )
}
