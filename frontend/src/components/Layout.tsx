import { Link, Outlet } from 'react-router-dom'

export function Layout() {
  return (
    <div className="app-shell">
      <header className="top-bar">
        <div className="brand">
          <h1>Creator Agent Toolbox</h1>
          <p>Workflow review console</p>
        </div>
        <nav className="top-nav">
          <Link to="/">Dashboard</Link>
        </nav>
      </header>
      <main className="content-wrap">
        <Outlet />
      </main>
    </div>
  )
}
