import { Empty, ErrorState, Kpi, Loading, Panel, SeverityTag } from '../components/Primitives'
import RiskMatrix from '../components/RiskMatrix'
import { api } from '../lib/api'
import { useData } from '../lib/useData'
import { when } from '../lib/format'

export default function SiteRisk({ projectId, refreshKey }) {
  const { data, error, loading, reload } = useData(() => api.siteRisk(projectId), [projectId, refreshKey])

  if (loading && !data) return <Loading label="Site Risk Agent scanning site data" />
  if (error) return <ErrorState error={error} onRetry={reload} />

  const m = data.metrics

  const closeRisk = async (riskId) => {
    await api.updateRisk(riskId, 'closed')
    reload()
  }

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Kpi label="Active risks" value={m.active_risks} tone="text-caution" />
        <Kpi label="High-risk zones" value={m.high_risk_zones} tone="text-hazard" />
        <Kpi label="Hazards detected (7 days)" value={m.hazards_detected_7d} />
        <Kpi label="Site risk score" value={m.site_risk_score} unit="/100" tone="text-hivis" />
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <Panel
          className="lg:col-span-2"
          title="Risk heat map"
          note="Probability × impact, before and after the mitigation on record"
        >
          <div className="grid gap-6 md:grid-cols-2">
            <RiskMatrix grid={m.heatmap} title="Inherent risk" note="As detected on site" />
            <RiskMatrix grid={m.residual_heatmap} title="Residual risk" note="After recorded mitigation" />
          </div>
        </Panel>

        <Panel title="Risk distribution" note={data.summary}>
          {m.distribution.length ? (
            m.distribution.map((row) => (
              <div key={row.type} className="mb-3 last:mb-0">
                <div className="flex items-baseline justify-between text-sm">
                  <span className="capitalize text-concrete">{row.type}</span>
                  <span className="metric text-steel">{row.share}%</span>
                </div>
                <div className="mt-1 h-1.5 w-full bg-site-600">
                  <div className="h-full bg-hivis" style={{ width: `${row.share}%` }} />
                </div>
              </div>
            ))
          ) : (
            <Empty>No open hazards on this site. Log one from the Projects screen.</Empty>
          )}
        </Panel>
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <Panel className="lg:col-span-2" title="Hazard detection panel" note="Latest detections from CCTV, sensors and inspections">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-sm">
              <thead className="text-left text-xs text-steel">
                <tr className="border-b border-site-500/60">
                  <th className="pb-2 font-medium">Hazard</th>
                  <th className="pb-2 font-medium">Zone</th>
                  <th className="pb-2 font-medium">P × I</th>
                  <th className="pb-2 font-medium">Severity</th>
                  <th className="pb-2 font-medium">Detected</th>
                  <th className="pb-2 font-medium" />
                </tr>
              </thead>
              <tbody>
                {data.recent_risks.map((risk) => (
                  <tr key={risk.risk_id} className="border-b border-site-500/30 align-top">
                    <td className="py-2 pr-3">
                      <p className="capitalize text-concrete">{risk.risk_type}</p>
                      <p className="text-xs text-steel">{risk.description}</p>
                    </td>
                    <td className="py-2 pr-3 text-steel">{risk.zone}</td>
                    <td className="metric py-2 pr-3 text-steel">{risk.probability}×{risk.impact}</td>
                    <td className="py-2 pr-3"><SeverityTag severity={risk.severity} /></td>
                    <td className="py-2 pr-3 text-xs text-steel">{when(risk.detected_at)}</td>
                    <td className="py-2 text-right">
                      <button onClick={() => closeRisk(risk.risk_id)} className="border border-site-500 px-2 py-1 text-xs text-steel hover:border-hivis hover:text-hivis">
                        Close out
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!data.recent_risks.length && <Empty>No open hazards recorded.</Empty>}
          </div>
        </Panel>

        <Panel title="AI risk recommendations" note="Ranked by exposure by the Site Risk Agent">
          {data.recommendations.length ? (
            <ol className="space-y-3 text-sm">
              {data.recommendations.map((rec, index) => (
                <li key={rec} className="flex gap-3">
                  <span className="metric text-hivis">{index + 1}</span>
                  <span className="text-concrete">{rec}</span>
                </li>
              ))}
            </ol>
          ) : (
            <Empty>Nothing to action — the site is clear.</Empty>
          )}
        </Panel>
      </div>
    </div>
  )
}
