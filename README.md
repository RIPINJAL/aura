# AURA

AURA is a production-oriented personal operations platform that coordinates specialized AI agents for research, career planning, task management, documentation, memory, approvals, and evaluation.

## Architecture overview

- Backend: FastAPI + Pydantic + SQLAlchemy
- Frontend: React + Vite + TypeScript
- Database: PostgreSQL
- Cache/queue: Redis
- Browser automation: Playwright
- Security: JWT auth, permissions, approval workflows
- Evaluation: benchmark-oriented agent metrics

## Repository layout

```text
aura/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── services/
│   │   ├── tools/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── index.html
├── docker/
├── docker-compose.yml
├── .env.example
├── README.md
└── LICENSE
```

## Quick start

### 1. Environment

Copy `.env.example` to `.env` and adjust values.

### 2. Start services

```bash
docker compose up -d postgres redis
```

### 3. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

## Agent workflow

When an OpenAI-compatible provider is configured, the Supervisor runs three specialized agents as separate model calls:

1. Research agent receives the user request and relevant saved context.
2. Career agent receives the request and the Research agent's structured findings.
3. Task Manager agent receives the request plus the Research and Career outputs.
4. Evaluator checks that the expected agent outputs are present.

The API response includes `agent_trace` so the handoffs can be inspected. Without `LLM_BASE_URL` and `LLM_MODEL`, the application uses its built-in demo responses.

## Current scope

The app includes account registration and login, user-scoped tasks, memory, documents and approvals, keyword document/context retrieval, a configurable OpenAI-compatible provider, and a React dashboard. Browser visits are still simulated; research uses saved context and does not browse the public web.

## Free-tier deployment

The deployment setup targets a Vercel static frontend, a Render free Docker web service, and a Neon free PostgreSQL database. Render's free web service may sleep when idle and take time to wake; free-tier availability and limits depend on the provider and account.

1. Create a Neon PostgreSQL project and copy its pooled connection string. For this Psycopg 3 backend, set its scheme to `postgresql+psycopg://` and keep `sslmode=require` in the URL.
2. In Render, create a Blueprint from this repository and select `render.yaml`. Set `DATABASE_URL` to the Neon connection string and `CORS_ORIGINS` to the final Vercel origin, for example `https://aura-web.vercel.app`. Render generates `SECRET_KEY`; do not replace it with the placeholder.
3. In Vercel, import this repository as a project with the root directory set to `frontend`. Set `VITE_API_URL` to the Render API origin, for example `https://aura-api.onrender.com`, without a trailing slash.
4. After Vercel provides its final domain, update Render's `CORS_ORIGINS` to that exact origin and redeploy the API.

The OpenAI-compatible model variables are optional. Keep `LLM_API_KEY` in Render's environment settings only; never add provider credentials to Git or the Vercel frontend.
