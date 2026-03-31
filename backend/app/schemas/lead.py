"""Lead schemas for CRUD operations."""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any


class LeadCreate(BaseModel):
    """Schema for creating a new lead."""
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    company: Optional[str] = Field(None, max_length=200)
    title: Optional[str] = Field(None, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    research_notes: Optional[str] = Field(None, max_length=5000)
    source: Optional[str] = Field("manual", max_length=50)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    job_title: Optional[str] = Field(None, max_length=200)
    seniority: Optional[str] = Field(None, max_length=50)
    company_size: Optional[str] = Field(None, max_length=50)


class LeadUpdate(BaseModel):
    """Schema for updating a lead."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    company: Optional[str] = Field(None, max_length=200)
    title: Optional[str] = Field(None, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    research_notes: Optional[str] = Field(None, max_length=5000)
    source: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    job_title: Optional[str] = Field(None, max_length=200)
    seniority: Optional[str] = Field(None, max_length=50)
    company_size: Optional[str] = Field(None, max_length=50)
    do_not_contact: Optional[bool] = None
    is_do_not_contact: Optional[bool] = None
    dnc_reason: Optional[str] = Field(None, max_length=255)


class LeadResponse(BaseModel):
    """Schema for lead response."""
    id: UUID
    org_id: Optional[UUID] = None
    first_name: str
    last_name: str
    full_name: str
    email: str
    company: Optional[str] = None
    title: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    research_notes: Optional[str] = None
    source: Optional[str] = None
    enriched_data: Optional[Dict[str, Any]] = None
    linkedin_url: Optional[str] = None
    job_title: Optional[str] = None
    seniority: Optional[str] = None
    company_size: Optional[str] = None
    linkedin_headline: Optional[str] = None
    do_not_contact: bool
    is_do_not_contact: bool
    dnc_reason: Optional[str] = None
    dnc_at: Optional[datetime] = None
    bounce_reason: Optional[str] = None
    bounced_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """Schema for paginated lead list response."""
    total: int
    page: int
    page_size: int
    leads: List[LeadResponse]
