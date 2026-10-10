from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    priority: str = "medium"
    status: str = "pending"
    deadline: Optional[datetime] = None


class TaskStatusUpdate(BaseModel):
    status: Literal["pending", "in_progress", "completed"]


class TaskResponse(TaskCreate):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
