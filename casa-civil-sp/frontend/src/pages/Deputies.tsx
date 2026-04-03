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

  useEffect(() => {
    axios.get<Deputy[]>('/api/deputies')
      .then(r => setDeputies(r.data))
      .finally(() => setLoading(false))
  }, [])

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
      <div className="page-title">ALESP — Deputados Estaduais</div>
      <div className="page-subtitle">35ª Legislatura · {deputies.length} deputados</div>

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
              onClick={() => handleSelect(d.id)}
              style={{
                cursor: 'pointer',
                transition: 'border-color 0.15s, transform 0.1s',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 10,
                padding: '16px 12px',
              }}
              onMouseEnter={e => (e.currentTarget.style.borderColor = 'var(--accent)')}
              onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--border)')}
            >
              <PhotoAvatar url={d.photo_url} name={d.name} />
              <div style={{ textAlign: 'center', width: '100%' }}>
                <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 6, lineHeight: 1.3 }}>{d.name}</div>
                <span className="badge" style={{
                  background: `${partyColor(d.party)}22`,
                  color: partyColor(d.party),
                }}>
                  {d.party}
                </span>
                {d.is_substitute && (
                  <span className="badge" style={{ background: 'var(--bg3)', color: 'var(--muted)', marginLeft: 4 }}>
                    Suplente
                  </span>
                )}
              </div>
              <div style={{
                width: '100%', display: 'flex', justifyContent: 'space-between',
                borderTop: '1px solid var(--border)', paddingTop: 8, marginTop: 2,
              }}>
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
              </tr>
            </thead>
            <tbody>
              {filtered.map(d => (
                <tr key={d.id} onClick={() => handleSelect(d.id)}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <PhotoAvatar url={d.photo_url} name={d.name} />
                      <div>
                        <div style={{ fontWeight: 500 }}>{d.name}</div>
                        {d.is_substitute && <span style={{ fontSize: 11, color: 'var(--muted)' }}>Suplente</span>}
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="badge" style={{ background: `${partyColor(d.party)}22`, color: partyColor(d.party) }}>
                      {d.party}
                    </span>
                  </td>
                  <td>{d.votes_2022.toLocaleString('pt-BR')}</td>
                  <td>{d.mandates}</td>
                  <td>{d.ranking > 0 ? `#${d.ranking}` : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selected && (
        <DeputyModal deputy={selected} onClose={() => setSelected(null)} />
      )}

      {loadingDetail && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 999,
        }}>
          <div style={{ color: 'var(--muted)', fontSize: 14 }}>Carregando...</div>
        </div>
      )}
    </div>
  )
}
