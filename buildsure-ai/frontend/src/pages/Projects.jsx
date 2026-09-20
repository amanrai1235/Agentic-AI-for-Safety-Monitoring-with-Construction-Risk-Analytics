import { useState } from 'react'
import { Empty, ErrorState, Loading, Panel } from '../components/Primitives'
import { api } from '../lib/api'
import { useData } from '../lib/useData'
import { day, money } from '../lib/format'

const RISK_TYPES = ['fall hazard', 'equipment risk', 'electrical hazard', 'environmental risk', 'structural risk', 'excavation risk']

export default function Projects({ projectId, refreshKey }) {
  const projects = useData(() => api.projects(), [refreshKey])
  const runs = useData(() => api.agentRuns(projectId), [projectId, refreshKey])
  const [form, setForm] = useState({ risk_type: RISK_TYPES[0], zone: '', description: '', probability: 3, impact: 3 })
  const [status, setStatus] = useState(null)

  if (projects.error) return <ErrorState error={projects.error} onRetry={projects.reload} />

  const submit = async (event) => {
    event.preventDefault()
    try {
      await api.createRisk({ project_id: Number(projectId), ...form, probability: Number(form.probability), impact: Number(form.impact) })
      setStatus('Hazard logged. The Site Risk Agent will pick it up on the next run.')
      setForm({ ...form, zone: '', description: '' })
      projects.reload()
    } catch (err) {
      setStatus(`Could not log the hazard: ${err.message}`)
    }
  }

  return (
    <div className="space-y-5">
      <Panel title="Site register" note="Scores update each time the agent network runs">
        {projects.loading && !projects.data ? (
          <Loading label="Loading projects" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-sm">
              <thead className="text-left text-xs text-steel">
                <tr className="border-b border-site-500/60">
                  <th className="pb-2 font-medium">Project</th>
                  <th className="pb-2 font-medium">Contractor</th>
                  <th className="pb-2 font-medium">Started</th>
                  <th className="pb-2 font-medium">Workers</th>
                  <th className="pb-2 font-medium">Risk</th>
                  <th className="pb-2 font-medium">Safety</th>
                  <th className="pb-2 font-medium">Compliance</th>
                  <th className="pb-2 font-medium">Exposure</th>
                </tr>
              </thead>
              <tbody>
                {projects.data.map((p) => (
                  <tr key={p.project_id} className={`border-b border-site-500/30 ${String(p.project_id) === String(projectId) ? 'bg-site-600/40' : ''}`}>
                    <td className="py-2 pr-3">
                      <p className="text-concrete">{p.project_name}</p>
                      <p className="text-xs text-steel">{p.location}</p>
                    </td>
                    <td className="py-2 pr-3 text-steel">{p.contractor}</td>
                    <td className="py-2 pr-3 text-xs text-steel">{day(p.start_date)}</td>
                    <td className="metric py-2 pr-3 text-steel">{p.workers_on_site}</td>
                    <td className="metric py-2 pr-3 text-concrete">{Math.round(p.risk_score) || '—'}</td>
                    <td className="metric py-2 pr-3 text-steel">{Math.round(p.safety_score) || '—'}</td>
                    <td className="metric py-2 pr-3 text-steel">{Math.round(p.compliance_score) || '—'}</td>
                    <td className="metric py-2 text-steel">{money(p.insurance_exposure)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      <div className="grid gap-5 lg:grid-cols-2">
        <Panel title="Log a hazard" note="Feeds straight into the Site Risk Agent">
          <form onSubmit={submit} className="space-y-3 text-sm">
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block">
                <span className="text-xs text-steel">Hazard type</span>
                <select
                  value={form.risk_type}
                  onChange={(e) => setForm({ ...form, risk_type: e.target.value })}
                  className="mt-1 w-full border border-site-500 bg-site-600 px-2 py-2 capitalize text-concrete"
                >
                  {RISK_TYPES.map((type) => <option key={type} value={type}>{type}</option>)}
                </select>
              </label>
              <label className="block">
                <span className="text-xs text-steel">Zone</span>
                <input
                  value={form.zone}
                  onChange={(e) => setForm({ ...form, zone: e.target.value })}
                  placeholder="Level 14 slab edge"
                  className="mt-1 w-full border border-site-500 bg-site-600 px-2 py-2 text-concrete placeholder:text-steel/60"
                  required
                />
              </label>
            </div>
            <label className="block">
              <span className="text-xs text-steel">What did you see?</span>
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                rows={3}
                className="mt-1 w-full border border-site-500 bg-site-600 px-2 py-2 text-concrete"
                required
              />
            </label>
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block">
                <span className="text-xs text-steel">Probability (1–5)</span>
                <input type="range" min="1" max="5" value={form.probability} onChange={(e) => setForm({ ...form, probability: e.target.value })} className="mt-2 w-full accent-hivis" />
              </label>
              <label className="block">
                <span className="text-xs text-steel">Impact (1–5)</span>
                <input type="range" min="1" max="5" value={form.impact} onChange={(e) => setForm({ ...form, impact: e.target.value })} className="mt-2 w-full accent-hivis" />
              </label>
            </div>
            <div className="flex items-center gap-3">
              <button type="submit" className="bg-hivis px-3 py-2 font-display text-sm font-semibold text-site-900">Log hazard</button>
              <span className="metric text-steel">Exposure {form.probability * form.impact}/25</span>
            </div>
            {status && <p className="text-xs text-hivis">{status}</p>}
          </form>
        </Panel>

        <Panel title="Agent run log" note="Audit trail of every agent execution">
          {runs.data?.length ? (
            <div className="max-h-[320px] overflow-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-site-700 text-left text-xs text-steel">
                  <tr className="border-b border-site-500/60">
                    <th className="pb-2 font-medium">Agent</th>
                    <th className="pb-2 font-medium">Findings</th>
                    <th className="pb-2 font-medium">Score</th>
                    <th className="pb-2 font-medium">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.data.map((run) => (
                    <tr key={run.run_id} className="border-b border-site-500/30">
                      <td className="py-2 pr-3 capitalize text-concrete">{run.agent.replace(/_/g, ' ')}</td>
                      <td className="metric py-2 pr-3 text-steel">{run.findings}</td>
                      <td className="metric py-2 pr-3 text-steel">{run.score}</td>
                      <td className="metric py-2 text-steel">{run.duration_ms} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <Empty>No agent runs recorded yet. Use “Run agent network”.</Empty>
          )}
        </Panel>
      </div>
    </div>
  )
}
