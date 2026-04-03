import { useEffect, useState, useMemo } from 'react'
import axios from 'axios'
import { fmt_currency, partyColor, PHOTO_BASE } from '../utils'

interface Deputy {
  id: number
  name: string
  party: string
  votes_2022: number
  ranking: number
  is_substitute: boolean
  mandates: number
  photo_url: string | null
}

interface Amendment {
  id: number
  year: number
  value: number
  description: string
  status: string
}

interface DeputyDetail extends Deputy {
  registration: number | null
  amendments: Amendment[]
}

const PARTIES = ['PL', 'PT', 'PSDB', 'PSOL', 'PSD', 'REPUBLICANOS', 'UNIÃO', 'PP', 'MDB', 'PSB', 'PODE', 'Outros']
const ALL_PARTIES = ['PL', 'PT', 'PSDB', 'PSOL', 'PSD', 'REPUBLICANOS', 'UNIÃO', 'PP', 'MDB', 'PSB', 'PODE', 'PDT', 'SOLIDARIEDADE', 'AVANTE', 'PATRIOTA', 'PRD', 'REDE', 'PSC', 'DEM', 'Sem partido']

const btnBase: React.CSSProperties = { border: 'none', borderRadius: 6, cursor: 'pointer', fontFamily: 'var(--font)', fontWeight: 600, fontSize: 12, padding: '5px 12px' }
const btnPrimary: React.CSSProperties = { ...btnBase, background: 'var(--accent)', color: '#fff' }
const btnGhost: React.CSSProperties = { ...btnBase, background: 'transparent', color: 'var(--muted)', border: '1px solid var(--border)' }
const btnDanger: React.CSSProperties = { ...btnBase, background: 'rgba(248,81,73,0.12)', color: '#f85149' }
const labelStyle: React.CSSProperties = { fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }

type DepForm = { name: string; party: string; votes_2022: string; registration: string; ranking: string; is_substitute: boolean; mandates: string; photo_url: string }
const EMPTY_DEP: DepForm = { name: '', party: 'PL', votes_2022: '0', registration: '', ranking: '0', is_substitute: false, mandates: '1', photo_url: '' }

function depToForm(d: Deputy): DepForm {
  return { name: d.name, party: d.party, votes_2022: String(d.votes_2022), registration: '', ranking: String(d.ranking), is_substitute: d.is_substitute, mandates: String(d.mandates), photo_url: d.photo_url || '' }
}

function DeputyFormModal({ item, onClose, onSaved }: { item: Deputy | null; onClose: () => void; onSaved: (d: Deputy) => void }) {
  const [form, setForm] = useState<DepForm>(item ? depToForm(item) : EMPTY_DEP)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  function set<K extends keyof DepForm>(k: K, v: DepForm[K]) { setForm(f => ({ ...f, [k]: v })) }

  async function save() {
    if (!form.name.trim()) { setError('Nome é obrigatório'); return }
    setSaving(true); setError('')
    const payload = {
      name: form.name.trim(), party: form.party,
      votes_2022: parseInt(form.votes_2022) || 0,
      registration: form.registration ? parseInt(form.registration) : null,
      ranking: parseInt(form.ranking) || 0,
      is_substitute: form.is_substitute,
      mandates: parseInt(form.mandates) || 1,
      photo_url: form.photo_url.trim() || null,
    }
    try {
      const { data } = item
        ? await axios.put<Deputy>(`/api/deputies/${item.id}`, payload)
        : await axios.post<Deputy>('/api/deputies', payload)
      onSaved(data); onClose()
    } catch { setError('Erro ao salvar.') } finally { setSaving(false) }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" style={{ maxWidth: 560 }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span style={{ fontWeight: 700 }}>{item ? 'Editar Deputado' : 'Novo Deputado'}</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <div style={labelStyle}>Nome *</div>
            <input className="search-input" style={{ width: '100%', marginTop: 6 }} value={form.name} onChange={e => set('name', e.target.value)} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 100px 90px', gap: 12 }}>
            <div>
              <div style={labelStyle}>Partido</div>
              <select className="search-input" style={{ width: '100%', marginTop: 6 }} value={form.party} onChange={e => set('party', e.target.value)}>
                {ALL_PARTIES.map(p => <option key={p}>{p}</option>)}
              </select>
            </div>
            <div>
              <div style={labelStyle}>Votos 2022</div>
              <input className="search-input" style={{ width: '100%', marginTop: 6 }} type="number" value={form.votes_2022} onChange={e => set('votes_2022', e.target.value)} />
            </div>
            <div>
              <div style={labelStyle}>Mandatos</div>
              <input className="search-input" style={{ width: '100%', marginTop: 6 }} type="number" value={form.mandates} onChange={e => set('mandates', e.target.value)} />
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <div style={labelStyle}>Ranking</div>
              <input className="search-input" style={{ width: '100%', marginTop: 6 }} type="number" value={form.ranking} onChange={e => set('ranking', e.target.value)} />
            </div>
            <div>
              <div style={labelStyle}>Matrícula ALESP</div>
              <input className="search-input" style={{ width: '100%', marginTop: 6 }} type="number" value={form.registration} onChange={e => set('registration', e.target.value)} />
            </div>
          </div>
          <div>
            <div style={labelStyle}>URL da foto (hash do ALESP)</div>
            <input className="search-input" style={{ width: '100%', marginTop: 6 }} value={form.photo_url} onChange={e => set('photo_url', e.target.value)} placeholder="hash-da-foto" />
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: 13 }}>
            <input type="checkbox" checked={form.is_substitute} onChange={e => set('is_substitute', e.target.checked)} />
            Suplente
          </label>
          {error && <div style={{ color: '#f85149', fontSize: 13 }}>{error}</div>}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
            <button style={btnGhost} onClick={onClose}>Cancelar</button>
            <button style={btnPrimary} onClick={save} disabled={saving}>{saving ? 'Salvando...' : (item ? 'Salvar' : 'Criar')}</button>
          </div>
        </div>
      </div>
    </div>
  )
}

