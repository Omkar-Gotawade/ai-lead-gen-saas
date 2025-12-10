"""Sending log model for tracking email sends."""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.database import Base


class SendStatus(str, enum.Enum):
    """Email send status."""
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


class SendingLog(Base):
    """Email sending log."""
    __tablename__ = "sending_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    lead_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    provider_type = Column(String, nullable=False)
    to_email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    
    status = Column(SQLEnum(SendStatus), default=SendStatus.QUEUED, nullable=False)
    error_message = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
