import { useEffect, useState, useMemo } from 'react'
import axios from 'axios'

interface GoalGroup {
  id: number
  number: number
  name: string
  pillar: string
}

interface Secretariat {
  id: number
  name: string
  acronym: string
  emoji?: string
}

interface Meta {
  id: number
  code: string
  description: string
  goal_group_id: number
  goal_group: GoalGroup
  secretariat_id: number | null
  secretariat: Secretariat | null
  priority: string
  status: string
  flag_100_dias: boolean
  flag_estadao: boolean
  flag_folha: boolean
  flag_interior: boolean
  flag_capital: boolean
  flag_infraestrutura: boolean
  planned_value: number | null
  actual_value: number | null
  unit: string | null
  planned_date: string | null
  progress_pct: number | null
}

interface Summary {
  total: number
  by_status: Record<string, number>
  by_pillar: Record<string, number>
  by_priority: Record<string, number>
}

const PILLARS = [
  'Dignidade e Comprometimento',
  'Desenvolvimento e Técnica',
  'Diálogo e Inovação',
]

const PILLAR_COLORS: Record<string, string> = {
  'Dignidade e Comprometimento': '#e74c3c',
  'Desenvolvimento e Técnica': '#3498db',
  'Diálogo e Inovação': '#2ecc71',
}

const PILLAR_EMOJI: Record<string, string> = {
  'Dignidade e Comprometimento': '🤲',
  'Desenvolvimento e Técnica': '⚙️',
  'Diálogo e Inovação': '💡',
}

const STATUS_COLORS: Record<string, string> = {
  'Em andamento': '#3498db',
  'Em alerta': '#e67e22',
  'Atrasado': '#e74c3c',
  'Alcançado': '#2ecc71',
  'Evento a confirmar': '#9b59b6',
  'Não iniciado': '#8b949e',
  'Não alcançado': '#c0392b',
}

const PRIORITY_COLORS: Record<string, string> = {
  A: '#e74c3c',
  B: '#e67e22',
  C: '#3498db',
}

function ProgressBar({ pct, status }: { pct: number; status: string }) {
  const color = STATUS_COLORS[status] ?? '#8b949e'
  const capped = Math.min(pct, 100)
  return (
    <div style={{ background: 'var(--bg3)', borderRadius: 4, height: 6, width: '100%', overflow: 'hidden' }}>
      <div style={{ width: `${capped}%`, height: '100%', background: color, borderRadius: 4, transition: 'width 0.4s' }} />
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const color = STATUS_COLORS[status] ?? '#8b949e'
  return (
    <span style={{
      background: `${color}22`, color, border: `1px solid ${color}44`,
      borderRadius: 4, padding: '2px 8px', fontSize: 11, fontWeight: 600, whiteSpace: 'nowrap',
    }}>{status}</span>
  )
}

function PriorityBadge({ priority }: { priority: string }) {
  const color = PRIORITY_COLORS[priority] ?? '#8b949e'
  return (
    <span title={`Prioridade ${priority}`} style={{
      background: color, color: '#fff',
      borderRadius: '50%', width: 20, height: 20,
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      fontSize: 11, fontWeight: 700, flexShrink: 0,
    }}>{priority}</span>
  )
}

function FlagChip({ label, active }: { label: string; active: boolean }) {
  if (!active) return null
  return (
    <span style={{
      background: 'var(--bg3)', color: 'var(--muted)',
      border: '1px solid var(--border)', borderRadius: 4,
      padding: '1px 6px', fontSize: 10,
    }}>{label}</span>
  )
}

function KPIStrip({ summary }: { summary: Summary }) {
  const statusOrder = ['Em andamento', 'Em alerta', 'Atrasado', 'Alcançado', 'Evento a confirmar']
  return (
    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
      {statusOrder.map(s => (
        <div key={s} style={{
          background: 'var(--bg2)', border: `1px solid ${STATUS_COLORS[s]}44`,
          borderLeft: `3px solid ${STATUS_COLORS[s]}`,
          borderRadius: 8, padding: '10px 16px', minWidth: 130,
        }}>
          <div style={{ fontSize: 22, fontWeight: 700, color: STATUS_COLORS[s] }}>
            {summary.by_status[s] ?? 0}
          </div>
          <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 2 }}>{s}</div>
        </div>
      ))}
    </div>
  )
}

