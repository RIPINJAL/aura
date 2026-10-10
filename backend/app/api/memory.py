from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.database import get_db
from app.models.memory import Memory
from app.models.user import User
from app.schemas.memory import MemoryCreate, MemoryResponse

router = APIRouter(prefix="/api", tags=["memory"])


@router.get("/memory", response_model=List[MemoryResponse])
def list_memory(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    memories = db.query(Memory).filter(Memory.user_id == user.id).order_by(Memory.created_at.desc()).all()
    return memories


@router.post("/memory", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(
    memory: MemoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    db_memory = Memory(user_id=user.id, type=memory.type, content=memory.content)
    db.add(db_memory)
    db.commit()
    db.refresh(db_memory)
    return db_memory


@router.get("/memory/{memory_id}", response_model=MemoryResponse)
def get_memory(memory_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    memory = db.query(Memory).filter(Memory.id == memory_id, Memory.user_id == user.id).first()
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory
