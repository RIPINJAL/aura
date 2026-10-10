from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskStatusUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskResponse])
def list_tasks(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.user_id == user.id).order_by(Task.created_at.desc()).all()
    return tasks


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_task = Task(
        user_id=user.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        deadline=task.deadline,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    update: TaskStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = update.status
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
