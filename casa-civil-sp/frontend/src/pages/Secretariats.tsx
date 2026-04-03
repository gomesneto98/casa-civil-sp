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
      <span style={{
        display: 'inline-block', padding: '2px 8px', borderRadius: 12,
        fontSize: 10, fontWeight: 600, background: 'rgba(139,148,158,0.15)',
        color: '#8b949e', letterSpacing: '0.3px',
      }}>
        sem partido
      </span>
    )
  }
  const color = partyColor(party)
  return (
    <span style={{
      display: 'inline-block', padding: '2px 8px', borderRadius: 12,
      fontSize: 10, fontWeight: 600, letterSpacing: '0.3px',
      background: `${color}22`, color, border: `1px solid ${color}44`,
    }}>
      {party}
    </span>
  )
}

export default function Secretariats() {
  const [secretariats, setSecretariats] = useState<SecretariatItem[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

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

  return (
    <div>
      <div className="page-title">Secretarias de Estado</div>
      <div className="page-subtitle">
        Governo Tarcísio de Freitas · {secretariats.length} secretarias
      </div>

      {/* Search */}
      <div style={{ marginBottom: 20 }}>
        <input
          className="search-input"
          style={{ width: '100%', maxWidth: 400 }}
          placeholder="Buscar secretaria ou secretário..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="sec-grid">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="loading-skeleton" style={{ height: 200 }} />
          ))}
        </div>
      ) : (
        <div className="sec-grid">
          {filtered.map(sec => {
            const executives = parseExecutives(sec.executives)
            return (
              <div key={sec.id} className="card sec-card">
                {/* Emoji + acronym */}
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
                  <div style={{
                    fontSize: 36, lineHeight: 1,
                    width: 52, height: 52,
                    background: 'var(--bg3)', borderRadius: 12,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    flexShrink: 0,
                  }}>
                    {sec.emoji || '🏛️'}
                  </div>
                  <span style={{
                    fontSize: 10, fontWeight: 700, letterSpacing: '1px',
                    color: 'var(--accent)', background: 'rgba(88,166,255,0.1)',
                    padding: '3px 8px', borderRadius: 8,
                  }}>
                    {sec.acronym}
                  </span>
                </div>

                {/* Name */}
                <div style={{ fontWeight: 700, fontSize: 15, lineHeight: 1.3, marginBottom: 14, color: 'var(--text)' }}>
                  {sec.name}
                </div>

                {/* Secretary */}
                <div style={{ borderTop: '1px solid var(--border)', paddingTop: 12, marginBottom: 12 }}>
                  <div style={{ fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 6 }}>
                    SECRETÁRIO(A)
                  </div>
                  <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 6 }}>
                    {sec.secretary_name || '—'}
                  </div>
                  <PartyBadge party={sec.party} />
                </div>

                {/* Executives */}
                {executives.length > 0 && (
                  <div style={{ borderTop: '1px solid var(--border)', paddingTop: 12 }}>
                    <div style={{ fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>
                      SECRETÁRIOS(AS) EXECUTIVOS(AS)
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                      {executives.map((exec, i) => (
                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
                          <div style={{ fontSize: 12, color: 'var(--text)', flex: 1, minWidth: 0 }}>
                            {exec.name}
                          </div>
                          <PartyBadge party={exec.party} />
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Metas vinculadas */}
                {sec.meta_count > 0 && (
                  <div style={{ borderTop: '1px solid var(--border)', paddingTop: 12, marginTop: 12 }}>
                    <div style={{ fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>
                      METAS VINCULADAS ({sec.meta_count})
                    </div>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      {Object.entries(sec.meta_by_status).map(([status, count]) => {
                        const color = STATUS_COLORS[status] || '#8b949e'
                        return (
                          <span key={status} style={{
                            fontSize: 11, padding: '2px 8px', borderRadius: 10,
                            background: `${color}20`, color,
                            border: `1px solid ${color}44`, whiteSpace: 'nowrap',
                          }}>
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
        <div className="empty-state">
          <div className="empty-state-icon">🔍</div>
          <div>Nenhuma secretaria encontrada.</div>
        </div>
      )}
    </div>
  )
}