function DeleteConfirm({ name, onClose, onConfirm }: { name: string; onClose: () => void; onConfirm: () => void }) {
  const [loading, setLoading] = useState(false)
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" style={{ maxWidth: 380 }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span style={{ fontWeight: 700 }}>Excluir?</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <p style={{ color: 'var(--muted)', margin: '0 0 16px', fontSize: 13 }}>{name}</p>
        <p style={{ color: '#f85149', fontSize: 12, marginBottom: 20 }}>Esta ação não pode ser desfeita.</p>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          <button style={btnGhost} onClick={onClose}>Cancelar</button>
          <button style={{ ...btnBase, background: '#f85149', color: '#fff' }} onClick={async () => { setLoading(true); await onConfirm() }} disabled={loading}>{loading ? 'Excluindo...' : 'Excluir'}</button>
        </div>
      </div>
    </div>
  )
}

function PhotoAvatar({ url, name }: { url: string | null; name: string }) {
  const [err, setErr] = useState(false)
  const src = url ? `${PHOTO_BASE}${url}` : ''

  if (!src || err) {
    return (
      <div style={{
        width: 76, height: 76, borderRadius: '50%',
        background: 'var(--bg3)', border: '2px solid var(--border)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 26, color: 'var(--muted)', flexShrink: 0,
      }}>
        {name.charAt(0).toUpperCase()}
      </div>
    )
  }

  return (
    <img
      src={src}
      alt={name}
      onError={() => setErr(true)}
      style={{
        width: 76, height: 76, borderRadius: '50%',
        objectFit: 'cover', border: '2px solid var(--border)', flexShrink: 0,
      }}
    />
  )
}

function AmendmentBadge({ status }: { status: string }) {
  return <span className={`badge badge-${status}`}>{status}</span>
}

