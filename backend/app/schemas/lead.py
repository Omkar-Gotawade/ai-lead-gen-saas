"""Lead schemas for CRUD operations."""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any


class LeadCreate(BaseModel):
    """Schema for creating a new lead."""
    first_name: str
    last_name: str
    email: EmailStr
    company: Optional[str] = None
    source: Optional[str] = "manual"
    linkedin_url: Optional[str] = None
    job_title: Optional[str] = None
    seniority: Optional[str] = None
    company_size: Optional[str] = None


class LeadUpdate(BaseModel):
    """Schema for updating a lead."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    source: Optional[str] = None
    linkedin_url: Optional[str] = None
    job_title: Optional[str] = None
    seniority: Optional[str] = None
    company_size: Optional[str] = None


class LeadResponse(BaseModel):
    """Schema for lead response."""
    id: UUID
    org_id: Optional[UUID] = None
    first_name: str
    last_name: str
    full_name: str
    email: str
    company: Optional[str] = None
    source: Optional[str] = None
    enriched_data: Optional[Dict[str, Any]] = None
    linkedin_url: Optional[str] = None
    job_title: Optional[str] = None
    seniority: Optional[str] = None
    company_size: Optional[str] = None
    linkedin_headline: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """Schema for paginated lead list response."""
    total: int
    page: int
    page_size: int
    leads: List[LeadResponse]
