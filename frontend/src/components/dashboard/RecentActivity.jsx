import { Link } from 'react-router-dom'
import { snippet, trustLevelStyles, verdictStyles } from '../../constants/styles'

export default function RecentActivity({ items }) {
  if (!items?.length) {
    return <p className="text-sm text-slate-500">No recent verifications yet.</p>
  }

  return (
    <ul className="divide-y divide-slate-100">
      {items.map((item) => (
        <li key={item.submission_id} className="flex items-center justify-between gap-3 py-3">
          <Link
            to={`/result/${item.submission_id}`}
            className="min-w-0 flex-1 text-left hover:text-blue-600"
          >
            <p className="truncate text-sm font-medium text-slate-800">{snippet(item)}</p>
            <p className="font-mono text-xs text-slate-400">
              {new Date(item.created_at).toLocaleString()}
            </p>
          </Link>
          <div className="flex shrink-0 items-center gap-1.5">
            {item.ai_prediction && (
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${verdictStyles[item.ai_prediction]}`}>
                {item.ai_prediction}
              </span>
            )}
            {item.trust_level && (
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${trustLevelStyles[item.trust_level]}`}>
                {item.trust_level}
              </span>
            )}
          </div>
        </li>
      ))}
    </ul>
  )
}
