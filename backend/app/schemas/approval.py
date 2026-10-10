from datetime import datetime

from pydantic import BaseModel, Field


class ApprovalCreate(BaseModel):
    action: str = Field(..., min_length=1)
    risk_level: int = Field(default=0, ge=0, le=3)
    reason: str | None = None


class ApprovalResponse(ApprovalCreate):
    id: int
    user_id: str
    status: str
    requires_approval: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
