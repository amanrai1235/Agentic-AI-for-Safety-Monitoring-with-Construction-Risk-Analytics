const BASE = import.meta.env.VITE_API_URL ?? ''

async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(`${response.status} ${detail || response.statusText}`)
  }
  if (response.status === 204) return null
  return response.json()
}

export const api = {
  health: () => request('/api/health'),
  projects: () => request('/api/projects'),
  siteRisk: (id) => request(`/api/dashboards/site-risk/${id}`),
  safety: (id) => request(`/api/dashboards/safety/${id}`),
  compliance: (id) => request(`/api/dashboards/compliance/${id}`),
  insurance: (id) => request(`/api/dashboards/insurance/${id}`),
  executive: (id) => request(`/api/dashboards/executive/${id}`),
  portfolio: () => request('/api/dashboards/portfolio'),
  agents: () => request('/api/agents'),
  agentRuns: (id) => request(`/api/agents/runs?project_id=${id}`),
  agentPerformance: (id) => request(`/api/agents/performance?project_id=${id}`),
  runNetwork: (id) => request(`/api/agents/run-network/${id}`, { method: 'POST' }),
  runAgent: (key, id) => request(`/api/agents/${key}/run/${id}`, { method: 'POST' }),
  reports: (id) => request(`/api/reports?project_id=${id}`),
  generateReport: (id, type = 'daily') =>
    request(`/api/reports/generate/${id}?report_type=${type}`, { method: 'POST' }),
  alerts: (id) => request(`/api/alerts?project_id=${id}`),
  acknowledgeAlert: (alertId) => request(`/api/alerts/${alertId}`, { method: 'PATCH' }),
  risks: (id) => request(`/api/risks?project_id=${id}`),
  createRisk: (payload) => request('/api/risks', { method: 'POST', body: JSON.stringify(payload) }),
  updateRisk: (riskId, status) => request(`/api/risks/${riskId}?status=${status}`, { method: 'PATCH' }),
  violations: (id) => request(`/api/ppe-violations?project_id=${id}`),
  resolveViolation: (vid) => request(`/api/ppe-violations/${vid}?resolved=true`, { method: 'PATCH' }),
  incidents: (id) => request(`/api/incidents?project_id=${id}`),
  complianceChecks: (id) => request(`/api/compliance-checks?project_id=${id}`),
  insuranceCases: (id) => request(`/api/insurance-cases?project_id=${id}`),
}
