import { useEffect, useState, useMemo } from 'react'
import axios from 'axios'

// ── Types ───────────────────────────────────────────────

interface GoalGroup {
  id: number
  number: number
  name: string
  pillar: string
}

interface SecretariatOpt {
  id: number
  name: string
  acronym: string
}

interface MetaItem {
  id: number
  code: string
  description: string
  goal_group_id: number
  secretariat_id: number | null
  secretariat: SecretariatOpt | null
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

// ── Constants ───────────────────────────────────────────

const PILLAR_LABELS = [
  'Dignidade e Comprometimento',
  'Desenvolvimento e Técnica',
  'Diálogo e Inovação',
]

const PILLAR_COLORS: Record<string, string> = {
  'Dignidade e Comprometimento': '#f85149',
  'Desenvolvimento e Técnica': '#58a6ff',
  'Diálogo e Inovação': '#3fb950',
}

const STATUS_COLORS: Record<string, string> = {
  'Em andamento': '#58a6ff',
  'Em alerta': '#f0883e',
  'Atrasado': '#f85149',
  'Alcançado': '#3fb950',
  'Evento a confirmar': '#a371f7',
  'Não iniciado': '#8b949e',
  'Não alcançado': '#da3633',
}

const STATUSES = Object.keys(STATUS_COLORS)
const PRIORITIES = ['A', 'B', 'C']
const PRIORITY_COLORS: Record<string, string> = { A: '#f85149', B: '#58a6ff', C: '#8b949e' }

const FLAGS = [
  { key: 'flag_100_dias', label: '100 dias' },
  { key: 'flag_estadao', label: 'Estadão' },
  { key: 'flag_folha', label: 'Folha' },
  { key: 'flag_interior', label: 'Interior' },
  { key: 'flag_capital', label: 'Capital' },
  { key: 'flag_infraestrutura', label: 'Infraestrutura' },
]

// ── Helpers ─────────────────────────────────────────────

function calcProgress(planned: string | number | null, actual: string | number | null): number | null {
  const p = parseFloat(String(planned))
  const a = parseFloat(String(actual))
  if (!p || isNaN(p) || isNaN(a)) return null
  return Math.min(100, Math.round((a / p) * 1000) / 10)
}

// ── Small components ────────────────────────────────────

function Pill({ label, color }: { label: string; color: string }) {
  return (
    <span style={{
      display: 'inline-block', padding: '2px 8px', borderRadius: 10,
      fontSize: 10, fontWeight: 600, whiteSpace: 'nowrap',
      background: `${color}22`, color, border: `1px solid ${color}44`,
    }}>{label}</span>
  )
}

function MiniProgress({ pct }: { pct: number | null }) {
  const v = pct ?? 0
  const color = v >= 100 ? '#3fb950' : v >= 60 ? '#58a6ff' : v >= 30 ? '#f0883e' : '#f85149'
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
      <div style={{ flex: 1, height: 4, background: 'var(--bg3)', borderRadius: 4, minWidth: 50 }}>
        <div style={{ width: `${Math.min(v, 100)}%`, height: '100%', background: color, borderRadius: 4 }} />
      </div>
      <span style={{ fontSize: 11, color: 'var(--muted)', minWidth: 36, textAlign: 'right' }}>
        {v.toFixed(1)}%
      </span>
    </div>
  )
}

// ── Btn helpers ─────────────────────────────────────────

const btnBase: React.CSSProperties = {
  border: 'none', borderRadius: 6, cursor: 'pointer', fontFamily: 'var(--font)',
  fontWeight: 600, fontSize: 12, padding: '5px 12px',
}
const btnPrimary: React.CSSProperties = { ...btnBase, background: 'var(--accent)', color: '#fff' }
const btnGhost: React.CSSProperties = {
  ...btnBase, background: 'transparent', color: 'var(--muted)',
  border: '1px solid var(--border)',
}
const btnDanger: React.CSSProperties = {
  ...btnBase, background: 'rgba(248,81,73,0.12)', color: '#f85149',
}

// ── EditGroupModal ──────────────────────────────────────

