"""Extended Lead schemas for LinkedIn enrichment."""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
import uuid


class LinkedInEnrichmentRequest(BaseModel):
    """Request to enrich a lead from LinkedIn URL."""
    linkedin_url: str = Field(..., description="LinkedIn profile URL")


class LinkedInEnrichmentResponse(BaseModel):
    """Response from LinkedIn enrichment."""
    job_title: Optional[str]
    seniority: Optional[str]
    company_size: Optional[str]
    linkedin_headline: Optional[str]
    success: bool
    error: Optional[str]