function MetaCard({ meta, onClick }: { meta: Meta; onClick: () => void }) {
  const pct = meta.progress_pct ?? 0
  return (
    <div
      onClick={onClick}
      className="card"
      style={{ cursor: 'pointer', padding: 16, display: 'flex', flexDirection: 'column', gap: 10 }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
        <PriorityBadge priority={meta.priority} />
        <span style={{ fontSize: 11, color: 'var(--muted)', fontFamily: 'monospace', paddingTop: 2 }}>
          {meta.code}
        </span>
        <div style={{ marginLeft: 'auto' }}>
          <StatusBadge status={meta.status} />
        </div>
      </div>

      {/* Description */}
      <p style={{ fontSize: 13, lineHeight: 1.4, margin: 0, color: 'var(--fg)' }}>
        {meta.description}
      </p>

      {/* Progress */}
      {meta.planned_value != null && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--muted)' }}>
            <span>
              {meta.actual_value?.toLocaleString('pt-BR')} / {meta.planned_value?.toLocaleString('pt-BR')} {meta.unit}
            </span>
            <span style={{ fontWeight: 700, color: STATUS_COLORS[meta.status] ?? 'var(--fg)' }}>
              {pct.toFixed(0)}%
            </span>
          </div>
          <ProgressBar pct={pct} status={meta.status} />
        </div>
      )}

      {/* Footer */}
      <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', alignItems: 'center' }}>
        {meta.secretariat && (
          <span style={{ fontSize: 10, color: 'var(--muted)', background: 'var(--bg3)', borderRadius: 4, padding: '2px 6px' }}>
            {meta.secretariat.acronym}
          </span>
        )}
        {meta.planned_date && (
          <span style={{ fontSize: 10, color: 'var(--muted)' }}>📅 {meta.planned_date}</span>
        )}
        <FlagChip label="100 dias" active={meta.flag_100_dias} />
        <FlagChip label="Estadão" active={meta.flag_estadao} />
        <FlagChip label="Folha" active={meta.flag_folha} />
        <FlagChip label="Interior" active={meta.flag_interior} />
      </div>
    </div>
  )
}

