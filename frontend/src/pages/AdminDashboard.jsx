import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import StatsCard from '../components/dashboard/StatsCard'
import VerificationChart from '../components/dashboard/VerificationChart'

function SourcesTable({ sources }) {
  if (!sources?.length) {
    return <p className="text-sm text-slate-500">No trusted sources configured.</p>
  }
  return (
    <div className="card overflow-x-auto">
      <table className="w-full min-w-[560px] text-left text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
            <th className="px-4 py-3">Source</th>
            <th className="px-4 py-3">Category</th>
            <th className="px-4 py-3">Type</th>
            <th className="px-4 py-3">Trust</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {sources.map((source) => (
            <tr key={source.domain} className="hover:bg-slate-50">
              <td className="px-4 py-3">
                <p className="font-medium text-slate-800">{source.name}</p>
                <p className="font-mono text-xs text-slate-400">{source.domain}</p>
              </td>
              <td className="px-4 py-3 text-xs text-slate-600">{source.category}</td>
              <td className="px-4 py-3 text-xs text-slate-600">{source.source_type}</td>
              <td className="px-4 py-3">
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${
                    source.trust_level === 'high'
                      ? 'bg-green-100 text-green-700'
                      : source.trust_level === 'medium'
                        ? 'bg-amber-100 text-amber-700'
                        : 'bg-red-100 text-red-700'
                  }`}
                >
                  {source.trust_level}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function UsersTable({ users }) {
  if (!users?.length) return <p className="text-sm text-slate-500">No users registered.</p>
  return (
    <div className="card overflow-x-auto">
      <table className="w-full min-w-[480px] text-left text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
            <th className="px-4 py-3">Name</th>
            <th className="px-4 py-3">Email</th>
            <th className="px-4 py-3">Role</th>
            <th className="px-4 py-3">Joined</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {users.map((user) => (
            <tr key={user.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 font-medium text-slate-800">{user.name}</td>
              <td className="px-4 py-3 text-xs text-slate-600">{user.email}</td>
              <td className="px-4 py-3">
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${
                    user.role === 'admin'
                      ? 'bg-purple-100 text-purple-700'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {user.role}
                </span>
              </td>
              <td className="px-4 py-3 text-xs text-slate-500">
                {new Date(user.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function Section({ title, description, children }) {
  return (
    <section className="mt-8">
      <h2 className="text-lg font-bold text-slate-900">{title}</h2>
      {description && <p className="mt-0.5 text-sm text-slate-500">{description}</p>}
      <div className="mt-4">{children}</div>
    </section>
  )
}

export default function AdminDashboard() {
  const { user } = useAuth()
  const [overview, setOverview] = useState(null)
  const [stats, setStats] = useState(null)
  const [sources, setSources] = useState(null)
  const [users, setUsers] = useState(null)
  const [health, setHealth] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (user?.role !== 'admin') return
    let active = true
    Promise.all([
      api.getAdminDashboard(),
      api.getAdminStatistics(),
      api.listSources(),
      api.listUsers(),
      api.healthDb().catch(() => null),
    ])
      .then(([overviewData, statsData, sourcesData, usersData, healthData]) => {
        if (!active) return
        setOverview(overviewData)
        setStats(statsData)
        setSources(sourcesData)
        setUsers(usersData)
        setHealth(healthData)
      })
      .catch((err) => active && setError(err.message))
    return () => {
      active = false
    }
  }, [user])

  if (user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />
  }

  if (error) {
    return (
      <div className="px-4 py-16">
        <div className="mx-auto max-w-2xl">
          <p className="alert-error">{error}</p>
        </div>
      </div>
    )
  }

  if (!overview || !stats || !sources || !users) {
    return (
      <div className="px-4 py-20 text-center text-slate-400">
        <span className="inline-block h-6 w-6 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
        <p className="mt-3 text-sm">Loading admin dashboard...</p>
      </div>
    )
  }

  return (
    <div className="px-4 py-12">
      <div className="mx-auto max-w-6xl">
        <h1 className="text-2xl font-bold text-slate-900">Admin dashboard</h1>
        <p className="mt-1 text-sm text-slate-500">System-wide activity and analytics.</p>

        <Section title="System overview">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            <StatsCard label="Total users" value={overview.total_users} />
            <StatsCard label="Active users" value={overview.active_users} />
            <StatsCard label="Submissions" value={overview.total_submissions} />
            <StatsCard label="Completed" value={overview.completed_verifications} accent="text-green-600" />
            <StatsCard label="Failed" value={overview.failed_verifications} accent="text-red-600" />
            <StatsCard label="Fake predictions" value={overview.fake_predictions} accent="text-red-600" />
            <StatsCard label="Real predictions" value={overview.real_predictions} accent="text-green-600" />
            <StatsCard label="Unverified claims" value={overview.unverified_claims} />
            <StatsCard label="Avg trust score" value={overview.average_trust_score} accent="text-blue-600" sub="/ 100" />
            <StatsCard label="Official sources" value={overview.official_sources} />
          </div>
        </Section>

        <Section title="System health">
          <div className="flex flex-wrap gap-3">
            <StatsCard
              label="Database"
              value={health?.connected ? 'Connected' : 'Offline'}
              accent={health?.connected ? 'text-green-600' : 'text-red-600'}
            />
            <StatsCard label="Database mode" value={health?.mode || '—'} />
            <StatsCard label="Database" value={health?.database || '—'} />
          </div>
        </Section>

        <Section title="News analytics">
          <div className="grid gap-6 lg:grid-cols-2">
            <VerificationChart type="pie" data={stats.verification_distribution} />
            <VerificationChart type="line" trend={stats.verification_trend} />
          </div>
        </Section>

        <Section title="AI analytics">
          <div className="grid gap-6 lg:grid-cols-2">
            <VerificationChart type="doughnut" data={stats.prediction_distribution} />
            <VerificationChart type="bar" data={stats.trust_score_distribution} />
          </div>
        </Section>

        <Section title="User analytics" description="Registered accounts and activity.">
          <UsersTable users={users} />
        </Section>

        <Section title="Source management" description="Approved official sources used for verification.">
          <SourcesTable sources={sources} />
        </Section>
      </div>
    </div>
  )
}
