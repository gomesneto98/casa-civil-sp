import { NavLink } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: '🏠' },
  { to: '/alesp', label: 'ALESP', icon: '🏛️' },
  { to: '/secretarias', label: 'Secretarias', icon: '📁' },
  { to: '/prefeitos', label: 'Prefeitos', icon: '🏙️' },
  { to: '/programas', label: 'Programas', icon: '📋' },
  { to: '/metas', label: 'Programa de Metas', icon: '🎯' },
  { to: '/objetivos', label: 'Dim. Objetivos', icon: '📊' },
]

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
      {/* Logo */}
      <div style={{ padding: '20px 16px 16px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
          <div style={{
            width: 32, height: 32,
            background: 'linear-gradient(135deg, #58a6ff 0%, #1f6feb 100%)',
            borderRadius: 8, display: 'flex', alignItems: 'center',
            justifyContent: 'center', fontSize: 16, flexShrink: 0,
          }}>
            🏛
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text)', lineHeight: 1.2 }}>
              CIG
            </div>
            <div style={{ fontSize: 11, color: 'var(--muted)', lineHeight: 1.2 }}>
              Centro Integrado de Governo
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '12px 8px', overflowY: 'auto' }}>
        {NAV_ITEMS.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            onClick={onClose}
            style={({ isActive }) => ({
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '10px 10px', borderRadius: 6, marginBottom: 2,
              textDecoration: 'none', fontSize: 13,
              fontWeight: isActive ? 600 : 400,
              color: isActive ? 'var(--accent)' : 'var(--muted)',
              background: isActive ? 'rgba(88,166,255,0.1)' : 'transparent',
              transition: 'all 0.15s',
            })}
          >
            <span style={{ fontSize: 17, lineHeight: 1 }}>{icon}</span>
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div style={{ padding: '12px 16px', borderTop: '1px solid var(--border)', fontSize: 11, color: 'var(--muted)' }}>
        <div>Estado de São Paulo</div>
        <div style={{ marginTop: 2, color: '#444d56' }}>v2.0.0 — {new Date().getFullYear()}</div>
      </div>
    </aside>
  )
}
