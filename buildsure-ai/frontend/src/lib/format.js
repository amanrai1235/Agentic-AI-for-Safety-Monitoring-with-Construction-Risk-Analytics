export const money = (value) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value || 0)

export const when = (value) =>
  new Date(value).toLocaleString('en-GB', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })

export const day = (value) =>
  new Date(value).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })

export const severityColor = {
  critical: 'text-hazard border-hazard/50 bg-hazard/10',
  high: 'text-caution border-caution/50 bg-caution/10',
  medium: 'text-hivis border-hivis/40 bg-hivis/10',
  low: 'text-clear border-clear/40 bg-clear/10',
}

export const scoreColor = (score) =>
  score >= 80 ? 'text-clear' : score >= 65 ? 'text-hivis' : score >= 45 ? 'text-caution' : 'text-hazard'
