import { useEffect, useState } from 'react'
import axios from 'axios'
import { partyColor } from '../utils'

interface SecretariatItem {
  id: number
  name: string
  acronym: string
  emoji: string | null
  secretary_name: string | null
  party: string | null
  executives: string | null
  meta_count: number
  meta_by_status: Record<string, number>
}

const STATUS_COLORS: Record<string, string> = {
  'Em andamento': '#58a6ff',
  'Em alerta': '#f0883e',
  'Atrasado': '#f85149',
  'Alcançado': '#3fb950',
  'Evento a confirmar': '#a371f7',
}

const btnBase: React.CSSProperties = {
  border: 'none', borderRadius: 6, cursor: 'pointer',
  fontFamily: 'var(--font)', fontWeight: 600, fontSize: 12, padding: '5px 12px',
}
const btnPrimary: React.CSSProperties = { ...btnBase, background: 'var(--accent)', color: '#fff' }
const btnGhost: React.CSSProperties = { ...btnBase, background: 'transparent', color: 'var(--muted)', border: '1px solid var(--border)' }
const btnDanger: React.CSSProperties = { ...btnBase, background: 'rgba(248,81,73,0.12)', color: '#f85149' }
const labelStyle: React.CSSProperties = { fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }

type SecForm = {
  name: string; acronym: string; emoji: string
  secretary_name: string; party: string; executives: string
}
const EMPTY_SEC: SecForm = { name: '', acronym: '', emoji: '', secretary_name: '', party: '', executives: '' }

function secToForm(s: SecretariatItem): SecForm {
  return { name: s.name, acronym: s.acronym, emoji: s.emoji || '', secretary_name: s.secretary_name || '', party: s.party || '', executives: s.executives || '' }
}

function SecretariatModal({
  item, onClose, onSaved,
}: { item: SecretariatItem | null; onClose: () => void; onSaved: (s: SecretariatItem) => void }) {
  const [form, setForm] = useState<SecForm>(item ? secToForm(item) : EMPTY_SEC)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  function set<K extends keyof SecForm>(k: K, v: string) { setForm(f => ({ ...f, [k]: v })) }

  async function save() {
    if (!form.name.trim()) { setError('Nome é obrigatório'); return }
    if (!form.acronym.trim()) { setError('Sigla é obrigatória'); return }
    setSaving(true); setError('')
    const payload = {
      name: form.name, acronym: form.acronym,
      emoji: form.emoji || null, secretary_name: form.secretary_name || null,
      party: form.party || null, executives: form.executives || null,
    }
    try {
      const { data } = item
        ? await axios.put<SecretariatItem>(`/api/secretariats/${item.id}`, payload)
        : await axios.post<SecretariatItem>('/api/secretariats', payload)
      onSaved({ ...data, meta_count: item?.meta_count ?? 0, meta_by_status: item?.meta_by_status ?? {} })
      onClose()
    } catch { setError('Erro ao salvar.') } finally { setSaving(false) }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" style={{ maxWidth: 560 }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span style={{ fontWeight: 700 }}>{item ? 'Editar Secretaria' : 'Nova Secretaria'}</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 120px 60px', gap: 12 }}>
            <div>
              <div style={labelStyle}>Nome *</div>
              <input className="search-input" style={{ width: '100%', marginTop: 6 }} value={form.name} onChange={e => set('name', e.target.value)} />
            </div>
            <div>
              <div style={labelStyle}>Sigla *</div>
              <input className="search-input" style={{ width: '100%', marginTop: 6 }} value={form.acronym} onChange={e => set('acronym', e.target.value)} placeholder="SEE" />
            </div>
            <div>
              <div style={labelStyle}>Emoji</div>
              <input className="search-input" style={{ width: '100%', marginTop: 6 }} value={form.emoji} onChange={e => set('emoji', e.target.value)} placeholder="📚" />
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 120px', gap: 12 }}>
            <div>
              <div style={labelStyle}>Secretário(a)</div>
              <input className="search-input" style={{ width: '100%', marginTop: 6 }} value={form.secretary_name} onChange={e => set('secretary_name', e.target.value)} />
            </div>
            <div>
              <div style={labelStyle}>Partido</div>
              <input className="search-input" style={{ width: '100%', marginTop: 6 }} value={form.party} onChange={e => set('party', e.target.value)} placeholder="PL" />
            </div>
          </div>
          <div>
            <div style={labelStyle}>Secretários Executivos (formato: Nome|Partido; Nome|Partido)</div>
            <textarea className="search-input" style={{ width: '100%', marginTop: 6, resize: 'vertical' }} rows={3} value={form.executives} onChange={e => set('executives', e.target.value)} placeholder="João Silva|PL; Maria Santos|PP" />
          </div>
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
          <button style={{ ...btnBase, background: '#f85149', color: '#fff' }}
            onClick={async () => { setLoading(true); await onConfirm() }}
            disabled={loading}>{loading ? 'Excluindo...' : 'Excluir'}</button>
        </div>
      </div>
    </div>
  )
}

function parseExecutives(raw: string | null): { name: string; party: string }[] {
  if (!raw) return []
  return raw.split(';').map(entry => {
    const [name, party] = entry.split('|')
    return { name: name?.trim() || '', party: party?.trim() || 'sem partido' }
  }).filter(e => e.name)
}