function MetaModal({ meta, onClose }: { meta: Meta; onClose: () => void }) {
  const pct = meta.progress_pct ?? 0
  const color = STATUS_COLORS[meta.status] ?? '#8b949e'
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()} style={{ maxWidth: 560 }}>
        <div className="modal-header">
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <PriorityBadge priority={meta.priority} />
            <div>
              <div style={{ fontSize: 12, color: 'var(--muted)', fontFamily: 'monospace' }}>Meta {meta.code}</div>
              <div style={{ fontWeight: 700, fontSize: 15, marginTop: 2 }}>{meta.description}</div>
            </div>
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* status + pillar */}
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <StatusBadge status={meta.status} />
            <span style={{
              background: `${PILLAR_COLORS[meta.goal_group.pillar] ?? '#8b949e'}22`,
              color: PILLAR_COLORS[meta.goal_group.pillar] ?? '#8b949e',
              border: `1px solid ${PILLAR_COLORS[meta.goal_group.pillar] ?? '#8b949e'}44`,
              borderRadius: 4, padding: '2px 8px', fontSize: 11,
            }}>
              {PILLAR_EMOJI[meta.goal_group.pillar]} {meta.goal_group.pillar}
            </span>
          </div>

          {/* Objetivo */}
          <div className="info-row">
            <span className="info-label">Objetivo</span>
            <span className="info-value">{meta.goal_group.number}. {meta.goal_group.name}</span>
          </div>

          {/* Secretaria */}
          {meta.secretariat && (
            <div className="info-row">
              <span className="info-label">Secretaria</span>
              <span className="info-value">{meta.secretariat.emoji} {meta.secretariat.name}</span>
            </div>
          )}

          {/* Execução */}
          {meta.planned_value != null && (
            <div style={{ background: 'var(--bg3)', borderRadius: 8, padding: 14 }}>
              <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 8, fontWeight: 600 }}>EXECUÇÃO</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginBottom: 12 }}>
                <div>
                  <div style={{ fontSize: 11, color: 'var(--muted)' }}>Planejado</div>
                  <div style={{ fontWeight: 700, fontSize: 16 }}>
                    {meta.planned_value.toLocaleString('pt-BR')}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--muted)' }}>{meta.unit}</div>
                </div>
                <div>
                  <div style={{ fontSize: 11, color: 'var(--muted)' }}>Realizado</div>
                  <div style={{ fontWeight: 700, fontSize: 16, color }}>
                    {meta.actual_value?.toLocaleString('pt-BR') ?? '—'}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--muted)' }}>{meta.unit}</div>
                </div>
                <div>
                  <div style={{ fontSize: 11, color: 'var(--muted)' }}>Progresso</div>
                  <div style={{ fontWeight: 700, fontSize: 16, color }}>{pct.toFixed(1)}%</div>
                </div>
              </div>
              <ProgressBar pct={pct} status={meta.status} />
            </div>
          )}

          {/* prazo e flags */}
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            {meta.planned_date && (
              <div className="info-row" style={{ margin: 0 }}>
                <span className="info-label">Prazo</span>
                <span className="info-value">📅 {meta.planned_date}</span>
              </div>
            )}
            <div className="info-row" style={{ margin: 0 }}>
              <span className="info-label">Prioridade</span>
              <PriorityBadge priority={meta.priority} />
            </div>
          </div>

          {/* Visões */}
          <div>
            <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 6, fontWeight: 600 }}>VISÕES</div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {meta.flag_100_dias && <span style={{ background: '#e74c3c22', color: '#e74c3c', border: '1px solid #e74c3c44', borderRadius: 4, padding: '2px 8px', fontSize: 11 }}>⚡ Primeiros 100 dias</span>}
              {meta.flag_estadao && <span style={{ background: '#3498db22', color: '#3498db', border: '1px solid #3498db44', borderRadius: 4, padding: '2px 8px', fontSize: 11 }}>📰 Estadão</span>}
              {meta.flag_folha && <span style={{ background: '#2ecc7122', color: '#2ecc71', border: '1px solid #2ecc7144', borderRadius: 4, padding: '2px 8px', fontSize: 11 }}>📰 Folha</span>}
              {meta.flag_interior && <span style={{ background: '#e67e2222', color: '#e67e22', border: '1px solid #e67e2244', borderRadius: 4, padding: '2px 8px', fontSize: 11 }}>🗺️ Interior</span>}
              {meta.flag_capital && <span style={{ background: '#9b59b622', color: '#9b59b6', border: '1px solid #9b59b644', borderRadius: 4, padding: '2px 8px', fontSize: 11 }}>🏙️ Capital</span>}
              {meta.flag_infraestrutura && <span style={{ background: '#f39c1222', color: '#f39c12', border: '1px solid #f39c1244', borderRadius: 4, padding: '2px 8px', fontSize: 11 }}>🏗️ Infraestrutura</span>}
              {!meta.flag_100_dias && !meta.flag_estadao && !meta.flag_folha && !meta.flag_interior && !meta.flag_capital && !meta.flag_infraestrutura && (
                <span style={{ color: 'var(--muted)', fontSize: 12 }}>Nenhuma visão especial</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Metas() {
  const [metas, setMetas] = useState<Meta[]>([])
  const [summary, setSummary] = useState<Summary | null>(null)
  const [groups, setGroups] = useState<GoalGroup[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<Meta | null>(null)

  // Filters
  const [pillar, setPillar] = useState<string>('Todos')
  const [groupId, setGroupId] = useState<number | null>(null)
  const [priority, setPriority] = useState<string>('Todas')
  const [status, setStatus] = useState<string>('Todos')
  const [search, setSearch] = useState('')
  const [viewMode, setViewMode] = useState<'cards' | 'table'>('cards')

  useEffect(() => {
    Promise.all([
      axios.get<Meta[]>('/api/metas'),
      axios.get<Summary>('/api/metas/summary'),
      axios.get<GoalGroup[]>('/api/metas/groups'),
    ]).then(([m, s, g]) => {
      setMetas(m.data)
      setSummary(s.data)
      setGroups(g.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    return metas.filter(m => {
      if (pillar !== 'Todos' && m.goal_group.pillar !== pillar) return false
      if (groupId && m.goal_group_id !== groupId) return false
      if (priority !== 'Todas' && m.priority !== priority) return false
      if (status !== 'Todos' && m.status !== status) return false
      if (search && !m.description.toLowerCase().includes(search.toLowerCase()) && !m.code.includes(search)) return false
      return true
    })
  }, [metas, pillar, groupId, priority, status, search])

  // Group by pillar for grouped view
  const byPillar = useMemo(() => {
    const result: Record<string, { groups: Record<number, { group: GoalGroup; metas: Meta[] }> }> = {}
    for (const pillarName of PILLARS) {
      result[pillarName] = { groups: {} }
    }
    for (const m of filtered) {
      const p = m.goal_group.pillar
      if (!result[p]) result[p] = { groups: {} }
      if (!result[p].groups[m.goal_group.id]) {
        result[p].groups[m.goal_group.id] = { group: m.goal_group, metas: [] }
      }
      result[p].groups[m.goal_group.id].metas.push(m)
    }
    return result
  }, [filtered])

  if (loading) return <div style={{ padding: 32, color: 'var(--muted)' }}>Carregando programa de metas…</div>

  return (
    <div style={{ padding: '24px 28px' }}>
      {/* Title */}
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>Programa de Metas — SP 2023-2026</h1>
        <p style={{ color: 'var(--muted)', fontSize: 13, margin: '4px 0 0' }}>
          {summary?.total ?? 0} metas · Governo Tarcísio de Freitas · Monitoramento quadrimestral
        </p>
      </div>

      {/* KPI Strip */}
      {summary && <KPIStrip summary={summary} />}

      {/* Pillar tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
        {['Todos', ...PILLARS].map(p => (
          <button
            key={p}
            onClick={() => { setPillar(p); setGroupId(null) }}
            style={{
              padding: '6px 14px', borderRadius: 6, border: '1px solid',
              borderColor: pillar === p ? (PILLAR_COLORS[p] ?? 'var(--accent)') : 'var(--border)',
              background: pillar === p ? `${PILLAR_COLORS[p] ?? 'var(--accent)'}22` : 'transparent',
              color: pillar === p ? (PILLAR_COLORS[p] ?? 'var(--accent)') : 'var(--muted)',
              cursor: 'pointer', fontSize: 12, fontWeight: 600,
            }}
          >
            {p === 'Todos' ? '🌐 Todos' : `${PILLAR_EMOJI[p]} ${p}`}
          </button>
        ))}
      </div>

      {/* Filters row */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Buscar meta..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{
            flex: '1 1 200px', maxWidth: 280, padding: '7px 12px',
            background: 'var(--bg2)', border: '1px solid var(--border)',
            borderRadius: 6, color: 'var(--fg)', fontSize: 13,
          }}
        />

        <select
          value={groupId ?? ''}
          onChange={e => setGroupId(e.target.value ? Number(e.target.value) : null)}
          style={{ padding: '7px 10px', background: 'var(--bg2)', border: '1px solid var(--border)', borderRadius: 6, color: 'var(--fg)', fontSize: 12 }}
        >
          <option value="">Todos os objetivos</option>
          {groups
            .filter(g => pillar === 'Todos' || g.pillar === pillar)
            .map(g => (
              <option key={g.id} value={g.id}>{g.number}. {g.name.substring(0, 50)}…</option>
            ))}
        </select>

        <select
          value={status}
          onChange={e => setStatus(e.target.value)}
          style={{ padding: '7px 10px', background: 'var(--bg2)', border: '1px solid var(--border)', borderRadius: 6, color: 'var(--fg)', fontSize: 12 }}
        >
          <option value="Todos">Todos os status</option>
          {Object.keys(STATUS_COLORS).map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>

        <select
          value={priority}
          onChange={e => setPriority(e.target.value)}
          style={{ padding: '7px 10px', background: 'var(--bg2)', border: '1px solid var(--border)', borderRadius: 6, color: 'var(--fg)', fontSize: 12 }}
        >
          <option value="Todas">Prioridade: Todas</option>
          <option value="A">Prioridade A</option>
          <option value="B">Prioridade B</option>
          <option value="C">Prioridade C</option>
        </select>

        <div style={{ marginLeft: 'auto', display: 'flex', gap: 4 }}>
          {(['cards', 'table'] as const).map(m => (
            <button
              key={m}
              onClick={() => setViewMode(m)}
              style={{
                padding: '6px 10px', borderRadius: 6, border: '1px solid var(--border)',
                background: viewMode === m ? 'var(--accent)' : 'transparent',
                color: viewMode === m ? '#fff' : 'var(--muted)',
                cursor: 'pointer', fontSize: 12,
              }}
            >
              {m === 'cards' ? '⊞' : '☰'}
            </button>
          ))}
        </div>
      </div>

      <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 16 }}>
        {filtered.length} resultado{filtered.length !== 1 ? 's' : ''}
      </div>

      {/* Cards view — grouped by pillar → objetivo */}
      {viewMode === 'cards' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
          {PILLARS.filter(p => pillar === 'Todos' || p === pillar).map(pillarName => {
            const pillarData = byPillar[pillarName]
            const pillarGroups = Object.values(pillarData?.groups ?? {})
            if (pillarGroups.length === 0) return null
            const pc = PILLAR_COLORS[pillarName]
            return (
              <div key={pillarName}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                  <div style={{ width: 4, height: 24, background: pc, borderRadius: 2 }} />
                  <h2 style={{ fontSize: 16, fontWeight: 700, margin: 0, color: pc }}>
                    {PILLAR_EMOJI[pillarName]} {pillarName}
                  </h2>
                  <span style={{ color: 'var(--muted)', fontSize: 12 }}>
                    {pillarGroups.reduce((s, g) => s + g.metas.length, 0)} metas
                  </span>
                </div>

                {pillarGroups.sort((a, b) => a.group.number - b.group.number).map(({ group, metas: gMetas }) => (
                  <div key={group.id} style={{ marginBottom: 20 }}>
                    <div style={{
                      display: 'flex', alignItems: 'center', gap: 8,
                      background: 'var(--bg2)', borderRadius: '8px 8px 0 0',
                      padding: '10px 14px', borderBottom: '1px solid var(--border)',
                    }}>
                      <span style={{
                        background: pc, color: '#fff',
                        borderRadius: 4, padding: '2px 8px', fontSize: 12, fontWeight: 700,
                      }}>{group.number}</span>
                      <span style={{ fontWeight: 600, fontSize: 14 }}>{group.name}</span>
                      <span style={{ marginLeft: 'auto', color: 'var(--muted)', fontSize: 12 }}>
                        {gMetas.length} metas
                      </span>
                    </div>
                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                      gap: 12, background: 'var(--bg2)',
                      borderRadius: '0 0 8px 8px', padding: 12,
                    }}>
                      {gMetas.map(m => (
                        <MetaCard key={m.id} meta={m} onClick={() => setSelected(m)} />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )
          })}
        </div>
      )}

      {/* Table view */}
      {viewMode === 'table' && (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: 'var(--bg2)', textAlign: 'left' }}>
                {['Código', 'Meta', 'Objetivo', 'Secretaria', 'Prior.', 'Status', 'Progresso', 'Prazo'].map(h => (
                  <th key={h} style={{ padding: '10px 12px', color: 'var(--muted)', fontWeight: 600, fontSize: 11, borderBottom: '1px solid var(--border)', whiteSpace: 'nowrap' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((m, i) => (
                <tr
                  key={m.id}
                  onClick={() => setSelected(m)}
                  style={{
                    background: i % 2 === 0 ? 'transparent' : 'var(--bg2)',
                    cursor: 'pointer',
                    transition: 'background 0.15s',
                  }}
                  onMouseEnter={e => (e.currentTarget.style.background = 'var(--bg3)')}
                  onMouseLeave={e => (e.currentTarget.style.background = i % 2 === 0 ? 'transparent' : 'var(--bg2)')}
                >
                  <td style={{ padding: '8px 12px', fontFamily: 'monospace', color: 'var(--muted)', whiteSpace: 'nowrap' }}>{m.code}</td>
                  <td style={{ padding: '8px 12px', maxWidth: 320 }}>
                    <span style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                      {m.description}
                    </span>
                  </td>
                  <td style={{ padding: '8px 12px', color: 'var(--muted)', fontSize: 12, whiteSpace: 'nowrap' }}>
                    {m.goal_group.number}. {m.goal_group.name.substring(0, 30)}…
                  </td>
                  <td style={{ padding: '8px 12px', color: 'var(--muted)', fontSize: 11, whiteSpace: 'nowrap' }}>
                    {m.secretariat?.acronym ?? '—'}
                  </td>
                  <td style={{ padding: '8px 12px', textAlign: 'center' }}>
                    <PriorityBadge priority={m.priority} />
                  </td>
                  <td style={{ padding: '8px 12px', whiteSpace: 'nowrap' }}>
                    <StatusBadge status={m.status} />
                  </td>
                  <td style={{ padding: '8px 12px', minWidth: 100 }}>
                    {m.progress_pct != null ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <ProgressBar pct={m.progress_pct} status={m.status} />
                        <span style={{ fontSize: 11, color: 'var(--muted)', whiteSpace: 'nowrap' }}>
                          {m.progress_pct.toFixed(0)}%
                        </span>
                      </div>
                    ) : '—'}
                  </td>
                  <td style={{ padding: '8px 12px', color: 'var(--muted)', fontSize: 12, whiteSpace: 'nowrap' }}>
                    {m.planned_date ?? '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selected && <MetaModal meta={selected} onClose={() => setSelected(null)} />}
    </div>
  )
}
