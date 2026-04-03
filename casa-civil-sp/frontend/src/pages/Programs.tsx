export default function Programs() {
  return (
    <div>
      <div className="page-title">Programas de Governo</div>
      <div className="page-subtitle">Programas e iniciativas estratégicas do Estado de São Paulo</div>

      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', minHeight: 400, textAlign: 'center',
        padding: 40,
      }}>
        <div style={{ fontSize: 64, marginBottom: 24 }}>🚧</div>
        <div style={{
          fontSize: 22, fontWeight: 700, color: 'var(--text)', marginBottom: 12,
        }}>
          Em Construção
        </div>
        <div style={{ fontSize: 14, color: 'var(--muted)', maxWidth: 420, lineHeight: 1.7 }}>
          O módulo de <strong style={{ color: 'var(--text)' }}>Programas de Governo</strong> está
          sendo desenvolvido e estará disponível em breve com dados sobre todos os programas
          estratégicos do Estado de São Paulo.
        </div>

        <div style={{
          marginTop: 32, display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))',
          gap: 12, width: '100%', maxWidth: 600,
        }}>
          {[
            { icon: '🎓', label: 'Educação' },
            { icon: '🏥', label: 'Saúde' },
            { icon: '🏠', label: 'Habitação' },
            { icon: '🚇', label: 'Infraestrutura' },
            { icon: '🌿', label: 'Meio Ambiente' },
            { icon: '🤝', label: 'Social' },
          ].map(({ icon, label }) => (
            <div key={label} className="card" style={{ opacity: 0.4, pointerEvents: 'none' }}>
              <div style={{ fontSize: 28, marginBottom: 8 }}>{icon}</div>
              <div style={{ fontSize: 13, fontWeight: 600 }}>{label}</div>
              <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 4 }}>Em breve</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
