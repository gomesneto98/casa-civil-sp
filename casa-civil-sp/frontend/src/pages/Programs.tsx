import { useEffect, useState } from 'react'
import axios from 'axios'
import { fmt_currency } from '../utils'

interface Secretariat {
  id: number
  name: string
  acronym: string
  secretary_name: string | null
}

interface Program {
  id: number
  name: string
  description: string | null
  secretariat_id: number | null
  secretariat: Secretariat | null
  year_start: number
  year_end: number | null
  total_budget: number
  status: string
}

const STATUS_LABELS: Record<string, string> = {
  ativo: 'Ativo',
  concluido: 'Concluído',
  suspenso: 'Suspenso',
}

export default function Programs() {
  const [programs, setPrograms] = useState<Program[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('Todos')

  useEffect(() => {
    axios.get<Program[]>('/api/programs')
      .then(r => setPrograms(r.data))
      .finally(() => setLoading(false))
  }, [])

  const filtered = statusFilter === 'Todos'
    ? programs
    : programs.filter(p => p.status === statusFilter)

  const totalBudget = filtered.reduce((s, p) => s + p.total_budget, 0)

  return (
    <div>
      <div className="page-title">Programas de Governo</div>
      <div className="page-subtitle">Programas e iniciativas estratégicas do Estado de São Paulo</div>

      {/* Summary bar */}
      <div style={{
        background: 'var(--bg2)', border: '1px solid var(--border)', borderRadius: 8,
        padding: '12px 16px', marginBottom: 20,
        display: 'flex', gap: 32, flexWrap: 'wrap',
      }}>
        <div>
          <span style={{ fontSize: 11, color: 'var(--muted)' }}>Total de Programas</span>
          <div style={{ fontWeight: 700, fontSize: 20 }}>{programs.length}</div>
        </div>
        <div>
          <span style={{ fontSize: 11, color: 'var(--muted)' }}>Orçamento Total</span>
          <div style={{ fontWeight: 700, fontSize: 20, color: 'var(--accent)' }}>{fmt_currency(totalBudget)}</div>
        </div>
        <div>
          <span style={{ fontSize: 11, color: 'var(--muted)' }}>Programas Ativos</span>
          <div style={{ fontWeight: 700, fontSize: 20, color: 'var(--green)' }}>
            {programs.filter(p => p.status === 'ativo').length}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 20 }}>
        {['Todos', 'ativo', 'concluido', 'suspenso'].map(s => (
          <button
            key={s}
            className={`filter-btn ${statusFilter === s ? 'active' : ''}`}
            onClick={() => setStatusFilter(s)}
          >
            {s === 'Todos' ? 'Todos' : STATUS_LABELS[s]}
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="loading-skeleton" style={{ height: 180 }} />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📋</div>
          <div>Nenhum programa encontrado.</div>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
          {filtered.map(prog => (
            <div
              key={prog.id}
              className="card"
              style={{ display: 'flex', flexDirection: 'column', gap: 12 }}
            >
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
                <div style={{ fontWeight: 700, fontSize: 15, lineHeight: 1.3, flex: 1 }}>
                  {prog.name}
                </div>
                <span className={`badge badge-${prog.status}`} style={{ flexShrink: 0 }}>
                  {STATUS_LABELS[prog.status] ?? prog.status}
                </span>
              </div>

              {/* Description */}
              {prog.description && (
                <div style={{
                  fontSize: 12, color: 'var(--muted)', lineHeight: 1.5,
                  display: '-webkit-box', WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical', overflow: 'hidden',
                }}>
                  {prog.description}
                </div>
              )}

              {/* Secretariat */}
              {prog.secretariat && (
                <div style={{
                  display: 'inline-flex', alignItems: 'center', gap: 6,
                  background: 'var(--bg3)', borderRadius: 6, padding: '4px 10px',
                  width: 'fit-content',
                }}>
                  <span style={{ fontSize: 11, color: 'var(--accent)', fontWeight: 600 }}>{prog.secretariat.acronym}</span>
                  <span style={{ fontSize: 11, color: 'var(--muted)' }}>{prog.secretariat.name}</span>
                </div>
              )}

              {/* Footer */}
              <div style={{
                borderTop: '1px solid var(--border)', paddingTop: 10,
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              }}>
                <div>
                  <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 2 }}>Orçamento Total</div>
                  <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--green)' }}>
                    {fmt_currency(prog.total_budget)}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 2 }}>Período</div>
                  <div style={{ fontSize: 13, fontWeight: 500 }}>
                    {prog.year_start}{prog.year_end ? `–${prog.year_end}` : '+'}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
