"""Pydantic schemas for Lead Discovery feature."""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
import uuid
import json


# Request schemas
class LeadDiscoveryStartRequest(BaseModel):
    """Request to start a new lead discovery job."""
    keywords: str = Field(..., min_length=1, max_length=500,
                          description="Search keywords (e.g. 'VP Sales SaaS India')")
    location: Optional[str] = Field(None, max_length=200,
                                    description="Location filter (e.g. 'India', 'New York')")
    industry: Optional[str] = Field(None, max_length=200,
                                    description="Industry filter (e.g. 'SaaS')")
    job_title: Optional[str] = Field(None, max_length=200,
                                     description="Job title filter (e.g. 'VP Sales', 'CTO')")
    seniority: Optional[str] = Field(None, max_length=50,
                                     description="Seniority level: senior | manager | director | vp | c_suite | founder")
    max_results: Optional[int] = Field(25, ge=1, le=100,
                                       description="Maximum number of leads to find")


# Response schemas
class LeadDiscoveryJobResponse(BaseModel):
    """Response for a lead discovery job."""
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    org_id: Optional[uuid.UUID] = None
    keywords: str
    location: Optional[str] = None
    industry: Optional[str] = None
    status: str
    domains_found: int
    domains_crawled: int
    leads_created: int
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DiscoveredPersonInfo(BaseModel):
    """Decoded person metadata (parsed from company_description JSON)."""
    first_name: str = ""
    last_name: str = ""
    title: str = ""
    seniority: str = ""
    location: str = ""
    industry: str = ""
    source: str = ""
    company: str = ""


class DiscoveredDomainResponse(BaseModel):
    """Response for a discovered domain / person row."""
    id: uuid.UUID
    domain: str
    source_url: Optional[str] = None
    status: str
    company_name: Optional[str] = None
    company_description: Optional[str] = None
    emails_found: Optional[str] = None
    created_at: datetime

    # Decoded person metadata (populated by the validator below)
    person: Optional[DiscoveredPersonInfo] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj: Any) -> "DiscoveredDomainResponse":
        instance = super().from_orm(obj)
        # Try to decode person metadata stored as JSON in company_description
        if instance.company_description:
            try:
                meta = json.loads(instance.company_description)
                if isinstance(meta, dict) and "first_name" in meta:
                    instance.person = DiscoveredPersonInfo(**{
                        k: meta.get(k, "") for k in DiscoveredPersonInfo.model_fields
                    })
            except Exception:
                pass
        return instance


class LeadDiscoveryStatusResponse(BaseModel):
    """Detailed status response for a lead discovery job."""
    job: LeadDiscoveryJobResponse
    discovered_domains: List[DiscoveredDomainResponse] = []
    progress_percent: int = Field(0, ge=0, le=100)
