from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.agents.llm import LLMProviderError
from app.agents.context import retrieve_relevant_context
from app.agents.supervisor import SupervisorAgent
from app.api.auth import router as auth_router
from app.api.approvals import router as approvals_router
from app.api.browser import router as browser_router
from app.api.documents import router as documents_router
from app.api.memory import router as memory_router
from app.api.security import router as security_router
from app.api.tasks import router as tasks_router
from app.api.tools import router as tools_router
from app.core.database import get_db, init_db
from app.core.security import get_current_user
from app.models.user import User

app = FastAPI(title="AURA API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(tasks_router)
app.include_router(auth_router)
app.include_router(memory_router)
app.include_router(tools_router)
app.include_router(approvals_router)
app.include_router(documents_router)
app.include_router(browser_router)
app.include_router(security_router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "aura-backend"}


@app.get("/api/agents")
def list_agents():
    supervisor = SupervisorAgent()
    return {
        "agents": [
            {
                "name": supervisor.name,
                "description": supervisor.description,
                "capabilities": supervisor.capabilities,
            }
        ]
    }


@app.post("/api/agents/run")
def run_agent(
    request: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user_request = request.get("task") or request.get("user_request") or "General request"
    supervisor = SupervisorAgent()
    try:
        context = retrieve_relevant_context(user_request, db, user.id)
        return supervisor.run(user_request, context)
    except LLMProviderError as error:
        raise HTTPException(
            status_code=502,
            detail="The configured LLM provider failed. Check provider settings and try again.",
        ) from error
