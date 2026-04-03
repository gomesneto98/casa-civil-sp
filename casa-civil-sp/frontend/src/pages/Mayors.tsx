import { useEffect, useState, useMemo, useRef } from 'react'
import axios from 'axios'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import type { Map as LeafletMap } from 'leaflet'
import { partyColor } from '../utils'

interface Mayor {
  id: number
  name: string
  party: string
  term_start: number
  term_end: number
}

interface Municipality {
  id: number
  name: string
  region: string
  population: number | null
  lat: number | null
  lng: number | null
  mayor: Mayor | null
}

const REGION_COLORS: Record<string, string> = {
  'Grande SP': '#58a6ff',
  'Interior': '#3fb950',
  'Litoral': '#d29922',
  'Vale do Paraíba': '#f85149',
}

const REGIONS = ['Todos', 'Grande SP', 'Interior', 'Litoral', 'Vale do Paraíba']
const ALL_PARTIES = ['PL', 'PT', 'PSDB', 'PSOL', 'PSD', 'REPUBLICANOS', 'UNIÃO', 'PP', 'MDB', 'PSB', 'PODE', 'PDT', 'SOLIDARIEDADE', 'PATRIOTA', 'PRD', 'AVANTE', 'Outro']

const btnBase: React.CSSProperties = { border: 'none', borderRadius: 6, cursor: 'pointer', fontFamily: 'var(--font)', fontWeight: 600, fontSize: 12, padding: '5px 12px' }
const btnPrimary: React.CSSProperties = { ...btnBase, background: 'var(--accent)', color: '#fff' }
const btnGhost: React.CSSProperties = { ...btnBase, background: 'transparent', color: 'var(--muted)', border: '1px solid var(--border)' }
const btnDanger: React.CSSProperties = { ...btnBase, background: 'rgba(248,81,73,0.12)', color: '#f85149' }
const labelStyle: React.CSSProperties = { fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }

// ── Municipality form modal ──────────────────────────────────────────────────

type MunForm = { name: string; region: string; population: string; lat: string; lng: string }
type MayorForm = { name: string; party: string; term_start: string; term_end: string }

