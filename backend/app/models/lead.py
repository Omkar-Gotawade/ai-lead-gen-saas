"""Lead model for storing lead information."""
from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
from ..database import Base


class Lead(Base):
    """Lead model for storing lead/prospect information."""
    
    __tablename__ = "leads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # For future multi-tenant support
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    industry = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    source = Column(String(100), nullable=True)  # e.g., "csv_upload", "manual", "api"
    enriched_data = Column(JSONB, nullable=True)  # Store enrichment data as JSON
    
    # v1: LinkedIn enrichment fields
    linkedin_url = Column(String(500), nullable=True)
    job_title = Column(String(255), nullable=True)
    seniority = Column(String(100), nullable=True)  # e.g., "Senior", "Manager", "Director"
    company_size = Column(String(100), nullable=True)  # e.g., "1-10", "11-50", "51-200"
    linkedin_headline = Column(String(500), nullable=True)
    
    # Enhanced fields for better email personalization
    location = Column(String(255), nullable=True)  # City, State/Country
    research_notes = Column(Text, nullable=True)  # Manual research findings for personalization
    
    # Week 3: Bounce and do-not-contact tracking
    do_not_contact = Column(Boolean, default=False, nullable=False, index=True)
    bounce_reason = Column(String(255), nullable=True)
    bounced_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Lead(id={self.id}, name={self.full_name}, email={self.email})>"
