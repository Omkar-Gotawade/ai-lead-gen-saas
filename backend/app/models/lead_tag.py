"""Lead tag model for categorization."""
from sqlalchemy import Column, String, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class LeadTag(Base):
    """Many-to-many relationship for lead tags."""
    
    __tablename__ = "lead_tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    tag = Column(String(100), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Composite unique constraint
    __table_args__ = (
        Index('idx_lead_tags_lead_tag', 'lead_id', 'tag', unique=True),
        Index('idx_lead_tags_tag', 'tag'),
    )
