import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Empty, ErrorState, Kpi, Loading, Meter, Panel, SeverityTag } from '../components/Primitives'
import { api } from '../lib/api'
import { useData } from '../lib/useData'
import { when } from '../lib/format'

export default function Safety({ projectId, refreshKey }) {
  const { data, error, loading, reload } = useData(() => api.safety(projectId), [projectId, refreshKey])

  if (loading && !data) return <Loading label="Safety Agent reviewing PPE detections" />
  if (error) return <ErrorState error={error} onRetry={reload} />

  const m = data.metrics

  const resolve = async (violationId) => {
    await api.resolveViolation(violationId)
    reload()
  }

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Kpi label="PPE compliance rate" value={m.ppe_compliance_rate} unit="%" tone="text-clear" />
        <Kpi label="Open safety violations" value={m.safety_violations} tone="text-caution" sub={`${m.violations_today} today`} />
        <Kpi label="Workers monitored" value={m.workers_monitored} />
        <Kpi label="Safety score" value={m.safety_score} unit="/100" tone="text-hivis" sub={`${m.lost_days} lost worker-days`} />
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <Panel title="Compliance by PPE type" note={data.summary}>
          {m.compliance_by_ppe.map((row) => (
            <Meter key={row.type} label={`${row.type} (${row.violations} violations)`} value={Math.round(row.rate)} />
          ))}
        </Panel>

        <Panel title="Incident trend" note="Recorded incidents over the last 30 days">
          {m.incident_trend?.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={m.incident_trend}>
                <CartesianGrid stroke="#232A34" vertical={false} />
                <XAxis dataKey="day" stroke="#7C8899" fontSize={11} tickLine={false} />
                <YAxis stroke="#7C8899" fontSize={11} allowDecimals={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: '#1A2028', border: '1px solid #313A46', borderRadius: 2, color: '#D5DBE3' }}
                  cursor={{ fill: '#232A34' }}
                />
                <Bar dataKey="incidents" fill="#F5C518" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <Empty>No incidents recorded in the last 30 days.</Empty>
          )}
        </Panel>
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <Panel className="lg:col-span-2" title="Open PPE violations" note="Detected by the vision pipeline, pending sign-off">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[560px] text-sm">
              <thead className="text-left text-xs text-steel">
                <tr className="border-b border-site-500/60">
                  <th className="pb-2 font-medium">Worker</th>
                  <th className="pb-2 font-medium">Missing PPE</th>
                  <th className="pb-2 font-medium">Zone</th>
                  <th className="pb-2 font-medium">Confidence</th>
                  <th className="pb-2 font-medium">Detected</th>
                  <th className="pb-2 font-medium" />
                </tr>
              </thead>
              <tbody>
                {data.open_violations.map((v) => (
                  <tr key={v.violation_id} className="border-b border-site-500/30">
                    <td className="metric py-2 pr-3 text-concrete">{v.worker_id}</td>
                    <td className="py-2 pr-3 capitalize text-concrete">{v.violation_type}</td>
                    <td className="py-2 pr-3 text-steel">{v.zone}</td>
                    <td className="metric py-2 pr-3 text-steel">{Math.round(v.confidence * 100)}%</td>
                    <td className="py-2 pr-3 text-xs text-steel">{when(v.timestamp)}</td>
                    <td className="py-2 text-right">
                      <button onClick={() => resolve(v.violation_id)} className="border border-site-500 px-2 py-1 text-xs text-steel hover:border-clear hover:text-clear">
                        Mark corrected
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!data.open_violations.length && <Empty>Every detection has been corrected on site.</Empty>}
          </div>
        </Panel>

        <Panel title="Safety findings" note="Unsafe behaviour and accident-prone zones">
          {data.findings.length ? (
            <ul className="space-y-3 text-sm">
              {data.findings.map((f) => (
                <li key={f.title} className="border-l-2 border-site-500 pl-3">
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
            <Empty>No safety findings this cycle.</Empty>
          )}
        </Panel>
      </div>
    </div>
  )
}
