import { useState } from 'react'
import { chartColors, palette } from '../../constants/styles'

function Donut({ data, hole = false }) {
  const total = data.reduce((sum, d) => sum + d.count, 0)
  if (total === 0) {
    return (
      <div className="flex h-40 w-40 items-center justify-center rounded-full bg-slate-100 text-xs text-slate-400">
        No data
      </div>
    )
  }
  let acc = 0
  const stops = data.map((d, i) => {
    const start = (acc / total) * 100
    acc += d.count
    const end = (acc / total) * 100
    const color = chartColors[d.value] || palette[i % palette.length]
    return `${color} ${start}% ${end}%`
  })
  const gradient = `conic-gradient(${stops.join(', ')})`

  if (!hole) {
    return <div className="h-40 w-40 rounded-full" style={{ background: gradient }} />
  }
  return (
    <div className="relative h-40 w-40 rounded-full" style={{ background: gradient }}>
      <div className="absolute inset-[28%] rounded-full bg-white" />
    </div>
  )
}

function Legend({ data }) {
  return (
    <ul className="space-y-1">
      {data.map((d) => (
        <li key={d.value} className="flex items-center gap-2 text-xs">
          <span
            className="h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: chartColors[d.value] || palette[0] }}
          />
          <span className="text-slate-600">{d.value}</span>
          <span className="ml-auto font-semibold text-slate-800">{d.count}</span>
        </li>
      ))}
    </ul>
  )
}

function Bars({ data }) {
  const max = Math.max(...data.map((d) => d.count), 1)
  return (
    <div className="space-y-2">
      {data.map((d) => (
        <div key={d.value} className="flex items-center gap-2">
          <span className="w-20 shrink-0 text-xs text-slate-500">{d.value}</span>
          <div className="h-4 flex-1 overflow-hidden rounded bg-slate-100">
            <div
              className="h-full rounded"
              style={{
                width: `${(d.count / max) * 100}%`,
                backgroundColor: chartColors[d.value] || palette[0],
              }}
            />
          </div>
          <span className="w-8 shrink-0 text-right text-xs font-semibold text-slate-700">
            {d.count}
          </span>
        </div>
      ))}
    </div>
  )
}

function TrendLine({ trend }) {
  const [period, setPeriod] = useState('daily')
  const data = trend[period] || []
  const max = Math.max(...data.map((d) => d.count), 1)
  const width = 440
  const height = 140
  const pad = 20
  const stepX = data.length > 1 ? (width - pad * 2) / (data.length - 1) : 0
  const points = data.map((d, i) => {
    const x = pad + i * stepX
    const y = height - pad - (d.count / max) * (height - pad * 2)
    return [x, y]
  })

  return (
    <div>
      <div className="mb-3 flex gap-1">
        {['daily', 'weekly', 'monthly'].map((p) => (
          <button
            key={p}
            onClick={() => setPeriod(p)}
            className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${
              period === p ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {p}
          </button>
        ))}
      </div>
      {data.length ? (
        <div>
          <svg viewBox={`0 0 ${width} ${height}`} className="w-full">
            <polyline
              fill="none"
              stroke="#2563eb"
              strokeWidth="2"
              points={points.map(([x, y]) => `${x},${y}`).join(' ')}
            />
            {points.map(([x, y], i) => (
              <circle key={i} cx={x} cy={y} r="3" fill="#2563eb" />
            ))}
          </svg>
          <div className="mt-1 flex justify-between text-[10px] text-slate-400">
            <span>{data[0]?.period}</span>
            <span>{data[data.length - 1]?.period}</span>
          </div>
        </div>
      ) : (
        <p className="text-sm text-slate-400">No trend data</p>
      )}
    </div>
  )
}

export default function VerificationChart({ type, data, trend }) {
  if (type === 'line') {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
          Verification trend
        </p>
        <div className="mt-3">
          <TrendLine trend={trend} />
        </div>
      </div>
    )
  }

  const counts = Array.isArray(data) ? data : []

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {type === 'bar' ? 'Trust score distribution' : type === 'doughnut' ? 'AI prediction distribution' : 'Verification distribution'}
      </p>
      <div className="mt-4 flex items-center justify-center gap-6">
        {type === 'bar' ? (
          <div className="w-full">
            <Bars data={counts} />
          </div>
        ) : (
          <>
            <Donut data={counts} hole={type === 'doughnut'} />
            <Legend data={counts} />
          </>
        )}
      </div>
    </div>
  )
}
