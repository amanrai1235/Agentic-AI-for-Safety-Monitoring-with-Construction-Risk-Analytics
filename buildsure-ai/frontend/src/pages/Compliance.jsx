import { useState } from 'react'
import { Empty, ErrorState, Kpi, Loading, Meter, Panel, SeverityTag } from '../components/Primitives'
import { api } from '../lib/api'
import { useData } from '../lib/useData'
import { day } from '../lib/format'

const STATUS_TONE = {
  compliant: 'text-clear',
  pending: 'text-caution',
  violation: 'text-hazard',
}

export default function Compliance({ projectId, refreshKey }) {
  const dashboard = useData(() => api.compliance(projectId), [projectId, refreshKey])
  const checks = useData(() => api.complianceChecks(projectId), [projectId, refreshKey])
  const [filter, setFilter] = useState('all')

  if (dashboard.loading && !dashboard.data) return <Loading label="Compliance Agent validating regulations" />
  if (dashboard.error) return <ErrorState error={dashboard.error} onRetry={dashboard.reload} />

  const c = dashboard.data.compliance
  const rows = (checks.data ?? []).filter((row) => filter === 'all' || row.compliance_status === filter)

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Kpi label="Compliance score" value={c.metrics.compliance_score} unit="%" tone="text-clear" />
        <Kpi label="Open violations" value={c.metrics.open_violations} tone="text-hazard" />
        <Kpi label="Pending inspections" value={c.metrics.pending_inspections} tone="text-caution" />
        <Kpi label="Audit readiness" value={c.metrics.audit_readiness} unit="%" tone="text-hivis" sub={`Documentation ${c.metrics.documentation_status}`} />
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <Panel title="Compliance by category" note={c.summary}>
          {c.metrics.by_category.map((row) => (
            <Meter key={row.category} label={`${row.category} (${row.checks} checks)`} value={row.rate} />
          ))}
        </Panel>

        <Panel
          className="lg:col-span-2"
          title="Regulatory register"
          note="Every requirement tracked for this site"
          action={
            <div className="flex gap-1">
              {['all', 'compliant', 'pending', 'violation'].map((option) => (
                <button
                  key={option}
                  onClick={() => setFilter(option)}
                  className={`border px-2 py-1 text-xs capitalize ${
                    filter === option ? 'border-hivis text-hivis' : 'border-site-500 text-steel hover:text-concrete'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          }
        >
          <div className="max-h-[360px] overflow-auto">
            <table className="w-full min-w-[560px] text-sm">
              <thead className="sticky top-0 bg-site-700 text-left text-xs text-steel">
                <tr className="border-b border-site-500/60">
                  <th className="pb-2 font-medium">Requirement</th>
                  <th className="pb-2 font-medium">Category</th>
                  <th className="pb-2 font-medium">Status</th>
                  <th className="pb-2 font-medium">Due</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.compliance_id} className="border-b border-site-500/30">
                    <td className="py-2 pr-3 text-concrete">
                      {row.regulation_name}
                      {row.finding && <p className="text-xs text-steel">{row.finding}</p>}
                    </td>
                    <td className="py-2 pr-3 text-steel">{row.category}</td>
                    <td className={`py-2 pr-3 capitalize ${STATUS_TONE[row.compliance_status]}`}>{row.compliance_status}</td>
                    <td className="py-2 text-xs text-steel">{row.due_date ? day(row.due_date) : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!rows.length && <Empty>Nothing matches this filter.</Empty>}
          </div>
        </Panel>
      </div>

      <Panel title="Compliance findings and corrective actions">
        {c.findings.length ? (
          <ul className="grid gap-3 md:grid-cols-2">
            {c.findings.map((f) => (
              <li key={f.title} className="border-l-2 border-site-500 pl-3 text-sm">
                <div className="flex items-center gap-2">
                  <SeverityTag severity={f.severity} />
                  <span className="text-concrete">{f.title}</span>
                </div>
                <p className="mt-1 text-xs text-steel">{f.detail}</p>
                {f.recommendation && <p className="mt-1 text-xs text-hivis">{f.recommendation}</p>}
              </li>
            ))}
          </ul>
        ) : (
          <Empty>All tracked requirements are met.</Empty>
        )}
      </Panel>
    </div>
  )
}