function EditGroupModal({
  group, onClose, onSaved,
}: { group: GoalGroup; onClose: () => void; onSaved: (g: GoalGroup) => void }) {
  const [name, setName] = useState(group.name)
  const [pillar, setPillar] = useState(group.pillar)
  const [saving, setSaving] = useState(false)

  async function save() {
    setSaving(true)
    try {
      const { data } = await axios.put<GoalGroup>(`/api/metas/groups/${group.id}`, { name, pillar })
      onSaved(data)
      onClose()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" style={{ maxWidth: 480 }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span style={{ fontWeight: 700, fontSize: 15 }}>Editar Objetivo {group.number}</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <div style={labelStyle}>Nome</div>
            <textarea
              className="search-input"
              style={{ width: '100%', resize: 'vertical', marginTop: 6 }}
              rows={3} value={name}
              onChange={e => setName(e.target.value)}
            />
          </div>
          <div>
            <div style={labelStyle}>Eixo</div>
            <select
              className="search-input"
              style={{ width: '100%', marginTop: 6 }}
              value={pillar}
              onChange={e => setPillar(e.target.value)}
            >
              {PILLAR_LABELS.map(p => <option key={p}>{p}</option>)}
            </select>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 4 }}>
            <button style={btnGhost} onClick={onClose}>Cancelar</button>
            <button style={btnPrimary} onClick={save} disabled={saving}>
              {saving ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── MetaFormModal ───────────────────────────────────────

type MetaForm = {
  code: string; description: string; goal_group_id: number; secretariat_id: number | null
  priority: string; status: string; planned_value: string; actual_value: string
  unit: string; planned_date: string
  flag_100_dias: boolean; flag_estadao: boolean; flag_folha: boolean
  flag_interior: boolean; flag_capital: boolean; flag_infraestrutura: boolean
}

const EMPTY_FORM = (groupId: number): MetaForm => ({
  code: '', description: '', goal_group_id: groupId, secretariat_id: null,
  priority: 'B', status: 'Em andamento', planned_value: '', actual_value: '',
  unit: '', planned_date: '',
  flag_100_dias: false, flag_estadao: false, flag_folha: false,
  flag_interior: false, flag_capital: false, flag_infraestrutura: false,
})

function metaToForm(m: MetaItem): MetaForm {
  return {
    code: m.code, description: m.description, goal_group_id: m.goal_group_id,
    secretariat_id: m.secretariat_id, priority: m.priority, status: m.status,
    planned_value: m.planned_value?.toString() ?? '', actual_value: m.actual_value?.toString() ?? '',
    unit: m.unit ?? '', planned_date: m.planned_date ?? '',
    flag_100_dias: m.flag_100_dias, flag_estadao: m.flag_estadao, flag_folha: m.flag_folha,
    flag_interior: m.flag_interior, flag_capital: m.flag_capital, flag_infraestrutura: m.flag_infraestrutura,
  }
}

function MetaFormModal({
  meta, groupId, groups, secretariats, onClose, onSaved,
}: {
  meta: MetaItem | null; groupId: number; groups: GoalGroup[]
  secretariats: SecretariatOpt[]; onClose: () => void; onSaved: (m: MetaItem) => void
}) {
  const [form, setForm] = useState<MetaForm>(() => meta ? metaToForm(meta) : EMPTY_FORM(groupId))
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  function set<K extends keyof MetaForm>(key: K, val: MetaForm[K]) {
    setForm(f => ({ ...f, [key]: val }))
  }

  async function save() {
    if (!form.description.trim()) { setError('Descrição é obrigatória'); return }
    if (!form.code.trim()) { setError('Código é obrigatório'); return }
    setSaving(true); setError('')
    const planned = parseFloat(form.planned_value) || null
    const actual = parseFloat(form.actual_value) || null
    const payload = {
      ...form,
      planned_value: planned, actual_value: actual,
      unit: form.unit || null, planned_date: form.planned_date || null,
      secretariat_id: form.secretariat_id || null,
      progress_pct: calcProgress(planned, actual),
      goal_group_id: form.goal_group_id,
    }
    try {
      const { data } = meta
        ? await axios.put<MetaItem>(`/api/metas/${meta.id}`, payload)
        : await axios.post<MetaItem>('/api/metas', payload)
      onSaved(data)
      onClose()
    } catch {
      setError('Erro ao salvar. Verifique os dados.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-box"
        style={{ maxWidth: 660, maxHeight: '92vh', overflowY: 'auto' }}
        onClick={e => e.stopPropagation()}
      >
        <div className="modal-header">
          <span style={{ fontWeight: 700, fontSize: 15 }}>
            {meta ? `Editar ${meta.code}` : 'Nova Meta'}
          </span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {/* Código + Objetivo */}
          <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: 12 }}>
            <div>
              <div style={labelStyle}>Código *</div>
              <input className="search-input" style={{ width: '100%', marginTop: 6 }}
                value={form.code} onChange={e => set('code', e.target.value)}
                placeholder="Ex: 1.5" readOnly={!!meta} />
            </div>
            <div>
              <div style={labelStyle}>Objetivo</div>
              <select className="search-input" style={{ width: '100%', marginTop: 6 }}
                value={form.goal_group_id}
                onChange={e => set('goal_group_id', parseInt(e.target.value))}>
                {groups.map(g => (
                  <option key={g.id} value={g.id}>{g.number}. {g.name.slice(0, 55)}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Descrição */}
          <div>
            <div style={labelStyle}>Descrição *</div>
            <textarea className="search-input"
              style={{ width: '100%', marginTop: 6, resize: 'vertical' }}
              rows={3} value={form.description}
              onChange={e => set('description', e.target.value)} />
          </div>

          {/* Status + Prioridade + Secretaria */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 90px 1fr', gap: 12 }}>
            <div>
              <div style={labelStyle}>Status</div>
              <select className="search-input" style={{ width: '100%', marginTop: 6 }}
                value={form.status} onChange={e => set('status', e.target.value)}>
                {STATUSES.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <div style={labelStyle}>Prioridade</div>
              <select className="search-input" style={{ width: '100%', marginTop: 6 }}
                value={form.priority} onChange={e => set('priority', e.target.value)}>
                {PRIORITIES.map(p => <option key={p}>{p}</option>)}
              </select>
            </div>
            <div>
              <div style={labelStyle}>Secretaria</div>
              <select className="search-input" style={{ width: '100%', marginTop: 6 }}
                value={form.secretariat_id ?? ''}
                onChange={e => set('secretariat_id', e.target.value ? parseInt(e.target.value) : null)}>
                <option value="">— sem vínculo —</option>
                {secretariats.map(s => (
                  <option key={s.id} value={s.id}>{s.acronym} — {s.name.slice(0, 28)}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Planejado + Realizado + Unidade + Prazo */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 130px', gap: 12 }}>
            {[
              { key: 'planned_value', label: 'Meta (planejado)', type: 'number' },
              { key: 'actual_value', label: 'Realizado', type: 'number' },
              { key: 'unit', label: 'Unidade', type: 'text' },
              { key: 'planned_date', label: 'Prazo (AAAA-MM)', type: 'text' },
            ].map(({ key, label, type }) => (
              <div key={key}>
                <div style={labelStyle}>{label}</div>
                <input className="search-input"
                  style={{ width: '100%', marginTop: 6 }}
                  type={type} step="any"
                  value={(form as Record<string, unknown>)[key] as string}
                  onChange={e => set(key as keyof MetaForm, e.target.value as never)}
                  placeholder={key === 'planned_date' ? '2026-12' : undefined}
                />
              </div>
            ))}
          </div>

          {/* Auto-calc preview */}
          {(form.planned_value || form.actual_value) && (
            <div style={{ fontSize: 12, color: 'var(--muted)' }}>
              Progresso calculado:{' '}
              <strong style={{ color: 'var(--accent)' }}>
                {calcProgress(form.planned_value, form.actual_value)?.toFixed(1) ?? '—'}%
              </strong>
            </div>
          )}

          {/* Flags */}
          <div>
            <div style={labelStyle}>Destaques</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, marginTop: 8 }}>
              {FLAGS.map(({ key, label }) => (
                <label key={key} style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer', fontSize: 13 }}>
                  <input type="checkbox"
                    checked={(form as Record<string, unknown>)[key] as boolean}
                    onChange={e => set(key as keyof MetaForm, e.target.checked as never)}
                  />
                  {label}
                </label>
              ))}
            </div>
          </div>

          {error && <div style={{ color: '#f85149', fontSize: 13 }}>{error}</div>}

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 4 }}>
            <button style={btnGhost} onClick={onClose}>Cancelar</button>
            <button style={btnPrimary} onClick={save} disabled={saving}>
              {saving ? 'Salvando...' : (meta ? 'Salvar alterações' : 'Criar meta')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Delete confirm ──────────────────────────────────────

function DeleteConfirm({
  meta, onClose, onDeleted,
}: { meta: MetaItem; onClose: () => void; onDeleted: () => void }) {
  const [loading, setLoading] = useState(false)

  async function confirm() {
    setLoading(true)
    await axios.delete(`/api/metas/${meta.id}`)
    onDeleted()
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" style={{ maxWidth: 400 }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span style={{ fontWeight: 700 }}>Excluir meta {meta.code}?</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <p style={{ color: 'var(--muted)', fontSize: 13, lineHeight: 1.5, margin: '0 0 8px' }}>
          {meta.description}
        </p>
        <p style={{ color: '#f85149', fontSize: 12, margin: '0 0 20px' }}>
          Esta ação não pode ser desfeita.
        </p>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          <button style={btnGhost} onClick={onClose}>Cancelar</button>
          <button
            style={{ ...btnBase, background: '#f85149', color: '#fff' }}
            onClick={confirm} disabled={loading}
          >
            {loading ? 'Excluindo...' : 'Excluir'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Shared label style ──────────────────────────────────

const labelStyle: React.CSSProperties = {
  fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px',
}

// ── Main page ───────────────────────────────────────────

export default function Objetivos() {
  const [groups, setGroups] = useState<GoalGroup[]>([])
  const [metas, setMetas] = useState<MetaItem[]>([])
  const [secretariats, setSecretariats] = useState<SecretariatOpt[]>([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<Set<number>>(new Set())
  const [pillarFilter, setPillarFilter] = useState('Todos')
  const [search, setSearch] = useState('')

  // Modal state
  const [editingGroup, setEditingGroup] = useState<GoalGroup | null>(null)
  const [metaModal, setMetaModal] = useState<{ meta: MetaItem | null; groupId: number } | null>(null)
  const [deletingMeta, setDeletingMeta] = useState<MetaItem | null>(null)

  useEffect(() => {
    Promise.all([
      axios.get<GoalGroup[]>('/api/metas/groups'),
      axios.get<MetaItem[]>('/api/metas'),
      axios.get<SecretariatOpt[]>('/api/secretariats'),
    ]).then(([g, m, s]) => {
      setGroups(g.data)
      setMetas(m.data)
      setSecretariats(s.data)
    }).finally(() => setLoading(false))
  }, [])

  const metasByGroup = useMemo(() => {
    const map: Record<number, MetaItem[]> = {}
    for (const m of metas) {
      ;(map[m.goal_group_id] ??= []).push(m)
    }
    return map
  }, [metas])

  const visibleGroups = useMemo(() =>
    groups.filter(g =>
      (pillarFilter === 'Todos' || g.pillar === pillarFilter) &&
      (!search || g.name.toLowerCase().includes(search.toLowerCase()))
    ), [groups, pillarFilter, search])

  function toggle(id: number) {
    setExpanded(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  function handleGroupSaved(g: GoalGroup) {
    setGroups(prev => prev.map(x => x.id === g.id ? g : x))
    setEditingGroup(null)
  }

  function handleMetaSaved(saved: MetaItem) {
    setMetas(prev => {
      const idx = prev.findIndex(m => m.id === saved.id)
      if (idx >= 0) { const next = [...prev]; next[idx] = saved; return next }
      return [...prev, saved]
    })
    setMetaModal(null)
  }

  function handleMetaDeleted(id: number) {
    setMetas(prev => prev.filter(m => m.id !== id))
    setDeletingMeta(null)
  }

  return (
    <div>
      {/* Header */}
      <div className="page-title">Dimensão: Objetivos do Programa de Metas</div>
      <div className="page-subtitle">
        {groups.length} objetivos · 3 eixos · {metas.length} metas
      </div>

      {/* KPI strip */}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 20 }}>
        {PILLAR_LABELS.map(p => {
          const c = PILLAR_COLORS[p]
          const count = groups.filter(g => g.pillar === p).length
          const metasCount = metas.filter(m => {
            const g = groups.find(gg => gg.id === m.goal_group_id)
            return g?.pillar === p
          }).length
          return (
            <div key={p} style={{
              background: 'var(--bg2)', border: `1px solid ${c}33`,
              borderLeft: `3px solid ${c}`, borderRadius: 8,
              padding: '8px 14px', cursor: 'pointer',
            }} onClick={() => setPillarFilter(pillarFilter === p ? 'Todos' : p)}>
              <div style={{ fontSize: 18, fontWeight: 700, color: c }}>{count}</div>
              <div style={{ fontSize: 10, color: 'var(--muted)', marginTop: 2 }}>
                {p.split(' e ')[0]}
              </div>
              <div style={{ fontSize: 10, color: c, marginTop: 1 }}>{metasCount} metas</div>
            </div>
          )
        })}
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 20, alignItems: 'center' }}>
        <input
          className="search-input"
          placeholder="Buscar objetivo..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ width: 260 }}
        />
        {['Todos', ...PILLAR_LABELS].map(p => {
          const active = pillarFilter === p
          const c = PILLAR_COLORS[p] || 'var(--accent)'
          return (
            <button key={p}
              className={`filter-btn${active ? ' active' : ''}`}
              style={active ? { borderColor: c, color: c, background: `${c}15` } : {}}
              onClick={() => setPillarFilter(p)}>
              {p === 'Todos' ? 'Todos os eixos' : p.split(' e ')[0]}
            </button>
          )
        })}
        {(pillarFilter !== 'Todos' || search) && (
          <button style={btnGhost}
            onClick={() => { setPillarFilter('Todos'); setSearch('') }}>
            Limpar filtros ✕
          </button>
        )}
      </div>

      {/* List */}
      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="loading-skeleton" style={{ height: 56, borderRadius: 8 }} />
          ))}
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {visibleGroups.map(group => {
            const gMetas = (metasByGroup[group.id] || []).slice().sort((a, b) =>
              a.code.localeCompare(b.code, undefined, { numeric: true })
            )
            const isOpen = expanded.has(group.id)
            const pColor = PILLAR_COLORS[group.pillar] || '#58a6ff'

            return (
              <div key={group.id} className="card" style={{ padding: 0, overflow: 'hidden' }}>

                {/* Group header row */}
                <div
                  style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '12px 16px', cursor: 'pointer',
                    borderBottom: isOpen ? '1px solid var(--border)' : 'none',
                  }}
                  onClick={() => toggle(group.id)}
                >
                  {/* Number badge */}
                  <div style={{
                    width: 30, height: 30, borderRadius: 8, flexShrink: 0,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: `${pColor}22`, color: pColor, fontWeight: 700, fontSize: 13,
                  }}>
                    {String(group.number).padStart(2, '0')}
                  </div>

                  {/* Name */}
                  <div style={{ flex: 1, fontWeight: 600, fontSize: 13, color: 'var(--text)', lineHeight: 1.3 }}>
                    {group.name}
                  </div>

                  {/* Pillar badge */}
                  <Pill label={group.pillar.split(' e ')[0]} color={pColor} />

                  {/* Meta count */}
                  <span style={{ fontSize: 11, color: 'var(--muted)', whiteSpace: 'nowrap' }}>
                    {gMetas.length} metas
                  </span>

                  {/* Edit group btn */}
                  <button style={{ ...btnGhost, fontSize: 11, padding: '3px 10px' }}
                    onClick={e => { e.stopPropagation(); setEditingGroup(group) }}>
                    ✏️ Objetivo
                  </button>

                  {/* Expand arrow */}
                  <span style={{
                    color: 'var(--muted)', fontSize: 11,
                    transform: isOpen ? 'rotate(180deg)' : 'none',
                    transition: 'transform 0.2s',
                    userSelect: 'none',
                  }}>▼</span>
                </div>

                {/* Metas table */}
                {isOpen && (
                  <div>
                    {gMetas.length > 0 ? (
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th style={{ width: 60 }}>Cód</th>
                            <th>Descrição</th>
                            <th style={{ width: 130 }}>Status</th>
                            <th style={{ width: 70 }}>Prior.</th>
                            <th style={{ width: 140 }}>Progresso</th>
                            <th style={{ width: 90 }}>Prazo</th>
                            <th style={{ width: 80 }}>Ações</th>
                          </tr>
                        </thead>
                        <tbody>
                          {gMetas.map(m => (
                            <tr key={m.id}>
                              <td style={{ fontWeight: 700, color: 'var(--accent)', fontFamily: 'monospace' }}>
                                {m.code}
                              </td>
                              <td>
                                <div style={{
                                  display: '-webkit-box', WebkitLineClamp: 2,
                                  WebkitBoxOrient: 'vertical', overflow: 'hidden',
                                  lineHeight: 1.4, maxWidth: 380,
                                }}>
                                  {m.description}
                                </div>
                                {m.secretariat && (
                                  <span style={{
                                    fontSize: 10, color: 'var(--muted)',
                                    background: 'var(--bg3)', borderRadius: 4,
                                    padding: '1px 5px', marginTop: 4, display: 'inline-block',
                                  }}>
                                    {m.secretariat.acronym}
                                  </span>
                                )}
                              </td>
                              <td>
                                <Pill label={m.status} color={STATUS_COLORS[m.status] || '#8b949e'} />
                              </td>
                              <td>
                                <span style={{
                                  display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                                  width: 22, height: 22, borderRadius: '50%',
                                  background: PRIORITY_COLORS[m.priority] || '#8b949e',
                                  color: '#fff', fontWeight: 700, fontSize: 11,
                                }}>
                                  {m.priority}
                                </span>
                              </td>
                              <td><MiniProgress pct={m.progress_pct} /></td>
                              <td style={{ color: 'var(--muted)', fontSize: 12 }}>
                                {m.planned_date || '—'}
                              </td>
                              <td>
                                <div style={{ display: 'flex', gap: 4 }}>
                                  <button style={{ ...btnGhost, padding: '3px 7px', fontSize: 12 }}
                                    onClick={() => setMetaModal({ meta: m, groupId: group.id })}>
                                    ✏️
                                  </button>
                                  <button style={{ ...btnDanger, padding: '3px 7px', fontSize: 12 }}
                                    onClick={() => setDeletingMeta(m)}>
                                    🗑️
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <div style={{ padding: '12px 16px', color: 'var(--muted)', fontSize: 13 }}>
                        Nenhuma meta cadastrada.
                      </div>
                    )}

                    {/* Add meta */}
                    <div style={{ padding: '10px 16px', borderTop: '1px solid var(--border)' }}>
                      <button
                        style={{ ...btnGhost, fontSize: 12, display: 'flex', alignItems: 'center', gap: 6 }}
                        onClick={() => setMetaModal({ meta: null, groupId: group.id })}
                      >
                        <span style={{ fontSize: 16, lineHeight: 1 }}>+</span> Nova Meta
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {!loading && visibleGroups.length === 0 && (
        <div className="empty-state">
          <div className="empty-state-icon">🔍</div>
          <div>Nenhum objetivo encontrado.</div>
        </div>
      )}

      {/* ── Modals ── */}
      {editingGroup && (
        <EditGroupModal
          group={editingGroup}
          onClose={() => setEditingGroup(null)}
          onSaved={handleGroupSaved}
        />
      )}

      {metaModal && (
        <MetaFormModal
          meta={metaModal.meta}
          groupId={metaModal.groupId}
          groups={groups}
          secretariats={secretariats}
          onClose={() => setMetaModal(null)}
          onSaved={handleMetaSaved}
        />
      )}

      {deletingMeta && (
        <DeleteConfirm
          meta={deletingMeta}
          onClose={() => setDeletingMeta(null)}
          onDeleted={() => handleMetaDeleted(deletingMeta.id)}
        />
      )}
    </div>
  )
}
