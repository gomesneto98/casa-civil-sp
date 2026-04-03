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

  useEffect(() => {
    axios.get<Municipality[]>('/api/municipalities')
      .then(r => setMunicipalities(r.data))
      .finally(() => setLoading(false))
  }, [])

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
      <div className="page-title">Prefeitos e Municípios</div>
      <div className="page-subtitle">
        30 maiores municípios · Eleições 2024 · Mandato 2025–2028
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
                </tr>
              </thead>
              <tbody>
                {filtered.map(mun => (
                  <tr
                    key={mun.id}
                    onClick={() => handleSelect(mun)}
                    style={{ background: mun.id === highlightId ? 'rgba(88,166,255,0.07)' : undefined }}
                  >
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span
                          style={{
                            width: 8, height: 8, borderRadius: '50%', flexShrink: 0,
                            background: REGION_COLORS[mun.region] ?? '#8b949e',
                          }}
                        />
                        <span style={{ fontWeight: 500 }}>{mun.name}</span>
                      </div>
                    </td>
                    <td>
                      <span style={{ fontSize: 12, color: REGION_COLORS[mun.region] ?? 'var(--muted)' }}>
                        {mun.region}
                      </span>
                    </td>
                    <td>{mun.mayor?.name || '—'}</td>
                    <td>
                      {mun.mayor && (
                        <span className="badge" style={{
                          background: `${partyColor(mun.mayor.party)}22`,
                          color: partyColor(mun.mayor.party),
                        }}>
                          {mun.mayor.party}
                        </span>
                      )}
                    </td>
                    <td style={{ textAlign: 'right', fontSize: 12 }}>
                      {formatPop(mun.population)}
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
    </div>
  )
}
