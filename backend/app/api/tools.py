from fastapi import APIRouter

from app.tools.registry import ToolRegistry

router = APIRouter(prefix="/api", tags=["tools"])


@router.get("/tools")
def list_tools():
    registry = ToolRegistry()
    return {"tools": registry.list_tools()}
