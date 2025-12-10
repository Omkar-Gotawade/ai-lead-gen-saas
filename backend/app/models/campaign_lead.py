"""Campaign lead model for tracking leads in campaigns."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.database import Base


class CampaignLeadStatus(str, enum.Enum):
    """Campaign lead status."""
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    STOPPED = "stopped"


class CampaignLead(Base):
    """Lead enrolled in a campaign."""
    __tablename__ = "campaign_leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    
    status = Column(String, default=CampaignLeadStatus.QUEUED.value, nullable=False)
    last_step_index = Column(Integer, default=0, nullable=False)
    last_sent_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
