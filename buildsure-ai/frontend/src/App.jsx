import { useCallback, useEffect, useState } from 'react'
import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { ErrorState, Loading } from './components/Primitives'
import { api } from './lib/api'
import CommandCentre from './pages/CommandCentre'
import Compliance from './pages/Compliance'
import Insurance from './pages/Insurance'
import Projects from './pages/Projects'
import Reports from './pages/Reports'
import Safety from './pages/Safety'
import SiteRisk from './pages/SiteRisk'

export default function App() {
  const [projects, setProjects] = useState([])
  const [projectId, setProjectId] = useState(null)
  const [error, setError] = useState(null)
  const [health, setHealth] = useState(false)
  const [running, setRunning] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)
  const [live, setLive] = useState(false)

  const load = useCallback(async () => {
    try {
      await api.health()
      setHealth(true)
      const list = await api.projects()
      setProjects(list)
      setProjectId((current) => current ?? list[0]?.project_id ?? null)
      setError(null)
    } catch (err) {
      setHealth(false)
      setError(err)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  // Live mode: poll the dashboards so streamed site events appear without a reload.
  useEffect(() => {
    if (!live) return undefined
    const timer = setInterval(() => setRefreshKey((key) => key + 1), 10000)
    return () => clearInterval(timer)
  }, [live])

  const runNetwork = async () => {
    if (!projectId) return
    setRunning(true)
    try {
      await api.runNetwork(projectId)
      setRefreshKey((key) => key + 1)
      await load()
    } catch (err) {
      setError(err)
    } finally {
      setRunning(false)
    }
  }

  if (error && !projects.length) return <ErrorState error={error} onRetry={load} />
  if (!projects.length) return <Loading label="Connecting to the risk engine" />

  const pageProps = { projectId, refreshKey }

  return (
    <Layout
      projects={projects}
      projectId={projectId}
      onProjectChange={setProjectId}
      onRunNetwork={runNetwork}
      running={running}
      live={live}
      onToggleLive={() => setLive((value) => !value)}
      health={health}
    >
      <Routes>
        <Route path="/" element={<CommandCentre {...pageProps} />} />
        <Route path="/site-risk" element={<SiteRisk {...pageProps} />} />
        <Route path="/safety" element={<Safety {...pageProps} />} />
        <Route path="/compliance" element={<Compliance {...pageProps} />} />
        <Route path="/insurance" element={<Insurance {...pageProps} />} />
        <Route path="/reports" element={<Reports {...pageProps} />} />
        <Route path="/projects" element={<Projects {...pageProps} />} />
      </Routes>
    </Layout>
  )
}
