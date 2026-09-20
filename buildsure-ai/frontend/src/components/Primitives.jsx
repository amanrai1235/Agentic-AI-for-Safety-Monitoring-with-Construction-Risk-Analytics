import { severityColor, scoreColor } from '../lib/format'

export function Panel({ title, note, action, children, className = '' }) {
  return (
    <section className={`panel ${className}`}>
      {(title || action) && (
        <header className="flex items-baseline justify-between gap-3 border-b border-site-500/60 px-4 py-3">
          <div>
            <h2 className="font-display text-lg font-semibold leading-none text-concrete">{title}</h2>
            {note && <p className="mt-1 text-xs text-steel">{note}</p>}
          </div>
          {action}
        </header>
      )}
      <div className="p-4">{children}</div>
    </section>
  )
}

export function Kpi({ label, value, unit, tone = 'text-concrete', sub }) {
  return (
    <div className="panel px-4 py-3">
      <p className="text-xs text-steel">{label}</p>
      <p className={`metric mt-1 text-3xl leading-none ${tone}`}>
        {value}
        {unit && <span className="ml-1 text-base text-steel">{unit}</span>}
      </p>
      {sub && <p className="mt-1 text-xs text-steel">{sub}</p>}
    </div>
  )
}

export function SeverityTag({ severity }) {
  return (
    <span className={`rounded-sm border px-1.5 py-0.5 text-[11px] font-medium ${severityColor[severity] ?? severityColor.low}`}>
      {severity}
    </span>
  )
}

export function Meter({ label, value, suffix = '%', tone }) {
  const width = Math.max(0, Math.min(100, value ?? 0))
  const color = tone ?? (width >= 90 ? 'bg-clear' : width >= 75 ? 'bg-hivis' : width >= 50 ? 'bg-caution' : 'bg-hazard')
  return (
    <div className="mb-3 last:mb-0">
      <div className="flex items-baseline justify-between text-sm">
        <span className="text-concrete">{label}</span>
        <span className="metric text-steel">{width}{suffix}</span>
      </div>
      <div className="mt-1 h-1.5 w-full bg-site-600">
        <div className={`h-full ${color}`} style={{ width: `${width}%` }} />
      </div>
    </div>
  )
}

export function Empty({ children }) {
  return <p className="py-6 text-center text-sm text-steel">{children}</p>
}

export function Loading({ label = 'Reading site data' }) {
  return (
    <div className="flex h-48 items-center justify-center text-sm text-steel">
      <span className="mr-2 inline-block h-2 w-2 animate-pulse bg-hivis" />
      {label}…
    </div>
  )
}

export function ErrorState({ error, onRetry }) {
  return (
    <div className="panel p-6">
      <h2 className="font-display text-xl text-hazard">The platform could not reach the backend</h2>
      <p className="mt-2 max-w-prose text-sm text-steel">
        Start the API with <code className="bg-site-600 px-1">uvicorn app.main:app --reload</code> in the backend folder,
        then retry. Details: {String(error?.message ?? error)}
      </p>
      {onRetry && (
        <button onClick={onRetry} className="mt-4 bg-hivis px-3 py-1.5 font-display text-sm font-semibold text-site-900">
          Retry
        </button>
      )}
    </div>
  )
}

export function ScoreDial({ score, caption }) {
  const clamped = Math.max(0, Math.min(100, score ?? 0))
  return (
    <div className="flex items-end gap-4">
      <div>
        <p className={`metric text-6xl leading-none ${scoreColor(clamped)}`}>{clamped}</p>
        <p className="text-xs text-steel">out of 100</p>
      </div>
      <div className="flex-1">
        <div className="h-2 w-full bg-site-600">
          <div className={`h-full ${clamped >= 80 ? 'bg-clear' : clamped >= 65 ? 'bg-hivis' : clamped >= 45 ? 'bg-caution' : 'bg-hazard'}`} style={{ width: `${clamped}%` }} />
        </div>
        {caption && <p className="mt-2 text-sm text-steel">{caption}</p>}
      </div>
    </div>
  )
}
