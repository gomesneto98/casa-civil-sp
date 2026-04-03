# CIG — Centro Integrado de Governo SP

Dashboard de Centro de Governo para o **Estado de São Paulo**, desenvolvido para a Casa Civil. Consolida informações sobre deputados estaduais (ALESP), municípios, prefeitos, secretarias e programas de governo.

## 🖥️ Acesso

> **Deploy:** Railway/Render — veja instruções abaixo

## 📦 Stack

| Camada | Tecnologia |
|--------|------------|
| Backend | Python 3.11 · FastAPI · SQLAlchemy |
| Banco | PostgreSQL 15 |
| Frontend | React 18 · TypeScript · Vite · Recharts · Leaflet |
| Infra | Docker Compose · Nginx |

## 🚀 Como Rodar Localmente

```bash
cd casa-civil-sp
cp .env.example .env
docker compose -f docker-compose.dev.yml up --build
```

Serviços:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## ☁️ Deploy (Railway)

1. Crie conta em [railway.app](https://railway.app)
2. Clique **New Project → Deploy from GitHub repo**
3. Adicione serviço PostgreSQL no projeto
4. Configure as variáveis de ambiente:
   ```
   POSTGRES_DB=casacivil
   POSTGRES_USER=casacivil
   POSTGRES_PASSWORD=<sua_senha>
   DATABASE_URL=postgresql://casacivil:<senha>@<host>:5432/casacivil
   ```
5. Deploy do backend e frontend como serviços separados

## ☁️ Deploy (Render)

1. Crie conta em [render.com](https://render.com)
2. New → PostgreSQL (Free)
3. New → Web Service → conecte este repositório → selecione `casa-civil-sp/backend`
4. New → Static Site → `casa-civil-sp/frontend` → Build: `npm ci && npm run build`, Publish: `dist`

## 📋 Dados

- **Deputados**: 35ª Legislatura ALESP (2023–2027) — 94+ deputados
- **Secretarias**: Governo Tarcísio de Freitas — 20 secretarias de Estado
- **Prefeitos**: 30 maiores municípios, eleições outubro 2024, mandato 2025–2028
- **Mapa**: Mapa interativo do Estado com marcadores por cidade

## 🗂️ Estrutura

```
casa-civil-sp/
├── backend/          # FastAPI + PostgreSQL
├── frontend/         # React + Vite + Leaflet
├── docker-compose.yml          # Produção
└── docker-compose.dev.yml      # Desenvolvimento local
```
