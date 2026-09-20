import { Empty, ErrorState, Kpi, Loading, Panel, SeverityTag } from '../components/Primitives'
import { api } from '../lib/api'
import { useData } from '../lib/useData'
import { day, money } from '../lib/format'

const BAND_TONE = { Low: 'text-clear', Medium: 'text-hivis', High: 'text-hazard' }

export default function Insurance({ projectId, refreshKey }) {
  const { data, error, loading, reload } = useData(() => api.insurance(projectId), [projectId, refreshKey])

  if (loading && !data) return <Loading label="Insurance Agent assessing exposure" />
  if (error) return <ErrorState error={error} onRetry={reload} />

  const m = data.metrics

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Kpi label="Total exposure" value={money(m.total_exposure)} tone="text-hazard" />
        <Kpi label="Open cases" value={m.open_cases} tone="text-caution" />
        <Kpi label="Insurance risk band" value={m.insurance_risk_band} tone={BAND_TONE[m.insurance_risk_band]} sub={`Index ${m.insurance_risk_index}/100`} />
        <Kpi label="Average claim value" value={money(m.avg_claim_value)} sub={`${m.claims_90d} incidents in 90 days`} />
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <Panel className="lg:col-span-2" title="Claim register" note={data.summary}>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[600px] text-sm">
              <thead className="text-left text-xs text-steel">
                <tr className="border-b border-site-500/60">
                  <th className="pb-2 font-medium">Case</th>
                  <th className="pb-2 font-medium">Claim type</th>
                  <th className="pb-2 font-medium">Estimated cost</th>
                  <th className="pb-2 font-medium">Claim risk</th>
                  <th className="pb-2 font-medium">Status</th>
                  <th className="pb-2 font-medium">Documentation</th>
                </tr>
              </thead>
              <tbody>
                {m.cases.map((c) => (
                  <tr key={c.case_id} className="border-b border-site-500/30">
                    <td className="metric py-2 pr-3 text-steel">#{c.case_id}</td>
                    <td className="py-2 pr-3 text-concrete">{c.claim_type}</td>
                    <td className="metric py-2 pr-3 text-concrete">{money(c.estimated_cost)}</td>
                    <td className="py-2 pr-3">
                      <div className="h-1.5 w-20 bg-site-600">
                        <div className={`h-full ${c.risk_score >= 60 ? 'bg-hazard' : c.risk_score >= 30 ? 'bg-caution' : 'bg-clear'}`} style={{ width: `${Math.min(c.risk_score, 100)}%` }} />
                      </div>
                    </td>
                    <td className="py-2 pr-3 capitalize text-steel">{c.status}</td>
                    <td className={`py-2 capitalize ${c.documentation_status === 'complete' ? 'text-clear' : 'text-caution'}`}>
                      {c.documentation_status}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!m.cases.length && <Empty>No insurance cases filed for this project.</Empty>}
          </div>
        </Panel>

        <Panel title="Exposure findings" note="What the underwriter will ask about">
          {data.findings.length ? (
            <ul className="space-y-3 text-sm">
              {data.findings.map((f, i) => (
                <li key={`${f.title}-${i}`} className="border-l-2 border-site-500 pl-3">
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
            <Empty>Exposure is within the expected band.</Empty>
          )}
        </Panel>
      </div>
    </div>
  )
}
