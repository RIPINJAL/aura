from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, default="demo-user")
    action = Column(String, nullable=False)
    risk_level = Column(Integer, nullable=False, default=0)
    reason = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="pending")
    requires_approval = Column(String, nullable=False, default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
