# CLAUDE.md — Casa Civil SP

Este arquivo descreve o projeto e orienta ferramentas de IA (como Claude) sobre sua estrutura, comandos e convenções.

## Visão Geral

Dashboard de Centro de Governo para a **Casa Civil do Estado de São Paulo**. A aplicação consolida informações sobre:

- **Deputados estaduais (ALESP)** — votação 2022, emendas, partido
- **Municípios e Prefeitos** — regiões, partido, mandato
- **Secretarias do Estado** — orçamento, dotação, liquidação
- **Programas de Governo** — orçamento total, vigência, secretaria responsável

O projeto também inclui um dashboard standalone (`alesp_dashboard.html`) para análise rápida da ALESP, sem dependência de servidor.

## Estrutura

```
cc/
├── alesp_dashboard.html          # Dashboard standalone ALESP (HTML puro)
├── casa-civil-sp/
│   ├── docker-compose.yml        # Orquestração dos serviços
│   ├── backend/                  # API FastAPI + PostgreSQL
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── start.sh              # Entrypoint: seed + uvicorn
│   │   └── app/
│   │       ├── main.py           # App FastAPI, CORS, routers
│   │       ├── database.py       # SQLAlchemy engine + sessão
│   │       ├── models.py         # ORM: Deputy, Municipality, Mayor, Amendment, Secretariat, BudgetItem, Program
│   │       ├── schemas.py        # Pydantic schemas
│   │       ├── seed.py           # Seed idempotente do banco
│   │       └── routers/
│   │           ├── dashboard.py  # GET /api/dashboard/summary
│   │           ├── deputies.py   # GET /api/deputies
│   │           ├── municipalities.py
│   │           ├── secretariats.py
│   │           └── programs.py
│   └── frontend/                 # React 18 + Vite + TypeScript
│       ├── Dockerfile
│       ├── package.json
│       └── src/
│           ├── App.tsx           # Roteamento principal
│           ├── utils.ts          # Helpers (fmt_currency, partyColor)
│           ├── components/
│           │   ├── KPICard.tsx
│           │   └── Sidebar.tsx
│           └── pages/
│               ├── Dashboard.tsx
│               ├── Deputies.tsx
│               ├── Secretariats.tsx
│               ├── Mayors.tsx
│               └── Programs.tsx
```

## Stack Tecnológica

| Camada     | Tecnologia                                      |
|------------|-------------------------------------------------|
| Backend    | Python 3.12, FastAPI 0.111, SQLAlchemy 2.0      |
| Banco      | PostgreSQL 15                                   |
| Frontend   | React 18, TypeScript 5, Vite 5, Recharts, Axios |
| Infra      | Docker Compose                                  |

## Pré-requisitos

- Docker e Docker Compose
- (Opcional) Python 3.12+ e Node 20+ para desenvolvimento local

## Como Rodar

### Com Docker (recomendado)

```bash
cd casa-civil-sp

# Copie e ajuste as variáveis de ambiente
cp .env.example .env   # ou crie o .env conforme abaixo

# Suba todos os serviços (postgres + backend + frontend)
docker compose up --build
```

Serviços disponíveis após subir:

| Serviço  | URL                            |
|----------|--------------------------------|
| Frontend | http://localhost:3000          |
| API      | http://localhost:8000          |
| API Docs | http://localhost:8000/docs     |
| Health   | http://localhost:8000/api/health |

### Variáveis de Ambiente (`.env`)

```env
POSTGRES_DB=casacivil
POSTGRES_USER=casacivil
POSTGRES_PASSWORD=casacivil123
DATABASE_URL=postgresql://casacivil:casacivil123@postgres:5432/casacivil
```

### Desenvolvimento Local (sem Docker)

**Backend:**
```bash
cd casa-civil-sp/backend
pip install -r requirements.txt
export DATABASE_URL=postgresql://casacivil:casacivil123@localhost:5432/casacivil
python app/seed.py
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd casa-civil-sp/frontend
npm install
npm run dev
```

## Banco de Dados

O seed (`app/seed.py`) é **idempotente** — verifica existência de dados antes de inserir. É executado automaticamente no `start.sh` do container backend.

### Modelos principais

- `Deputy` — deputados estaduais (nome, partido, votos 2022, foto)
- `Municipality` + `Mayor` — municípios e prefeitos
- `Amendment` — emendas parlamentares por deputado/município/ano
- `Secretariat` — secretarias do estado
- `BudgetItem` — itens orçamentários (dotação, empenhado, liquidado, pago)
- `Program` — programas de governo

## Rotas da API

| Método | Rota                        | Descrição                          |
|--------|-----------------------------|------------------------------------|
| GET    | `/api/health`               | Health check                       |
| GET    | `/api/dashboard/summary`    | KPIs e gráficos do dashboard       |
| GET    | `/api/deputies`             | Lista de deputados                 |
| GET    | `/api/municipalities`       | Lista de municípios                |
| GET    | `/api/secretariats`         | Lista de secretarias               |
| GET    | `/api/programs`             | Lista de programas                 |

Documentação interativa: `http://localhost:8000/docs`

## Convenções de Código

- **Python**: snake_case, tipagem explícita nos schemas Pydantic, dependências via `Depends(get_db)`
- **TypeScript/React**: componentes funcionais com hooks, interfaces explícitas para dados da API
- **Commits**: mensagens em português descrevendo a mudança
- **Sem testes automatizados** no momento — validação manual via `/docs` e UI

## Dashboard Standalone

`alesp_dashboard.html` é um arquivo HTML auto-contido (CSS e JS inline) para análise dos deputados da ALESP. Não requer servidor — abrir diretamente no navegador.
