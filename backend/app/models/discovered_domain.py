"""Discovered Domain model for tracking domains found during lead discovery."""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..database import Base


class DiscoveredDomain(Base):
    """Model for storing discovered domains during lead search."""
    
    __tablename__ = "discovered_domains"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    discovery_job_id = Column(UUID(as_uuid=True), ForeignKey("lead_discovery_jobs.id"), nullable=False, index=True)
    
    # Domain information
    domain = Column(String(500), nullable=False, index=True)
    source_url = Column(String(1000), nullable=True)
    
    # Crawling status: pending, crawled, failed
    status = Column(String(50), default="pending", nullable=False, index=True)
    
    # Extracted data (stored temporarily before creating Lead records)
    company_name = Column(String(500), nullable=True)
    company_description = Column(Text, nullable=True)
    emails_found = Column(Text, nullable=True)  # Comma-separated list
    raw_content = Column(Text, nullable=True)  # Raw scraped content for AI enrichment
    
    # Error tracking
    error_message = Column(String(1000), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    crawled_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<DiscoveredDomain(id={self.id}, domain={self.domain}, status={self.status})>"
