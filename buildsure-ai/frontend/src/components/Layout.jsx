import { NavLink } from 'react-router-dom'

const NAV = [
  { to: '/', label: 'Command centre', hint: 'Milestone 4' },
  { to: '/site-risk', label: 'Site risk', hint: 'Milestone 1' },
  { to: '/safety', label: 'Safety', hint: 'Milestone 2' },
  { to: '/compliance', label: 'Compliance', hint: 'Milestone 3' },
  { to: '/insurance', label: 'Insurance', hint: 'Milestone 3' },
  { to: '/reports', label: 'Reports & alerts', hint: 'Milestone 4' },
  { to: '/projects', label: 'Projects', hint: 'Site register' },
]

export default function Layout({ children, projects, projectId, onProjectChange, onRunNetwork, running, health, live, onToggleLive }) {
  const project = projects.find((p) => String(p.project_id) === String(projectId))

  return (
    <div className="min-h-screen">
      <div className="hazard-tape h-1.5 w-full" />
      <div className="mx-auto flex max-w-[1500px] flex-col lg:flex-row">
        <aside className="border-b border-site-500/60 bg-site-900 px-4 py-4 lg:min-h-[calc(100vh-6px)] lg:w-60 lg:border-b-0 lg:border-r">
          <div className="flex items-center gap-2">
            <span className="grid h-8 w-8 place-items-center bg-hivis font-display text-lg font-bold text-site-900">B</span>
            <div>
              <p className="font-display text-xl font-semibold leading-none">BuildSure AI</p>
              <p className="text-[11px] text-steel">Construction risk intelligence</p>
            </div>
          </div>

          <nav className="mt-6 flex flex-wrap gap-1 lg:flex-col">
            {NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `flex items-baseline justify-between border-l-2 px-3 py-2 text-sm transition-colors ${
                    isActive
                      ? 'border-hivis bg-site-700 text-concrete'
                      : 'border-transparent text-steel hover:bg-site-800 hover:text-concrete'
                  }`
                }
              >
                <span className="font-display text-base">{item.label}</span>
                <span className="ml-3 text-[10px] text-steel/70">{item.hint}</span>
              </NavLink>
            ))}
          </nav>

          <div className="mt-6 hidden lg:block">
            <p className="text-xs text-steel">Agent network</p>
            <ul className="mt-2 space-y-1 text-xs text-steel">
              {['Site risk', 'Safety', 'Compliance', 'Insurance', 'Reporting'].map((agent) => (
                <li key={agent} className="flex items-center gap-2">
                  <span className={`h-1.5 w-1.5 ${health ? 'bg-clear' : 'bg-hazard'}`} />
                  {agent} agent
                </li>
              ))}
            </ul>
            <p className="mt-3 text-[11px] text-steel/70">
              {health ? 'Engine online' : 'Engine unreachable'}
            </p>
          </div>
        </aside>

        <main className="flex-1 px-4 py-5 lg:px-7">
          <header className="mb-5 flex flex-wrap items-end justify-between gap-3 border-b border-site-500/60 pb-4">
            <div>
              <h1 className="font-display text-3xl font-semibold leading-none">
                {project ? project.project_name : 'Select a project'}
              </h1>
              <p className="mt-1 text-sm text-steel">
                {project ? `${project.location} · ${project.contractor} · ${project.workers_on_site} workers on site` : 'No project selected'}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={projectId ?? ''}
                onChange={(event) => onProjectChange(event.target.value)}
                className="border border-site-500 bg-site-700 px-3 py-2 font-display text-sm text-concrete"
              >
                {projects.map((p) => (
                  <option key={p.project_id} value={p.project_id}>
                    {p.project_name}
                  </option>
                ))}
              </select>
              <button
                onClick={onToggleLive}
                className={`flex items-center gap-2 border px-3 py-2 font-display text-sm ${
                  live ? 'border-hivis text-hivis' : 'border-site-500 text-steel hover:text-concrete'
                }`}
              >
                <span className={`h-1.5 w-1.5 ${live ? 'animate-pulse bg-hivis' : 'bg-steel'}`} />
                {live ? 'Live monitoring' : 'Go live'}
              </button>
              <button
                onClick={onRunNetwork}
                disabled={running}
                className="bg-hivis px-3 py-2 font-display text-sm font-semibold text-site-900 disabled:opacity-50"
              >
                {running ? 'Agents running…' : 'Run agent network'}
              </button>
            </div>
          </header>
          {children}
        </main>
      </div>
    </div>
  )
}
