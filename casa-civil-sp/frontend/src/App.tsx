import { useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Deputies from './pages/Deputies'
import Secretariats from './pages/Secretariats'
import Mayors from './pages/Mayors'
import Programs from './pages/Programs'
import Metas from './pages/Metas'
import Objetivos from './pages/Objetivos'

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <BrowserRouter>
      <div className="main-layout">
        {/* Mobile overlay */}
        {sidebarOpen && (
          <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
        )}

        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="page-content">
          {/* Mobile top bar */}
          <div className="mobile-topbar">
            <button
              className="hamburger-btn"
              onClick={() => setSidebarOpen(true)}
              aria-label="Abrir menu"
            >
              ☰
            </button>
            <span style={{ fontWeight: 700, fontSize: 15 }}>CIG — Centro Integrado de Governo</span>
          </div>

          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/alesp" element={<Deputies />} />
            <Route path="/secretarias" element={<Secretariats />} />
            <Route path="/prefeitos" element={<Mayors />} />
            <Route path="/programas" element={<Programs />} />
            <Route path="/metas" element={<Metas />} />
            <Route path="/objetivos" element={<Objetivos />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
