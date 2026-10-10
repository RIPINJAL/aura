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

## Phase 1 status

This repository currently includes the foundational pieces for:

- FastAPI backend shell
- Supervisor agent scaffold
- Task management API
- Health route
- React dashboard shell
- Docker Compose for Postgres and Redis
- Environment configuration

## Notes

This is the foundation for the larger multi-agent platform described in the project brief. The next stages are memory, tool registry, browser agent, evaluator, approvals, and deployment hardening.
