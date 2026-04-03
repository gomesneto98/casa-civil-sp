export function fmt_currency(value: number): string {
  if (value >= 1_000_000_000) {
    return `R$ ${(value / 1_000_000_000).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} bi`
  }
  if (value >= 1_000_000) {
    return `R$ ${(value / 1_000_000).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} mi`
  }
  if (value >= 1_000) {
    return `R$ ${(value / 1_000).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })} mil`
  }
  return `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export const PARTY_COLORS: Record<string, string> = {
  PL: '#0066cc',
  PT: '#cc0000',
  PSDB: '#0055a5',
  PSOL: '#f5a623',
  PSD: '#1a5276',
  REPUBLICANOS: '#e67e22',
  UNIÃO: '#2ecc71',
  PP: '#8e44ad',
  PSB: '#f39c12',
  MDB: '#2980b9',
  PCdoB: '#c0392b',
  PODE: '#27ae60',
  NOVO: '#e74c3c',
  MISSÃO: '#16a085',
  CIDADANIA: '#d35400',
  AVANTE: '#2c3e50',
  REDE: '#00a65a',
  PSC: '#8b4513',
}

export function partyColor(party: string): string {
  return PARTY_COLORS[party] ?? '#8b949e'
}

export const PHOTO_BASE = 'https://www3.al.sp.gov.br/legis'
