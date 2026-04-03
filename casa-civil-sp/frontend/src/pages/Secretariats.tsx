import { useEffect, useState } from 'react'
import axios from 'axios'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, Legend,
} from 'recharts'
import { fmt_currency } from '../utils'

interface SecretariatItem {
  id: number
  name: string
  acronym: string
  secretary_name: string | null
  total_budget: number
}

interface BudgetItem {
  id: number
  year: number
  category: string
  value: number
  description: string | null
}

interface SecretariatDetail {
  id: number
  name: string
  acronym: string
  secretary_name: string | null
  budget_items: BudgetItem[]
}

const CATEGORY_COLORS: Record<string, string> = {
  dotacao: '#58a6ff',
  empenhado: '#3fb950',
  liquidado: '#d29922',
  pago: '#f85149',
}

const CATEGORY_LABELS: Record<string, string> = {
  dotacao: 'Dotação',
  empenhado: 'Empenhado',
  liquidado: 'Liquidado',
  pago: 'Pago',
}

function buildChartData(items: BudgetItem[]) {
  const byYear: Record<number, Record<string, number>> = {}
  for (const item of items) {
    if (!byYear[item.year]) byYear[item.year] = {}
    byYear[item.year][item.category] = item.value
  }
  return Object.entries(byYear)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([year, cats]) => ({ year, ...cats }))
}

function SecretariatModal({ sec, onClose }: { sec: SecretariatDetail; onClose: () => void }) {
  const chartData = buildChartData(sec.budget_items)

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" style={{ maxWidth: 780 }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div style={{ fontSize: 11, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 4 }}>
              {sec.acronym}
            </div>
            <div style={{ fontWeight: 700, fontSize: 17, marginBottom: 4 }}>{sec.name}</div>
            {sec.secretary_name && (
              <div style={{ fontSize: 13, color: 'var(--muted)' }}>Secretário(a): {sec.secretary_name}</div>
            )}
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="chart-card-title" style={{ marginBottom: 16 }}>Execução Orçamentária por Ano</div>

        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={chartData} margin={{ left: 10, right: 10, top: 0, bottom: 0 }}>
              <XAxis dataKey="year" tick={{ fill: '#8b949e', fontSize: 12 }} />
              <YAxis hide />
              <Tooltip
                formatter={(value: number, name: string) => [fmt_currency(value), CATEGORY_LABELS[name] ?? name]}
                contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 6, fontSize: 12 }}
              />
              <Legend
                formatter={value => <span style={{ color: '#8b949e', fontSize: 12 }}>{CATEGORY_LABELS[value] ?? value}</span>}
              />
              {Object.keys(CATEGORY_COLORS).map(cat => (
                <Bar key={cat} dataKey={cat} fill={CATEGORY_COLORS[cat]} radius={[3, 3, 0, 0]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">📊</div>
            <div>Sem dados orçamentários disponíveis.</div>
          </div>
        )}
      </div>
    </div>
  )
}

export default function Secretariats() {
  const [secretariats, setSecretariats] = useState<SecretariatItem[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<SecretariatDetail | null>(null)

  useEffect(() => {
    axios.get<SecretariatItem[]>('/api/secretariats')
      .then(r => setSecretariats(r.data))
      .finally(() => setLoading(false))
  }, [])

  const handleSelect = async (id: number) => {
    const r = await axios.get<SecretariatDetail>(`/api/secretariats/${id}`)
    setSelected(r.data)
  }

  const sorted = [...secretariats].sort((a, b) => b.total_budget - a.total_budget)

  return (
    <div>
      <div className="page-title">Secretarias de Estado</div>
      <div className="page-subtitle">Pastas do governo paulista — execução orçamentária</div>

      {loading ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 14 }}>
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="loading-skeleton" style={{ height: 110 }} />
          ))}
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 14 }}>
          {sorted.map((sec, idx) => (
            <div
              key={sec.id}
              className="card"
              onClick={() => handleSelect(sec.id)}
              style={{ cursor: 'pointer', position: 'relative', overflow: 'hidden' }}
              onMouseEnter={e => (e.currentTarget.style.borderColor = 'var(--accent)')}
              onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--border)')}
            >
              {/* Rank */}
              <div style={{
                position: 'absolute', top: 12, right: 12,
                fontSize: 11, color: 'var(--muted)',
                background: 'var(--bg3)', padding: '2px 6px', borderRadius: 10,
              }}>
                #{idx + 1}
              </div>

              <div style={{ fontSize: 11, color: 'var(--accent)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px', marginBottom: 6 }}>
                {sec.acronym}
              </div>
              <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4, paddingRight: 36, lineHeight: 1.3 }}>
                {sec.name}
              </div>
              {sec.secretary_name && (
                <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 12 }}>
                  {sec.secretary_name}
                </div>
              )}

              <div style={{ borderTop: '1px solid var(--border)', paddingTop: 10 }}>
                <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 2 }}>Dotação Total</div>
                <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--accent)' }}>
                  {fmt_currency(sec.total_budget)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {selected && (
        <SecretariatModal sec={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  )
}
