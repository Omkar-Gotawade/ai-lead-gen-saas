"""Pydantic schemas for Lead Discovery feature."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


# Request schemas
class LeadDiscoveryStartRequest(BaseModel):
    """Request to start a new lead discovery job."""
    keywords: str = Field(..., min_length=1, max_length=500, description="Search keywords (e.g., 'AI software')")
    location: Optional[str] = Field(None, max_length=200, description="Location filter (e.g., 'India')")
    industry: Optional[str] = Field(None, max_length=200, description="Industry filter (e.g., 'SaaS')")
    max_results: Optional[int] = Field(20, ge=1, le=100, description="Maximum domains to discover")


# Response schemas
class LeadDiscoveryJobResponse(BaseModel):
    """Response for a lead discovery job."""
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    org_id: Optional[uuid.UUID]
    keywords: str
    location: Optional[str]
    industry: Optional[str]
    status: str
    domains_found: int
    domains_crawled: int
    leads_created: int
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DiscoveredDomainResponse(BaseModel):
    """Response for a discovered domain."""
    id: uuid.UUID
    domain: str
    source_url: Optional[str]
    status: str
    company_name: Optional[str]
    company_description: Optional[str]
    emails_found: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LeadDiscoveryStatusResponse(BaseModel):
    """Detailed status response for a lead discovery job."""
    job: LeadDiscoveryJobResponse
    discovered_domains: List[DiscoveredDomainResponse] = []
    progress_percent: int = Field(0, ge=0, le=100)
