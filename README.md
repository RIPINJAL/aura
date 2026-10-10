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

The checked-in setup targets a Vercel static frontend, a Render free Docker web service, and a Neon free PostgreSQL database. This can run at $0 while each account stays within its free allowances; it is a hobby/demo setup, not an always-on production guarantee.

### Free-plan caveats

- Vercel Hobby is free for personal, non-commercial use and has monthly usage caps. If this app is for a business or commercial use, check Vercel's current plan terms first.
- Render's free web service has 512 MB RAM, sleeps after 15 minutes without traffic, and can take about a minute to wake. The Hobby workspace includes 750 free instance-hours per calendar month, shared across its free services. Bandwidth and build minutes are also limited.
- Use Neon for the database. Render's free Postgres is only 1 GB and expires 30 days after creation; it is deliberately not part of this setup. Neon Free currently includes 100 CU-hours and 1 GB storage per project, 5 GB monthly public egress, and scales compute to zero after 5 minutes idle. If its compute or egress allowance is exhausted, the database suspends until the allowance resets; over 1 GB storage, writes that increase storage fail.
- A real model provider is optional. If you set `LLM_API_KEY`, model usage may cost money according to that provider. Leave LLM settings blank to deploy in demo mode with no model API charges.
- Do not add a credit card or choose a paid plan if you need to keep the deployment at $0. Check the provider's billing and usage page regularly; provider limits and terms can change.

### Deploy the database

1. Create or sign in to a Neon account and create a project on the **Free** plan. Choose a region near the Render service.
2. In the Neon project, open **Connection Details**, select the pooled connection option, and copy the connection string. Keep `sslmode=require` in the query string.
3. SQLAlchemy needs the Psycopg 3 driver name. In Render, set `DATABASE_URL` to the same connection string with its prefix changed from `postgresql://` to `postgresql+psycopg://`. Do not commit this URL or paste it into chat.

### Deploy the API

1. Sign in to Render and connect the GitHub account that can access `RIPINJAL/aura`.
2. Choose **New** → **Blueprint**, select the `RIPINJAL/aura` repository and its `main` branch, then apply the Blueprint from `render.yaml`.
3. Select the **Free** compute plan for `aura-api` if Render asks. Keep the generated `SECRET_KEY`; do not use the placeholder from `.env.example`.
4. Set `DATABASE_URL` to the Neon connection string prepared above. Leave `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL` empty for no model-provider charges.
5. The Blueprint's example CORS origin assumes `https://aura-web.vercel.app`. You will replace it with the actual Vercel domain after the frontend deploys.
6. Wait for the Render service to finish deploying. Check `https://<your-render-service>.onrender.com/api/health`; it should return `{"status":"ok","service":"aura-backend"}`. Record the service origin without a trailing slash.

### Deploy the frontend

1. Sign in to Vercel and import `RIPINJAL/aura` from GitHub.
2. Set **Root Directory** to `frontend` and leave the framework as **Vite**. The project `frontend/vercel.json` sets the build command and output folder.
3. Add the environment variable `VITE_API_URL` with the Render API origin, such as `https://aura-api.onrender.com` (no `/api` suffix and no trailing slash).
4. Deploy and note the exact production domain Vercel assigns, for example `https://aura-web.vercel.app`.

### Connect and smoke-test

1. In Render, open `aura-api` → **Environment** and set `CORS_ORIGINS` to the exact Vercel origin, with no path or trailing slash. For example: `https://aura-web.vercel.app`.
2. Save the environment change and let Render redeploy the API.
3. Open the Vercel site, create an account, sign in, add a task, then sign out and back in to confirm the database-backed flow.
4. Visit the Render health URL again if the first app request is slow; a sleeping free service needs time to wake.

Keep `LLM_API_KEY` only in Render's environment settings if you later configure a provider; never put it in Vercel or Git. Detailed provider limits and current terms: [Vercel Hobby](https://vercel.com/docs/plans/hobby), [Render free instances](https://render.com/docs/free), and [Neon plans](https://neon.com/docs/introduction/plans).
