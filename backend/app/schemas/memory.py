from datetime import datetime

from pydantic import BaseModel, Field


class MemoryCreate(BaseModel):
    type: str = Field(default="semantic")
    content: str = Field(..., min_length=1)


class MemoryResponse(MemoryCreate):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