function MunicipalityModal({
  item, onClose, onSaved,
}: { item: Municipality | null; onClose: () => void; onSaved: (m: Municipality) => void }) {
  const [mun, setMun] = useState<MunForm>({
    name: item?.name || '', region: item?.region || 'Interior',
    population: item?.population?.toString() || '',
    lat: item?.lat?.toString() || '', lng: item?.lng?.toString() || '',
  })
  const [mayor, setMayor] = useState<MayorForm>({
    name: item?.mayor?.name || '', party: item?.mayor?.party || 'PL',
    term_start: item?.mayor?.term_start?.toString() || '2025',
    term_end: item?.mayor?.term_end?.toString() || '2028',
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  function setM<K extends keyof MunForm>(k: K, v: string) { setMun(f => ({ ...f, [k]: v })) }
  function setMa<K extends keyof MayorForm>(k: K, v: string) { setMayor(f => ({ ...f, [k]: v })) }

  async function save() {
    if (!mun.name.trim()) { setError('Nome do município é obrigatório'); return }
    setSaving(true); setError('')
    try {
      const munPayload = {
        name: mun.name.trim(), region: mun.region,
        population: mun.population ? parseInt(mun.population) : null,
        lat: mun.lat ? parseFloat(mun.lat) : null,
        lng: mun.lng ? parseFloat(mun.lng) : null,
      }
      const { data: saved } = item
        ? await axios.put<Municipality>(`/api/municipalities/${item.id}`, munPayload)
        : await axios.post<Municipality>('/api/municipalities', munPayload)

      // Upsert mayor if name provided
      if (mayor.name.trim()) {
        const mayorPayload = { name: mayor.name.trim(), party: mayor.party, term_start: parseInt(mayor.term_start), term_end: parseInt(mayor.term_end) }
        if (item?.mayor) {
          const { data: ma } = await axios.put<Mayor>(`/api/municipalities/${saved.id}/mayor`, mayorPayload)
          saved.mayor = ma
        } else {
          const { data: ma } = await axios.post<Mayor>(`/api/municipalities/${saved.id}/mayor`, mayorPayload)
          saved.mayor = ma
        }
      }
      onSaved(saved); onClose()
    } catch { setError('Erro ao salvar.') } finally { setSaving(false) }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" style={{ maxWidth: 540 }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span style={{ fontWeight: 700 }}>{item ? 'Editar Município' : 'Novo Município'}</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {/* Município */}
          <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Dados do Município</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 160px', gap: 12 }}>
            <div>
              <div style={labelStyle}>Nome *</div>
              <input className="search-input" style={{ width: '100%', marginTop: 6 }} value={mun.name} onChange={e => setM('name', e.target.value)} />
            </div>
            <div>
              <div style={labelStyle}>Região</div>
              <select className="search-input" style={{ width: '100%', marginTop: 6 }} value={mun.region} onChange={e => setM('region', e.target.value)}>
                {['Grande SP', 'Interior', 'Litoral', 'Vale do Paraíba'].map(r => <option key={r}>{r}</option>)}
              </select>
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
            <div>
              <div style={labelStyle}>População</div>
              <input className="search-input" style={{ width: '100%', marginTop: 6 }} type="number" value={mun.population} onChange={e => setM('population', e.target.value)} />
            </div>
            <div>
              <div style={labelStyle}>Latitude</div>
              <input className="search-input" style={{ width: '100%', marginTop: 6 }} type="number" step="any" value={mun.lat} onChange={e => setM('lat', e.target.value)} placeholder="-23.5" />
            </div>
            <div>
              <div style={labelStyle}>Longitude</div>
              <input className="search-input" style={{ width: '100%', marginTop: 6 }} type="number" step="any" value={mun.lng} onChange={e => setM('lng', e.target.value)} placeholder="-46.6" />
            </div>
          </div>

          {/* Prefeito */}
          <div style={{ borderTop: '1px solid var(--border)', paddingTop: 14 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 12 }}>Prefeito(a) {!item?.mayor ? '(opcional)' : ''}</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 120px', gap: 12 }}>
              <div>
                <div style={labelStyle}>Nome</div>
                <input className="search-input" style={{ width: '100%', marginTop: 6 }} value={mayor.name} onChange={e => setMa('name', e.target.value)} />
              </div>
              <div>
                <div style={labelStyle}>Partido</div>
                <select className="search-input" style={{ width: '100%', marginTop: 6 }} value={mayor.party} onChange={e => setMa('party', e.target.value)}>
                  {ALL_PARTIES.map(p => <option key={p}>{p}</option>)}
                </select>
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 12 }}>
              <div>
                <div style={labelStyle}>Início do mandato</div>
                <input className="search-input" style={{ width: '100%', marginTop: 6 }} type="number" value={mayor.term_start} onChange={e => setMa('term_start', e.target.value)} />
              </div>
              <div>
                <div style={labelStyle}>Fim do mandato</div>
                <input className="search-input" style={{ width: '100%', marginTop: 6 }} type="number" value={mayor.term_end} onChange={e => setMa('term_end', e.target.value)} />
              </div>
            </div>
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
          <span style={{ fontWeight: 700 }}>Excluir município?</span>
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

function FlyTo({ lat, lng }: { lat: number; lng: number }) {
  const map = useMap()
  useEffect(() => {
    map.flyTo([lat, lng], 10, { duration: 1 })
  }, [lat, lng, map])
  return null
}

function formatPop(n: number | null) {
  if (!n) return '—'
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M hab.`
  if (n >= 1_000) return `${Math.round(n / 1_000)}k hab.`
  return `${n} hab.`
}

export default function Mayors() {
  const [municipalities, setMunicipalities] = useState<Municipality[]>([])
  const [loading, setLoading] = useState(true)
  const [regionFilter, setRegionFilter] = useState('Todos')
  const [search, setSearch] = useState('')
  const [focusCity, setFocusCity] = useState<{ lat: number; lng: number } | null>(null)
  const [highlightId, setHighlightId] = useState<number | null>(null)
  const [modal, setModal] = useState<{ item: Municipality | null } | null>(null)
  const [deleting, setDeleting] = useState<Municipality | null>(null)

  useEffect(() => {
    axios.get<Municipality[]>('/api/municipalities')
      .then(r => setMunicipalities(r.data))
      .finally(() => setLoading(false))
  }, [])

  function handleSaved(m: Municipality) {
    setMunicipalities(prev => {
      const idx = prev.findIndex(x => x.id === m.id)
      if (idx >= 0) { const next = [...prev]; next[idx] = m; return next }
      return [...prev, m]
    })
  }

  async function handleDeleteConfirm() {
    if (!deleting) return
    await axios.delete(`/api/municipalities/${deleting.id}`)
    setMunicipalities(prev => prev.filter(m => m.id !== deleting.id))
    setDeleting(null)
  }

  const filtered = useMemo(() => {
    let list = municipalities
    if (regionFilter !== 'Todos') list = list.filter(m => m.region === regionFilter)
    if (search) list = list.filter(m =>
      m.name.toLowerCase().includes(search.toLowerCase()) ||
      (m.mayor?.name || '').toLowerCase().includes(search.toLowerCase())
    )
    return list
  }, [municipalities, regionFilter, search])

  const handleSelect = (mun: Municipality) => {
    if (mun.lat && mun.lng) {
      setFocusCity({ lat: mun.lat, lng: mun.lng })
      setHighlightId(mun.id)
    }
  }

  const totalPop = municipalities.reduce((s, m) => s + (m.population || 0), 0)

  // Stats by region
  const regionStats = useMemo(() => {
    const stats: Record<string, number> = {}
    for (const m of municipalities) {
      stats[m.region] = (stats[m.region] || 0) + 1
    }
    return stats
  }, [municipalities])

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 4 }}>
        <div>
          <div className="page-title">Prefeitos e Municípios</div>
          <div className="page-subtitle">30 maiores municípios · Eleições 2024 · Mandato 2025–2028</div>
        </div>
        <button style={btnPrimary} onClick={() => setModal({ item: null })}>+ Nova Cidade</button>
      </div>

      {/* KPIs */}
      {!loading && (
        <div className="kpi-grid" style={{ marginBottom: 20 }}>
          <div className="card">
            <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 6 }}>MUNICÍPIOS</div>
            <div style={{ fontSize: 24, fontWeight: 700 }}>{municipalities.length}</div>
          </div>
          <div className="card">
            <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 6 }}>POPULAÇÃO TOTAL</div>
            <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--accent)' }}>
              {(totalPop / 1_000_000).toFixed(1)}M
            </div>
          </div>
          {Object.entries(regionStats).map(([region, count]) => (
            <div key={region} className="card">
              <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 6 }}>{region.toUpperCase()}</div>
              <div style={{ fontSize: 20, fontWeight: 700, color: REGION_COLORS[region] }}>{count}</div>
            </div>
          ))}
        </div>
      )}

      {/* Map */}
      {!loading && (
        <div className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: 20, borderRadius: 8 }}>
          <div style={{ height: 400, position: 'relative' }}>
            <MapContainer
              center={[-22.5, -48.5]}
              zoom={6}
              style={{ height: '100%', width: '100%', background: '#161b22' }}
              zoomControl={true}
            >
              <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://carto.com/">CARTO</a>'
              />
              {focusCity && <FlyTo lat={focusCity.lat} lng={focusCity.lng} />}
              {municipalities.filter(m => m.lat && m.lng).map(mun => {
                const color = REGION_COLORS[mun.region] ?? '#8b949e'
                const isHighlight = mun.id === highlightId
                const radius = mun.population
                  ? Math.max(6, Math.min(22, Math.sqrt(mun.population / 50000) * 4))
                  : 7

                return (
                  <CircleMarker
                    key={mun.id}
                    center={[mun.lat!, mun.lng!]}
                    radius={isHighlight ? radius + 4 : radius}
                    pathOptions={{
                      fillColor: isHighlight ? '#fff' : color,
                      color: isHighlight ? '#fff' : color,
                      fillOpacity: isHighlight ? 0.95 : 0.75,
                      weight: isHighlight ? 3 : 1.5,
                    }}
                    eventHandlers={{ click: () => setHighlightId(mun.id) }}
                  >
                    <Popup>
                      <div style={{ minWidth: 180 }}>
                        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>{mun.name}</div>
                        <div style={{
                          display: 'inline-block', padding: '2px 8px', borderRadius: 10,
                          fontSize: 10, fontWeight: 600, marginBottom: 8,
                          background: `${color}33`, color,
                        }}>
                          {mun.region}
                        </div>
                        {mun.population && (
                          <div style={{ fontSize: 12, marginBottom: 6 }}>
                            👥 {mun.population.toLocaleString('pt-BR')} hab.
                          </div>
                        )}
                        {mun.mayor && (
                          <>
                            <div style={{ fontSize: 12, fontWeight: 600 }}>
                              🏛 {mun.mayor.name}
                            </div>
                            <div style={{ fontSize: 11, color: '#666', marginTop: 2 }}>
                              {mun.mayor.party} · {mun.mayor.term_start}–{mun.mayor.term_end}
                            </div>
                          </>
                        )}
                      </div>
                    </Popup>
                  </CircleMarker>
                )
              })}
            </MapContainer>
          </div>
          <div style={{
            padding: '10px 16px', background: 'var(--bg2)',
            display: 'flex', gap: 20, flexWrap: 'wrap', fontSize: 11, color: 'var(--muted)',
          }}>
            <span style={{ fontWeight: 600 }}>Legenda:</span>
            {Object.entries(REGION_COLORS).map(([r, c]) => (
              <span key={r} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <span style={{ width: 10, height: 10, borderRadius: '50%', background: c, display: 'inline-block' }} />
                {r}
              </span>
            ))}
            <span style={{ marginLeft: 'auto' }}>Clique nos círculos para ver detalhes · Tamanho = população</span>
          </div>
        </div>
      )}

      {/* Filters */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 14 }}>
        <input
          className="search-input"
          placeholder="Buscar cidade ou prefeito..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ flex: '1', minWidth: 200, maxWidth: 320 }}
        />
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {REGIONS.map(r => (
            <button
              key={r}
              className={`filter-btn ${regionFilter === r ? 'active' : ''}`}
              onClick={() => setRegionFilter(r)}
              style={regionFilter === r && r !== 'Todos' ? {
                background: `${REGION_COLORS[r]}22`,
                borderColor: REGION_COLORS[r],
                color: REGION_COLORS[r],
              } : {}}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <div className="card" style={{ padding: 0 }}>
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="loading-skeleton" style={{ height: 52, margin: '2px 0' }} />
          ))}
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Município</th>
                  <th>Região</th>
                  <th>Prefeito(a)</th>
                  <th>Partido</th>
                  <th style={{ textAlign: 'right' }}>População</th>
                  <th style={{ width: 80 }}>Ações</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(mun => (
                  <tr
                    key={mun.id}
                    style={{ background: mun.id === highlightId ? 'rgba(88,166,255,0.07)' : undefined }}
                  >
                    <td onClick={() => handleSelect(mun)} style={{ cursor: 'pointer' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 8, height: 8, borderRadius: '50%', flexShrink: 0, background: REGION_COLORS[mun.region] ?? '#8b949e' }} />
                        <span style={{ fontWeight: 500 }}>{mun.name}</span>
                      </div>
                    </td>
                    <td><span style={{ fontSize: 12, color: REGION_COLORS[mun.region] ?? 'var(--muted)' }}>{mun.region}</span></td>
                    <td>{mun.mayor?.name || '—'}</td>
                    <td>
                      {mun.mayor && (
                        <span className="badge" style={{ background: `${partyColor(mun.mayor.party)}22`, color: partyColor(mun.mayor.party) }}>{mun.mayor.party}</span>
                      )}
                    </td>
                    <td style={{ textAlign: 'right', fontSize: 12 }}>{formatPop(mun.population)}</td>
                    <td>
                      <div style={{ display: 'flex', gap: 4 }}>
                        <button style={{ ...btnGhost, padding: '3px 7px', fontSize: 12 }} onClick={() => setModal({ item: mun })}>✏️</button>
                        <button style={{ ...btnDanger, padding: '3px 7px', fontSize: 12 }} onClick={() => setDeleting(mun)}>🗑️</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filtered.length === 0 && (
            <div className="empty-state">
              <div className="empty-state-icon">🔍</div>
              <div>Nenhum município encontrado.</div>
            </div>
          )}
        </div>
      )}

      {modal && <MunicipalityModal item={modal.item} onClose={() => setModal(null)} onSaved={handleSaved} />}
      {deleting && <DeleteConfirm name={deleting.name} onClose={() => setDeleting(null)} onConfirm={handleDeleteConfirm} />}
    </div>
  )
}
