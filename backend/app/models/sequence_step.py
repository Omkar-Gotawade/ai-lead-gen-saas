"""Sequence step model for campaign steps."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class SequenceStep(Base):
    """Individual step in an email campaign sequence."""
    __tablename__ = "sequence_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    
    step_index = Column(Integer, nullable=False)  # Order in sequence (1, 2, 3...)
    delay_days = Column(Integer, default=0, nullable=False)  # Delay from previous step
    
    subject_template = Column(String, nullable=False)
    body_template = Column(String, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
