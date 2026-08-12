import { Link } from 'react-router-dom'
import {
  snippet,
  statusStyles,
  trustLevelStyles,
  verdictStyles,
} from '../../constants/styles'

export default function HistoryTable({ items, onDelete }) {
  if (!items?.length) {
    return (
      <div className="card p-8 text-center">
        <p className="text-slate-500">No submissions match your filters.</p>
      </div>
    )
  }

  return (
    <div className="card overflow-x-auto">
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
            <th className="px-4 py-3">Submission</th>
            <th className="px-4 py-3">Date</th>
            <th className="px-4 py-3">Prediction</th>
            <th className="px-4 py-3">Verification</th>
            <th className="px-4 py-3">Trust</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items.map((item) => (
            <tr key={item.submission_id} className="hover:bg-slate-50">
              <td className="max-w-[240px] px-4 py-3">
                <Link to={`/result/${item.submission_id}`} className="block hover:text-blue-600">
                  <p className="truncate font-medium text-slate-800">{snippet(item, 70)}</p>
                  <p className="font-mono text-[11px] text-slate-400">{item.submission_id}</p>
                </Link>
              </td>
              <td className="whitespace-nowrap px-4 py-3 text-xs text-slate-500">
                {new Date(item.created_at).toLocaleDateString()}
              </td>
              <td className="px-4 py-3">
                {item.ai_prediction ? (
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${verdictStyles[item.ai_prediction]}`}>
                    {item.ai_prediction}
                  </span>
                ) : (
                  <span className="text-xs text-slate-400">—</span>
                )}
              </td>
              <td className="px-4 py-3 text-xs text-slate-600">
                {item.verification_status || '—'}
              </td>
              <td className="px-4 py-3">
                {item.trust_level ? (
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${trustLevelStyles[item.trust_level]}`}>
                    {item.trust_level}
                  </span>
                ) : (
                  <span className="text-xs text-slate-400">—</span>
                )}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${statusStyles[item.status]}`}>
                  {item.status}
                </span>
              </td>
              <td className="whitespace-nowrap px-4 py-3 text-right">
                <Link
                  to={`/result/${item.submission_id}`}
                  className="mr-2 text-xs font-medium text-blue-600 hover:underline"
                >
                  View
                </Link>
                <button
                  onClick={() => onDelete(item)}
                  className="text-xs font-medium text-red-600 hover:underline"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