function DeputyModal({ deputy, onClose }: { deputy: DeputyDetail; onClose: () => void }) {
  const total = deputy.amendments.reduce((sum, a) => sum + a.value, 0)

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
            <PhotoAvatar url={deputy.photo_url} name={deputy.name} />
            <div>
              <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>{deputy.name}</div>
              <span className="badge" style={{
                background: `${partyColor(deputy.party)}22`,
                color: partyColor(deputy.party),
                border: `1px solid ${partyColor(deputy.party)}44`,
              }}>
                {deputy.party}
              </span>
            </div>
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        {/* Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginBottom: 20 }}>
          {[
            { label: 'Votos 2022', value: deputy.votes_2022.toLocaleString('pt-BR') },
            { label: 'Mandatos', value: deputy.mandates },
            { label: 'Ranking', value: deputy.ranking > 0 ? `#${deputy.ranking}` : 'Suplente' },
          ].map(({ label, value }) => (
            <div key={label} style={{ background: 'var(--bg3)', borderRadius: 6, padding: '10px 12px' }}>
              <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 4 }}>{label}</div>
              <div style={{ fontWeight: 600, fontSize: 15 }}>{value}</div>
            </div>
          ))}
        </div>

        {/* Amendments */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Emendas ({deputy.amendments.length})
            </div>
            {total > 0 && (
              <div style={{ fontSize: 13, color: 'var(--green)', fontWeight: 600 }}>
                Total: {fmt_currency(total)}
              </div>
            )}
          </div>

          {deputy.amendments.length === 0 ? (
            <div style={{ color: 'var(--muted)', fontSize: 13, padding: '16px 0' }}>Nenhuma emenda registrada.</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {deputy.amendments.map(am => (
                <div key={am.id} style={{
                  background: 'var(--bg3)', borderRadius: 6, padding: '10px 12px',
                  border: '1px solid var(--border)',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12,
                }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {am.description}
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--muted)' }}>Ano: {am.year}</div>
                  </div>
                  <div style={{ textAlign: 'right', flexShrink: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--green)', marginBottom: 4 }}>
                      {fmt_currency(am.value)}
                    </div>
                    <AmendmentBadge status={am.status} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function Deputies() {
  const [deputies, setDeputies] = useState<Deputy[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [partyFilter, setPartyFilter] = useState('Todos')
  const [sortBy, setSortBy] = useState('name')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [selected, setSelected] = useState<DeputyDetail | null>(null)
  const [loadingDetail, setLoadingDetail] = useState(false)
  const [modal, setModal] = useState<{ item: Deputy | null } | null>(null)
  const [deleting, setDeleting] = useState<Deputy | null>(null)

  useEffect(() => {
    axios.get<Deputy[]>('/api/deputies')
      .then(r => setDeputies(r.data))
      .finally(() => setLoading(false))
  }, [])

  function handleSaved(d: Deputy) {
    setDeputies(prev => {
      const idx = prev.findIndex(x => x.id === d.id)
      if (idx >= 0) { const next = [...prev]; next[idx] = d; return next }
      return [...prev, d]
    })
  }

  async function handleDeleteConfirm() {
    if (!deleting) return
    await axios.delete(`/api/deputies/${deleting.id}`)
    setDeputies(prev => prev.filter(d => d.id !== deleting.id))
    setDeleting(null)
  }

  const filtered = useMemo(() => {
    let list = [...deputies]
    if (search) {
      const s = search.toLowerCase()
      list = list.filter(d => d.name.toLowerCase().includes(s))
    }
    if (partyFilter !== 'Todos') {
      if (partyFilter === 'Outros') {
        const mainParties = ['PL', 'PT', 'PSDB', 'PSOL', 'PSD', 'REPUBLICANOS', 'UNIÃO', 'PP']
        list = list.filter(d => !mainParties.includes(d.party))
      } else {
        list = list.filter(d => d.party === partyFilter)
      }
    }
    list.sort((a, b) => {
      if (sortBy === 'votes') return b.votes_2022 - a.votes_2022
      if (sortBy === 'mandates') return b.mandates - a.mandates
      if (sortBy === 'party') return a.party.localeCompare(b.party)
      return a.name.localeCompare(b.name)
    })
    return list
  }, [deputies, search, partyFilter, sortBy])

  const handleSelect = async (id: number) => {
    setLoadingDetail(true)
    try {
      const r = await axios.get<DeputyDetail>(`/api/deputies/${id}`)
      setSelected(r.data)
    } finally {
      setLoadingDetail(false)
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 4 }}>
        <div>
          <div className="page-title">ALESP — Deputados Estaduais</div>
          <div className="page-subtitle">35ª Legislatura · {deputies.length} deputados</div>
        </div>
        <button style={btnPrimary} onClick={() => setModal({ item: null })}>+ Novo Deputado</button>
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 16, flexWrap: 'wrap', alignItems: 'center' }}>
        <input
          className="search-input"
          placeholder="Buscar deputado..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ width: 220 }}
        />

        <select
          value={sortBy}
          onChange={e => setSortBy(e.target.value)}
          style={{
            background: 'var(--bg3)', border: '1px solid var(--border)',
            borderRadius: 6, color: 'var(--text)', padding: '8px 12px',
            fontSize: 12, cursor: 'pointer',
          }}
        >
          <option value="name">Nome</option>
          <option value="votes">Votos</option>
          <option value="party">Partido</option>
          <option value="mandates">Mandatos</option>
        </select>

        <div style={{ display: 'flex', gap: 4, marginLeft: 'auto' }}>
          {(['grid', 'list'] as const).map(m => (
            <button
              key={m}
              className={`filter-btn ${viewMode === m ? 'active' : ''}`}
              onClick={() => setViewMode(m)}
            >
              {m === 'grid' ? '⊞' : '≡'}
            </button>
          ))}
        </div>
      </div>

      {/* Party filters */}
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 20 }}>
        {['Todos', ...PARTIES].map(p => (
          <button
            key={p}
            className={`filter-btn ${partyFilter === p ? 'active' : ''}`}
            onClick={() => setPartyFilter(p)}
            style={p !== 'Todos' && PARTIES.includes(p) && p !== 'Outros' ? {
              borderColor: partyFilter === p ? partyColor(p) : undefined,
              color: partyFilter === p ? partyColor(p) : undefined,
              background: partyFilter === p ? `${partyColor(p)}22` : undefined,
            } : {}}
          >
            {p}
          </button>
        ))}
      </div>

      <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 12 }}>
        {filtered.length} resultado{filtered.length !== 1 ? 's' : ''}
      </div>

      {loading ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 12 }}>
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="loading-skeleton" style={{ height: 120 }} />
          ))}
        </div>
      ) : viewMode === 'grid' ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 12 }}>
          {filtered.map(d => (
            <div
              key={d.id}
              className="card"
              style={{ cursor: 'pointer', transition: 'border-color 0.15s, transform 0.1s', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10, padding: '16px 12px', position: 'relative' }}
              onMouseEnter={e => (e.currentTarget.style.borderColor = 'var(--accent)')}
              onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--border)')}
            >
              {/* CRUD buttons */}
              <div style={{ position: 'absolute', top: 6, right: 6, display: 'flex', gap: 2 }} onClick={e => e.stopPropagation()}>
                <button style={{ ...btnGhost, padding: '2px 6px', fontSize: 11 }} onClick={() => setModal({ item: d })}>✏️</button>
                <button style={{ ...btnDanger, padding: '2px 6px', fontSize: 11 }} onClick={() => setDeleting(d)}>🗑️</button>
              </div>
              <div onClick={() => handleSelect(d.id)} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10, width: '100%' }}>
                <PhotoAvatar url={d.photo_url} name={d.name} />
                <div style={{ textAlign: 'center', width: '100%' }}>
                  <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 6, lineHeight: 1.3 }}>{d.name}</div>
                  <span className="badge" style={{ background: `${partyColor(d.party)}22`, color: partyColor(d.party) }}>{d.party}</span>
                  {d.is_substitute && <span className="badge" style={{ background: 'var(--bg3)', color: 'var(--muted)', marginLeft: 4 }}>Suplente</span>}
                </div>
                <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border)', paddingTop: 8, marginTop: 2 }}>
                  <div style={{ textAlign: 'center', flex: 1 }}>
                    <div style={{ fontSize: 11, color: 'var(--muted)' }}>Votos</div>
                    <div style={{ fontSize: 12, fontWeight: 600 }}>{d.votes_2022.toLocaleString('pt-BR')}</div>
                  </div>
                  <div style={{ textAlign: 'center', flex: 1 }}>
                    <div style={{ fontSize: 11, color: 'var(--muted)' }}>Mandatos</div>
                    <div style={{ fontSize: 12, fontWeight: 600 }}>{d.mandates}</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Deputado</th>
                <th>Partido</th>
                <th>Votos 2022</th>
                <th>Mandatos</th>
                <th>Ranking</th>
                <th style={{ width: 80 }}>Ações</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(d => (
                <tr key={d.id}>
                  <td onClick={() => handleSelect(d.id)} style={{ cursor: 'pointer' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <PhotoAvatar url={d.photo_url} name={d.name} />
                      <div>
                        <div style={{ fontWeight: 500 }}>{d.name}</div>
                        {d.is_substitute && <span style={{ fontSize: 11, color: 'var(--muted)' }}>Suplente</span>}
                      </div>
                    </div>
                  </td>
                  <td><span className="badge" style={{ background: `${partyColor(d.party)}22`, color: partyColor(d.party) }}>{d.party}</span></td>
                  <td>{d.votes_2022.toLocaleString('pt-BR')}</td>
                  <td>{d.mandates}</td>
                  <td>{d.ranking > 0 ? `#${d.ranking}` : '—'}</td>
                  <td>
                    <div style={{ display: 'flex', gap: 4 }}>
                      <button style={{ ...btnGhost, padding: '3px 7px', fontSize: 12 }} onClick={() => setModal({ item: d })}>✏️</button>
                      <button style={{ ...btnDanger, padding: '3px 7px', fontSize: 12 }} onClick={() => setDeleting(d)}>🗑️</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selected && <DeputyModal deputy={selected} onClose={() => setSelected(null)} />}
      {modal && <DeputyFormModal item={modal.item} onClose={() => setModal(null)} onSaved={handleSaved} />}
      {deleting && <DeleteConfirm name={deleting.name} onClose={() => setDeleting(null)} onConfirm={handleDeleteConfirm} />}

      {loadingDetail && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 999 }}>
          <div style={{ color: 'var(--muted)', fontSize: 14 }}>Carregando...</div>
        </div>
      )}
    </div>
  )
}
