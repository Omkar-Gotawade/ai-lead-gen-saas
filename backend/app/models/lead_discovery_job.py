"""Lead Discovery Job model for tracking automated lead discovery tasks."""
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from ..database import Base


class LeadDiscoveryJob(Base):
    """Model for tracking lead discovery jobs."""
    
    __tablename__ = "lead_discovery_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    org_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Search parameters
    keywords = Column(String(500), nullable=False)
    location = Column(String(200), nullable=True)
    industry = Column(String(200), nullable=True)
    
    # Job status: pending, running, completed, failed
    status = Column(String(50), default="pending", nullable=False, index=True)
    
    # Statistics
    domains_found = Column(Integer, default=0)
    domains_crawled = Column(Integer, default=0)
    leads_created = Column(Integer, default=0)
    
    # Error tracking
    error_message = Column(String(1000), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<LeadDiscoveryJob(id={self.id}, keywords={self.keywords}, status={self.status})>"
