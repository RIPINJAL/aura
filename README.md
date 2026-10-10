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