function PartyBadge({ party }: { party: string | null }) {
  if (!party || party === 'sem partido') {
    return (
      <span style={{ display: 'inline-block', padding: '2px 8px', borderRadius: 12, fontSize: 10, fontWeight: 600, background: 'rgba(139,148,158,0.15)', color: '#8b949e', letterSpacing: '0.3px' }}>
        sem partido
      </span>
    )
  }
  const color = partyColor(party)
  return (
    <span style={{ display: 'inline-block', padding: '2px 8px', borderRadius: 12, fontSize: 10, fontWeight: 600, letterSpacing: '0.3px', background: `${color}22`, color, border: `1px solid ${color}44` }}>
      {party}
    </span>
  )
}

export default function Secretariats() {
  const [secretariats, setSecretariats] = useState<SecretariatItem[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [modal, setModal] = useState<{ item: SecretariatItem | null } | null>(null)
  const [deleting, setDeleting] = useState<SecretariatItem | null>(null)

  useEffect(() => {
    axios.get<SecretariatItem[]>('/api/secretariats')
      .then(r => setSecretariats(r.data))
      .finally(() => setLoading(false))
  }, [])

  const filtered = secretariats.filter(s =>
    !search ||
    s.name.toLowerCase().includes(search.toLowerCase()) ||
    (s.secretary_name || '').toLowerCase().includes(search.toLowerCase())
  )

  function handleSaved(s: SecretariatItem) {
    setSecretariats(prev => {
      const idx = prev.findIndex(x => x.id === s.id)
      if (idx >= 0) { const next = [...prev]; next[idx] = s; return next }
      return [...prev, s]
    })
  }

  async function handleDelete(id: number, name: string) {
    await axios.delete(`/api/secretariats/${id}`)
    setSecretariats(prev => prev.filter(s => s.id !== id))
    setDeleting(null)
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 4 }}>
        <div>
          <div className="page-title">Secretarias de Estado</div>
          <div className="page-subtitle">Governo Tarcísio de Freitas · {secretariats.length} secretarias</div>
        </div>
        <button style={btnPrimary} onClick={() => setModal({ item: null })}>+ Nova Secretaria</button>
      </div>

      {/* Search */}
      <div style={{ marginBottom: 20, marginTop: 16 }}>
        <input className="search-input" style={{ width: '100%', maxWidth: 400 }} placeholder="Buscar secretaria ou secretário..." value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      {loading ? (
        <div className="sec-grid">{Array.from({ length: 10 }).map((_, i) => <div key={i} className="loading-skeleton" style={{ height: 200 }} />)}</div>
      ) : (
        <div className="sec-grid">
          {filtered.map(sec => {
            const executives = parseExecutives(sec.executives)
            return (
              <div key={sec.id} className="card sec-card" style={{ position: 'relative' }}>

                {/* CRUD actions */}
                <div style={{ position: 'absolute', top: 10, right: 10, display: 'flex', gap: 4, zIndex: 1 }}>
                  <button style={{ ...btnGhost, padding: '3px 8px', fontSize: 11 }} onClick={() => setModal({ item: sec })}>✏️</button>
                  <button style={{ ...btnDanger, padding: '3px 8px', fontSize: 11 }} onClick={() => setDeleting(sec)}>🗑️</button>
                </div>

                {/* Emoji */}
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
                  <div style={{ fontSize: 36, lineHeight: 1, width: 52, height: 52, background: 'var(--bg3)', borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    {sec.emoji || '🏛️'}
                  </div>
                  <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '1px', color: 'var(--accent)', background: 'rgba(88,166,255,0.1)', padding: '3px 8px', borderRadius: 8, marginRight: 56 }}>
                    {sec.acronym}
                  </span>
                </div>

                {/* Name */}
                <div style={{ fontWeight: 700, fontSize: 15, lineHeight: 1.3, marginBottom: 14, color: 'var(--text)' }}>{sec.name}</div>

                {/* Secretary */}
                <div style={{ borderTop: '1px solid var(--border)', paddingTop: 12, marginBottom: 12 }}>
                  <div style={{ fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 6 }}>SECRETÁRIO(A)</div>
                  <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 6 }}>{sec.secretary_name || '—'}</div>
                  <PartyBadge party={sec.party} />
                </div>

                {/* Executives */}
                {executives.length > 0 && (
                  <div style={{ borderTop: '1px solid var(--border)', paddingTop: 12 }}>
                    <div style={{ fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>SECRETÁRIOS(AS) EXECUTIVOS(AS)</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                      {executives.map((exec, i) => (
                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
                          <div style={{ fontSize: 12, color: 'var(--text)', flex: 1, minWidth: 0 }}>{exec.name}</div>
                          <PartyBadge party={exec.party} />
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Metas vinculadas */}
                {sec.meta_count > 0 && (
                  <div style={{ borderTop: '1px solid var(--border)', paddingTop: 12, marginTop: 12 }}>
                    <div style={{ fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>METAS VINCULADAS ({sec.meta_count})</div>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      {Object.entries(sec.meta_by_status).map(([status, count]) => {
                        const color = STATUS_COLORS[status] || '#8b949e'
                        return (
                          <span key={status} style={{ fontSize: 11, padding: '2px 8px', borderRadius: 10, background: `${color}20`, color, border: `1px solid ${color}44`, whiteSpace: 'nowrap' }}>
                            {count} {status}
                          </span>
                        )
                      })}
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {!loading && filtered.length === 0 && (
        <div className="empty-state"><div className="empty-state-icon">🔍</div><div>Nenhuma secretaria encontrada.</div></div>
      )}

      {modal && <SecretariatModal item={modal.item} onClose={() => setModal(null)} onSaved={handleSaved} />}
      {deleting && <DeleteConfirm name={deleting.name} onClose={() => setDeleting(null)} onConfirm={() => handleDelete(deleting.id, deleting.name)} />}
    </div>
  )
}

