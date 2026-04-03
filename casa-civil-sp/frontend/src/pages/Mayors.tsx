import { useEffect, useState } from 'react'
import axios from 'axios'
import { fmt_currency, partyColor } from '../utils'

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
  mayor: Mayor | null
}

interface Amendment {
  id: number
  year: number
  value: number
  description: string
  status: string
  deputy: { id: number; name: string; party: string }
  municipality: { id: number; name: string; region: string }
}

const REGION_COLORS: Record<string, string> = {
  'Grande SP': '#58a6ff',
  'Interior': '#3fb950',
  'Litoral': '#d29922',
  'Vale do Paraíba': '#f85149',
}

function MunicipalityModal({ mun, onClose }: { mun: Municipality; onClose: () => void }) {
  const [amendments, setAmendments] = useState<Amendment[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get<Amendment[]>(`/api/municipalities/${mun.id}/amendments`)
      .then(r => setAmendments(r.data))
      .finally(() => setLoading(false))
  }, [mun.id])

  const totalAmendments = amendments.reduce((s, a) => s + a.value, 0)

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" style={{ maxWidth: 720 }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div style={{ fontWeight: 700, fontSize: 18, marginBottom: 4 }}>{mun.name}</div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <span className="badge" style={{
                background: `${REGION_COLORS[mun.region] ?? '#8b949e'}22`,
                color: REGION_COLORS[mun.region] ?? '#8b949e',
              }}>
                {mun.region}
              </span>
              {mun.population && (
                <span style={{ fontSize: 12, color: 'var(--muted)' }}>
                  {mun.population.toLocaleString('pt-BR')} hab.
                </span>
              )}
            </div>
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        {/* Mayor info */}
        {mun.mayor && (
          <div style={{
            background: 'var(--bg3)', borderRadius: 8, padding: '12px 14px',
            marginBottom: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }}>
            <div>
              <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 4 }}>Prefeito(a)</div>
              <div style={{ fontWeight: 600, fontSize: 14 }}>{mun.mayor.name}</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span className="badge" style={{
                background: `${partyColor(mun.mayor.party)}22`,
                color: partyColor(mun.mayor.party),
              }}>
                {mun.mayor.party}
              </span>
              <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 4 }}>
                {mun.mayor.term_start}–{mun.mayor.term_end}
              </div>
            </div>
          </div>
        )}

        {/* Amendments */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Emendas Recebidas ({amendments.length})
          </div>
          {totalAmendments > 0 && (
            <div style={{ fontSize: 13, color: 'var(--green)', fontWeight: 600 }}>
              {fmt_currency(totalAmendments)}
            </div>
          )}
        </div>

        {loading ? (
          <div style={{ color: 'var(--muted)', fontSize: 13 }}>Carregando...</div>
        ) : amendments.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📋</div>
            <div>Nenhuma emenda registrada para este município.</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {amendments.map(am => (
              <div key={am.id} style={{
                background: 'var(--bg3)', borderRadius: 6, padding: '10px 12px',
                border: '1px solid var(--border)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, marginBottom: 4 }}>
                  <div style={{ fontWeight: 500, fontSize: 13 }}>{am.description}</div>
                  <div style={{ fontWeight: 600, color: 'var(--green)', fontSize: 13, flexShrink: 0 }}>
                    {fmt_currency(am.value)}
                  </div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontSize: 11, color: 'var(--muted)' }}>
                    Dep. {am.deputy.name}
                    <span className="badge" style={{
                      marginLeft: 6,
                      background: `${partyColor(am.deputy.party)}22`,
                      color: partyColor(am.deputy.party),
                    }}>
                      {am.deputy.party}
                    </span>
                    <span style={{ marginLeft: 8 }}>· {am.year}</span>
                  </div>
                  <span className={`badge badge-${am.status}`}>{am.status}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default function Mayors() {
  const [municipalities, setMunicipalities] = useState<Municipality[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<Municipality | null>(null)
  const [regionFilter, setRegionFilter] = useState('Todos')

  const regions = ['Todos', 'Grande SP', 'Interior', 'Litoral', 'Vale do Paraíba']

  useEffect(() => {
    axios.get<Municipality[]>('/api/municipalities')
      .then(r => setMunicipalities(r.data))
      .finally(() => setLoading(false))
  }, [])

  const filtered = regionFilter === 'Todos'
    ? municipalities
    : municipalities.filter(m => m.region === regionFilter)

  return (
    <div>
      <div className="page-title">Prefeitos e Municípios</div>
      <div className="page-subtitle">Visão orçamentária por município</div>

      {/* Region filters */}
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 20 }}>
        {regions.map(r => (
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

      {loading ? (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="loading-skeleton" style={{ height: 52, margin: '2px 0' }} />
          ))}
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Município</th>
                <th>Região</th>
                <th>População</th>
                <th>Prefeito(a)</th>
                <th>Partido</th>
                <th>Mandato</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(m => (
                <tr key={m.id} onClick={() => setSelected(m)}>
                  <td style={{ fontWeight: 500 }}>{m.name}</td>
                  <td>
                    <span className="badge" style={{
                      background: `${REGION_COLORS[m.region] ?? '#8b949e'}22`,
                      color: REGION_COLORS[m.region] ?? '#8b949e',
                    }}>
                      {m.region}
                    </span>
                  </td>
                  <td style={{ color: 'var(--muted)' }}>
                    {m.population ? m.population.toLocaleString('pt-BR') : '—'}
                  </td>
                  <td>{m.mayor?.name ?? '—'}</td>
                  <td>
                    {m.mayor && (
                      <span className="badge" style={{
                        background: `${partyColor(m.mayor.party)}22`,
                        color: partyColor(m.mayor.party),
                      }}>
                        {m.mayor.party}
                      </span>
                    )}
                  </td>
                  <td style={{ color: 'var(--muted)', fontSize: 12 }}>
                    {m.mayor ? `${m.mayor.term_start}–${m.mayor.term_end}` : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selected && (
        <MunicipalityModal mun={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  )
}
