export const statusStyles = {
  submitted: 'bg-slate-100 text-slate-600',
  processing: 'bg-amber-100 text-amber-700',
  completed: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
}

export const verdictStyles = {
  REAL: 'bg-green-600 text-white',
  FAKE: 'bg-red-600 text-white',
}

export const verificationStyles = {
  SUPPORTED: 'bg-green-100 text-green-700 border-green-200',
  CONTRADICTED: 'bg-red-100 text-red-700 border-red-200',
  PARTIALLY_SUPPORTED: 'bg-amber-100 text-amber-700 border-amber-200',
  UNVERIFIED: 'bg-slate-100 text-slate-600 border-slate-200',
}

export const trustLevelStyles = {
  HIGH: 'bg-green-600 text-white',
  MEDIUM: 'bg-amber-500 text-white',
  LOW: 'bg-orange-500 text-white',
  VERY_LOW: 'bg-red-600 text-white',
}

export const trustBarStyles = {
  HIGH: 'bg-green-500',
  MEDIUM: 'bg-amber-500',
  LOW: 'bg-orange-500',
  VERY_LOW: 'bg-red-600',
}

export const chartColors = {
  SUPPORTED: '#16a34a',
  CONTRADICTED: '#dc2626',
  PARTIALLY_SUPPORTED: '#f59e0b',
  UNVERIFIED: '#94a3b8',
  HIGH: '#16a34a',
  MEDIUM: '#f59e0b',
  LOW: '#f97316',
  VERY_LOW: '#dc2626',
  REAL: '#16a34a',
  FAKE: '#dc2626',
}

export const palette = ['#2563eb', '#dc2626', '#f59e0b', '#64748b', '#16a34a', '#8b5cf6']

export function snippet(item, length = 90) {
  if (item.input_type === 'text') return item.content?.slice(0, length) || 'Text submission'
  return item.url || 'URL submission'
}
