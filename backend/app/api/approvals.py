from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.database import get_db
from app.models.approval import Approval
from app.models.user import User
from app.schemas.approval import ApprovalCreate, ApprovalResponse

router = APIRouter(prefix="/api", tags=["approvals"])


@router.get("/approvals", response_model=List[ApprovalResponse])
def list_approvals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    approvals = db.query(Approval).filter(Approval.user_id == user.id).order_by(Approval.created_at.desc()).all()
    return approvals


@router.post("/approvals", response_model=ApprovalResponse, status_code=status.HTTP_201_CREATED)
def create_approval(
    approval: ApprovalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    db_approval = Approval(
        user_id=user.id,
        action=approval.action,
        risk_level=approval.risk_level,
        reason=approval.reason,
        status="pending",
        requires_approval=str(approval.risk_level >= 1).lower(),
    )
    db.add(db_approval)
    db.commit()
    db.refresh(db_approval)
    return db_approval


@router.post("/approvals/{approval_id}/approve", response_model=ApprovalResponse)
def approve_approval(
    approval_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    approval = db.query(Approval).filter(Approval.id == approval_id, Approval.user_id == user.id).first()
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    approval.status = "approved"
    approval.requires_approval = "false"
    db.commit()
    db.refresh(approval)
    return approval
