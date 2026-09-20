import { Empty, ErrorState, Kpi, Loading, Meter, Panel, ScoreDial, SeverityTag } from '../components/Primitives'
import { api } from '../lib/api'
import { useData } from '../lib/useData'
import { money, when } from '../lib/format'

const AGENT_LABELS = {
  site_risk_agent: 'Site Risk Agent',
  safety_agent: 'Safety Agent',
  compliance_agent: 'Compliance Agent',
  insurance_agent: 'Insurance Agent',
}

export default function CommandCentre({ projectId, refreshKey }) {
  const exec = useData(() => api.executive(projectId), [projectId, refreshKey])
  const portfolio = useData(() => api.portfolio(), [refreshKey])

  if (exec.loading && !exec.data) return <Loading label="Risk intelligence engine consolidating agent findings" />
  if (exec.error) return <ErrorState error={exec.error} onRetry={exec.reload} />

  const { engine, alerts, incidents_prevented, estimated_cost_avoided, agent_summaries } = exec.data

  const acknowledge = async (alertId) => {
    await api.acknowledgeAlert(alertId)
    exec.reload()
  }

  return (
    <div className="space-y-5">
      <Panel title="Project risk score" note={`${engine.risk_band} · ${engine.total_findings} findings consolidated from five agents`}>
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_2fr]">
          <ScoreDial
            score={engine.project_risk_score}
            caption={`${engine.critical_findings} critical and ${engine.high_findings} high findings open. Forecast: ${engine.predicted_incidents} incidents in the next 30 days if nothing changes.`}
          />
          <div>
            {Object.entries(engine.agent_scores)
              .filter(([name]) => AGENT_LABELS[name])
              .map(([name, score]) => (
                <Meter key={name} label={AGENT_LABELS[name]} value={Math.round(score)} suffix="/100" />
              ))}
          </div>
        </div>
      </Panel>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Kpi label="Incidents prevented" value={incidents_prevented} tone="text-clear" sub="Hazards closed before escalation" />
        <Kpi label="Cost avoided" value={money(estimated_cost_avoided)} tone="text-clear" />
        <Kpi label="Critical findings" value={engine.critical_findings} tone="text-hazard" />
        <Kpi label="Predicted incidents" value={engine.predicted_incidents} tone="text-caution" sub="Next 30 days" />
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <Panel className="lg:col-span-2" title="Recommended actions" note="Ranked by the intelligence engine across every agent">
          {engine.recommendations.length ? (
            <ol className="space-y-3 text-sm">
              {engine.recommendations.map((rec, index) => (
                <li key={rec} className="flex gap-3 border-l-2 border-hivis/40 pl-3">
                  <span className="metric text-hivis">{index + 1}</span>
                  <span className="text-concrete">{rec}</span>
                </li>
              ))}
            </ol>
          ) : (
            <Empty>No open actions. Run the agent network to refresh.</Empty>
          )}

          {engine.patterns.length > 0 && (
            <div className="mt-5 border-t border-site-500/60 pt-4">
              <h3 className="font-display text-base text-concrete">Recurring patterns</h3>
              <ul className="mt-2 space-y-2 text-sm text-steel">
                {engine.patterns.map((pattern) => (
                  <li key={pattern}>{pattern}</li>
                ))}
              </ul>
            </div>
          )}
        </Panel>

        <Panel title="Agent collaboration" note="What each agent reported this cycle">
          <ul className="space-y-3 text-sm">
            {Object.entries(agent_summaries).map(([agent, summary]) => (
              <li key={agent}>
                <p className="font-display text-base text-concrete">{AGENT_LABELS[agent] ?? agent}</p>
                <p className="text-xs text-steel">{summary}</p>
              </li>
            ))}
          </ul>
        </Panel>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <Panel title="Incident escalation" note="Alerts routed to email, SMS and Teams by severity">
          {alerts.length ? (
            <ul className="space-y-3 text-sm">
              {alerts.map((alert) => (
                <li key={alert.alert_id} className="flex items-start justify-between gap-3 border-b border-site-500/30 pb-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <SeverityTag severity={alert.severity} />
                      <span className="text-xs text-steel">{alert.source_agent.replace(/_/g, ' ')} · {when(alert.created_at)}</span>
                    </div>
                    <p className="mt-1 text-concrete">{alert.message}</p>
                  </div>
                  <button onClick={() => acknowledge(alert.alert_id)} className="shrink-0 border border-site-500 px-2 py-1 text-xs text-steel hover:border-hivis hover:text-hivis">
                    Acknowledge
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <Empty>No alerts raised for this project.</Empty>
          )}
        </Panel>

        <Panel title="Portfolio risk" note="Every active site, scored by the same engine">
          {portfolio.data ? (
            <table className="w-full text-sm">
              <thead className="text-left text-xs text-steel">
                <tr className="border-b border-site-500/60">
                  <th className="pb-2 font-medium">Project</th>
                  <th className="pb-2 font-medium">Risk</th>
                  <th className="pb-2 font-medium">PPE</th>
                  <th className="pb-2 font-medium">Exposure</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.data.projects.map((row) => (
                  <tr key={row.project_id} className="border-b border-site-500/30">
                    <td className="py-2 pr-3">
                      <p className="text-concrete">{row.project_name}</p>
                      <p className="text-xs text-steel">{row.location}</p>
                    </td>
                    <td className="metric py-2 pr-3 text-concrete">
                      {row.project_risk_score}
                      <span className="block text-[11px] font-normal text-steel">{row.risk_band}</span>
                    </td>
                    <td className="metric py-2 pr-3 text-steel">{row.ppe_compliance}%</td>
                    <td className="metric py-2 text-steel">{money(row.exposure)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <Loading label="Rolling up the portfolio" />
          )}
        </Panel>
      </div>
    </div>
  )
}
