export default function SourceList({ sources }) {
  if (!sources?.length) {
    return <p className="mt-2 text-sm text-slate-500">No trusted source references are available.</p>
  }

  return (
    <div className="mt-2 space-y-2">
      {sources.map((ref, i) => (
        <div key={i} className="rounded-lg bg-slate-50 p-3 text-sm">
          <p className="font-medium text-slate-800">{ref.name}</p>
          <p className="text-xs text-slate-500">
            {ref.domain} · {ref.trust_level} trust · {ref.category || 'source'}
            {ref.publication_date ? ` · published ${ref.publication_date}` : ''}
          </p>
          {ref.url && (
            <a
              href={ref.url}
              target="_blank"
              rel="noreferrer"
              className="mt-1 inline-block break-all text-xs text-blue-600 hover:underline"
            >
              {ref.title || ref.url}
            </a>
          )}
        </div>
      ))}
    </div>
  )
}
