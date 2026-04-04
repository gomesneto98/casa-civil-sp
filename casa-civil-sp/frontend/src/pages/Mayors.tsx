import { useEffect, useState, useMemo, useCallback, useRef } from 'react'
import axios from 'axios'
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet'
import type { GeoJsonObject, FeatureCollection, Feature } from 'geojson'
import type L from 'leaflet'
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

// Choropleth color scale by population (Censo 2022)
function getPopColor(pop: number | null | undefined): string {
  if (!pop) return '#2d333b'
  if (pop >= 1_000_000) return '#1e3a8a'
  if (pop >= 500_000) return '#1d4ed8'
  if (pop >= 200_000) return '#2563eb'
  if (pop >= 100_000) return '#3b82f6'
  if (pop >= 50_000) return '#60a5fa'
  if (pop >= 20_000) return '#93c5fd'
  if (pop >= 10_000) return '#bfdbfe'
  return '#dbeafe'
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
  const [highlightId, setHighlightId] = useState<number | null>(null)
  const [modal, setModal] = useState<{ item: Municipality | null } | null>(null)
  const [deleting, setDeleting] = useState<Municipality | null>(null)

  // Choropleth map state
  const [geoJson, setGeoJson] = useState<FeatureCollection | null>(null)
  const [codeToName, setCodeToName] = useState<Record<string, string>>({})
  const [munByName, setMunByName] = useState<Record<string, Municipality>>({})
  const [selectedMun, setSelectedMun] = useState<Municipality | null>(null)
  const selectedLayerRef = useRef<L.Path | null>(null)
  const geoLayerRef = useRef<L.GeoJSON | null>(null)

  useEffect(() => {
    Promise.all([
      axios.get<Municipality[]>('/api/municipalities'),
      fetch('https://servicodados.ibge.gov.br/api/v2/malhas/35?resolucao=5&formato=application/vnd.geo+json').then(r => r.json()),
      fetch('https://servicodados.ibge.gov.br/api/v1/localidades/estados/35/municipios').then(r => r.json()),
    ]).then(([munRes, geo, ibgeMuns]) => {
      const muns: Municipality[] = munRes.data
      setMunicipalities(muns)

      const byName: Record<string, Municipality> = {}
      muns.forEach(m => { byName[m.name] = m })
      setMunByName(byName)

      const c2n: Record<string, string> = {}
      ;(ibgeMuns as { id: number; nome: string }[]).forEach(m => { c2n[String(m.id)] = m.nome })
      setCodeToName(c2n)

      setGeoJson(geo as FeatureCollection)
      setLoading(false)
    }).catch(() => {
      axios.get<Municipality[]>('/api/municipalities')
        .then(r => setMunicipalities(r.data))
        .finally(() => setLoading(false))
    })
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
    setSelectedMun(mun)
    setHighlightId(mun.id)
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

  // GeoJSON choropleth callbacks
  const geoStyle = useCallback((feature?: Feature) => {
    const code = (feature?.properties as Record<string, string>)?.codarea
    const name = codeToName[code]
    const mun = name ? munByName[name] : undefined
    return {
      fillColor: getPopColor(mun?.population),
      fillOpacity: 0.8,
      color: '#0d1117',
      weight: 0.5,
    }
  }, [codeToName, munByName])

  const onEachFeature = useCallback((feature: Feature, layer: import('leaflet').Layer) => {
    const code = (feature?.properties as Record<string, string>)?.codarea
    const name = codeToName[code]
    const mun = name ? munByName[name] : undefined
    if (name) {
      ;(layer as import('leaflet').Path).bindTooltip(name, { sticky: true })
    }
    layer.on({
      click: () => {
        if (selectedLayerRef.current && geoLayerRef.current) {
          geoLayerRef.current.resetStyle(selectedLayerRef.current)
        }
        ;(layer as import('leaflet').Path).setStyle({ color: '#ffffff', weight: 2, fillOpacity: 1 })
        selectedLayerRef.current = layer as import('leaflet').Path
        setSelectedMun(mun ?? null)
        setHighlightId(mun?.id ?? null)
      },
      mouseover: (e: import('leaflet').LeafletMouseEvent) => {
        if (layer !== selectedLayerRef.current) {
          ;(e.target as import('leaflet').Path).setStyle({ fillOpacity: 0.95 })
        }
      },
      mouseout: (e: import('leaflet').LeafletMouseEvent) => {
        if (layer !== selectedLayerRef.current) {
          ;(e.target as import('leaflet').Path).setStyle({ fillOpacity: 0.8 })
        }
      },
    })
  }, [codeToName, munByName])

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 4 }}>
        <div>
          <div className="page-title">Prefeitos e Municípios</div>
          <div className="page-subtitle">645 municípios · Censo 2022 · Eleições 2024</div>
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
          <div style={{ display: 'flex', height: 460, position: 'relative' }}>
            {/* Choropleth */}
            <div style={{ flex: 1, position: 'relative' }}>
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
                {geoJson && (
                  <GeoJSON
                    key={Object.keys(munByName).length}
                    data={geoJson as GeoJsonObject}
                    style={geoStyle}
                    onEachFeature={onEachFeature}
                    ref={(r: import('leaflet').GeoJSON | null) => { geoLayerRef.current = r }}
                  />
                )}
              </MapContainer>
              {!geoJson && (
                <div style={{
                  position: 'absolute', inset: 0, display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                  color: 'var(--muted)', fontSize: 13,
                }}>Carregando mapa…</div>
              )}
            </div>

            {/* Info panel — selected municipality */}
            <div style={{
              width: 220, background: 'var(--bg2)', borderLeft: '1px solid var(--border)',
              display: 'flex', flexDirection: 'column', overflow: 'hidden',
            }}>
              {selectedMun ? (
                <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 10 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <span style={{ fontWeight: 700, fontSize: 14, lineHeight: 1.3 }}>{selectedMun.name}</span>
                    <button
                      onClick={() => { setSelectedMun(null); if (geoLayerRef.current && selectedLayerRef.current) { geoLayerRef.current.resetStyle(selectedLayerRef.current); selectedLayerRef.current = null } }}
                      style={{ background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer', fontSize: 14, padding: 0 }}
                    >✕</button>
                  </div>
                  <span style={{
                    display: 'inline-block', padding: '2px 8px', borderRadius: 10,
                    fontSize: 10, fontWeight: 600, width: 'fit-content',
                    background: `${REGION_COLORS[selectedMun.region] ?? '#8b949e'}22`,
                    color: REGION_COLORS[selectedMun.region] ?? '#8b949e',
                  }}>
                    {selectedMun.region}
                  </span>
                  <div style={{ borderTop: '1px solid var(--border)', paddingTop: 10, display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div>
                      <div style={{ fontSize: 10, color: 'var(--muted)', marginBottom: 3 }}>POPULAÇÃO (Censo 2022)</div>
                      <div style={{ fontSize: 18, fontWeight: 700, color: getPopColor(selectedMun.population) }}>
                        {selectedMun.population ? selectedMun.population.toLocaleString('pt-BR') : '—'}
                      </div>
                      <div style={{ fontSize: 10, color: 'var(--muted)' }}>habitantes</div>
                    </div>
                  </div>
                  {selectedMun.mayor ? (
                    <div style={{ borderTop: '1px solid var(--border)', paddingTop: 10 }}>
                      <div style={{ fontSize: 10, color: 'var(--muted)', marginBottom: 5 }}>PREFEITO(A)</div>
                      <div style={{ fontWeight: 600, fontSize: 13 }}>{selectedMun.mayor.name}</div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
                        <span className="badge" style={{ background: `${partyColor(selectedMun.mayor.party)}22`, color: partyColor(selectedMun.mayor.party) }}>
                          {selectedMun.mayor.party}
                        </span>
                        <span style={{ fontSize: 11, color: 'var(--muted)' }}>
                          {selectedMun.mayor.term_start}–{selectedMun.mayor.term_end}
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div style={{ borderTop: '1px solid var(--border)', paddingTop: 10, color: 'var(--muted)', fontSize: 12 }}>
                      Prefeito não cadastrado
                    </div>
                  )}
                  <button style={{ ...btnGhost, fontSize: 11, marginTop: 4 }} onClick={() => setModal({ item: selectedMun })}>
                    ✏️ Editar
                  </button>
                </div>
              ) : (
                <div style={{ padding: 16, color: 'var(--muted)', fontSize: 12, textAlign: 'center', paddingTop: 40 }}>
                  <div style={{ fontSize: 28, marginBottom: 8 }}>🗺️</div>
                  <div>Clique em um município no mapa para ver os detalhes</div>
                </div>
              )}
            </div>
          </div>

          {/* Legend */}
          <div style={{
            padding: '10px 16px', background: 'var(--bg2)', borderTop: '1px solid var(--border)',
            display: 'flex', gap: 6, flexWrap: 'wrap', fontSize: 11, color: 'var(--muted)', alignItems: 'center',
          }}>
            <span style={{ fontWeight: 600, marginRight: 4 }}>População (Censo 2022):</span>
            {[
              { label: '< 10 mil', color: '#dbeafe' },
              { label: '10–50 mil', color: '#93c5fd' },
              { label: '50–200 mil', color: '#60a5fa' },
              { label: '200 mil–1M', color: '#3b82f6' },
              { label: '> 1M', color: '#1e3a8a' },
              { label: 'Sem dado', color: '#2d333b' },
            ].map(({ label, color }) => (
              <span key={label} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ width: 12, height: 12, background: color, display: 'inline-block', borderRadius: 2 }} />
                {label}
              </span>
            ))}
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
