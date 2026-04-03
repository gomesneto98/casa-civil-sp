interface KPICardProps {
  title: string
  value: string | number
  subtitle?: string
  color?: string
  icon?: string
}

export default function KPICard({ title, value, subtitle, color = 'var(--accent)', icon }: KPICardProps) {
  return (
    <div className="card" style={{ position: 'relative', overflow: 'hidden' }}>
      {/* Accent bar */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: 3,
        height: '100%',
        background: color,
        borderRadius: '8px 0 0 8px',
      }} />

      <div style={{ paddingLeft: 8 }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 8,
        }}>
          <div style={{ fontSize: 11, color: 'var(--muted)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            {title}
          </div>
          {icon && <span style={{ fontSize: 18 }}>{icon}</span>}
        </div>

        <div style={{
          fontSize: 26,
          fontWeight: 700,
          color: 'var(--text)',
          lineHeight: 1.1,
          marginBottom: 4,
        }}>
          {value}
        </div>

        {subtitle && (
          <div style={{ fontSize: 12, color: 'var(--muted)' }}>
            {subtitle}
          </div>
        )}
      </div>
    </div>
  )
}
