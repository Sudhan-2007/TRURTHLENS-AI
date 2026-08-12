import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import RecentActivity from '../components/dashboard/RecentActivity'
import StatsCard from '../components/dashboard/StatsCard'
import VerificationChart from '../components/dashboard/VerificationChart'

export default function Dashboard() {
  const [overview, setOverview] = useState(null)
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    Promise.all([api.getUserDashboard(), api.getUserStatistics()])
      .then(([overviewData, statsData]) => {
        if (!active) return
        setOverview(overviewData)
        setStats(statsData)
      })
      .catch((err) => active && setError(err.message))
    return () => {
      active = false
    }
  }, [])

  if (error) {
    return (
      <div className="px-4 py-16">
        <div className="mx-auto max-w-2xl">
          <p className="alert-error">{error}</p>
        </div>
      </div>
    )
  }

  if (!overview || !stats) {
    return (
      <div className="px-4 py-20 text-center text-slate-400">
        <span className="inline-block h-6 w-6 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
        <p className="mt-3 text-sm">Loading dashboard...</p>
      </div>
    )
  }

  return (
    <div className="px-4 py-12">
      <div className="mx-auto max-w-6xl">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
            <p className="mt-1 text-sm text-slate-500">Your verification activity at a glance.</p>
          </div>
          <Link to="/verify" className="btn-primary">Verify news</Link>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <StatsCard label="Submissions" value={overview.total_submissions} />
          <StatsCard label="Completed" value={overview.completed_verifications} />
          <StatsCard label="Fake predictions" value={overview.fake_predictions} accent="text-red-600" />
          <StatsCard label="Real predictions" value={overview.real_predictions} accent="text-green-600" />
          <StatsCard label="Unverified" value={overview.unverified_claims} />
          <StatsCard
            label="Avg trust score"
            value={overview.average_trust_score}
            accent="text-blue-600"
            sub="/ 100"
          />
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-4">
            <div className="flex items-center justify-between">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Recent verifications
              </p>
              <Link to="/history" className="text-xs font-medium text-blue-600 hover:underline">
                View history
              </Link>
            </div>
            <div className="mt-2">
              <RecentActivity items={overview.recent_verifications} />
            </div>
          </div>

          <VerificationChart type="bar" data={stats.trust_score_distribution} />
          <VerificationChart type="pie" data={stats.verification_distribution} />
          <VerificationChart type="doughnut" data={stats.prediction_distribution} />
          <VerificationChart type="line" trend={stats.verification_trend} />
        </div>
      </div>
    </div>
  )
}
