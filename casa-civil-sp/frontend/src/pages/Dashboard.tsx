import { useEffect, useState } from 'react'
import axios from 'axios'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import KPICard from '../components/KPICard'
import { fmt_currency, partyColor } from '../utils'

interface Summary {
  total_deputies: number
  total_municipalities: number
  total_secretariats: number
  total_programs: number
  total_amendments_value: number
  total_budget_2025: number
  amendments_by_status: Record<string, number>
  budget_by_secretariat: { name: string; acronym: string; total: number }[]
  amendments_by_party: { party: string; total: number }[]
}

const STATUS_COLORS: Record<string, string> = {
  aprovada: '#3fb950',
  pendente: '#d29922',
  executada: '#58a6ff',
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: '#161b22',
        border: '1px solid #30363d',
        borderRadius: 6,
        padding: '8px 12px',
        fontSize: 12,
      }}>
        <div style={{ color: '#8b949e', marginBottom: 4 }}>{label}</div>
        {payload.map((p: any, i: number) => (
          <div key={i} style={{ color: p.color || '#e6edf3' }}>
            {fmt_currency(p.value)}
          </div>
        ))}
      </div>
    )
  }
  return null
}

export default function Dashboard() {
  const [data, setData] = useState<Summary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    axios.get<Summary>('/api/dashboard/summary')
      .then(r => setData(r.data))
      .catch(() => setError('Erro ao carregar dados do painel.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div>
        <div className="page-title">Dashboard</div>
        <div className="page-subtitle">Carregando dados...</div>
        <div className="kpi-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="loading-skeleton" style={{ height: 96 }} />
          ))}
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div>
        <div className="page-title">Dashboard</div>
        <div className="card" style={{ color: 'var(--red)', marginTop: 16 }}>{error || 'Sem dados.'}</div>
      </div>
    )
  }

  const pieData = Object.entries(data.amendments_by_status).map(([name, value]) => ({ name, value }))

  const partyData = data.amendments_by_party.map(d => ({
    party: d.party,
    total: d.total,
  }))

  return (
    <div>
      <div className="page-title">Dashboard</div>
      <div className="page-subtitle">Visão geral do Centro de Governo — Estado de São Paulo</div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <KPICard
          title="Deputados"
          value={data.total_deputies}
          subtitle="ALESP — 35ª Legislatura"
          color="var(--accent)"
          icon="🏛️"
        />
        <KPICard
          title="Municípios"
          value={data.total_municipalities}
          subtitle="Municípios monitorados"
          color="var(--green)"
          icon="🏙️"
        />
        <KPICard
          title="Secretarias"
          value={data.total_secretariats}
          subtitle="Pastas do governo"
          color="var(--orange)"
          icon="📁"
        />
        <KPICard
          title="Programas"
          value={data.total_programs}
          subtitle="Programas ativos e concluídos"
          color="#8e44ad"
          icon="📋"
        />
        <KPICard
          title="Valor Emendas"
          value={fmt_currency(data.total_amendments_value)}
          subtitle="Total de emendas parlamentares"
          color="var(--green)"
          icon="💰"
        />
        <KPICard
          title="Orçamento 2025"
          value={fmt_currency(data.total_budget_2025)}
          subtitle="Dotação autorizada 2025"
          color="var(--accent)"
          icon="📊"
        />
      </div>

      {/* Charts row 1 */}
      <div className="charts-grid-3">
        <div className="chart-card">
          <div className="chart-card-title">Orçamento por Secretaria (Top 5)</div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data.budget_by_secretariat} layout="vertical" margin={{ left: 0, right: 20, top: 0, bottom: 0 }}>
              <XAxis type="number" hide />
              <YAxis type="category" dataKey="acronym" tick={{ fill: '#8b949e', fontSize: 11 }} width={55} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="total" fill="#58a6ff" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <div className="chart-card-title">Emendas por Status</div>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={90}
                paddingAngle={3}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={index} fill={STATUS_COLORS[entry.name] ?? '#8b949e'} />
                ))}
              </Pie>
              <Legend
                formatter={(value) => <span style={{ color: '#8b949e', fontSize: 12 }}>{value}</span>}
              />
              <Tooltip
                formatter={(value: number, name: string) => [value, name]}
                contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 6, fontSize: 12 }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts row 2 */}
      <div className="chart-card" style={{ marginBottom: 24 }}>
        <div className="chart-card-title">Emendas por Partido (Top 10 — Valor Total)</div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={partyData} margin={{ left: 10, right: 10, top: 0, bottom: 0 }}>
            <XAxis dataKey="party" tick={{ fill: '#8b949e', fontSize: 11 }} />
            <YAxis hide />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="total" radius={[4, 4, 0, 0]}>
              {partyData.map((entry, index) => (
                <Cell key={index} fill={partyColor(entry.party)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
