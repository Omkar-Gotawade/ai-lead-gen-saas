"""Pydantic schemas for Deliverability features."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uuid


# DNS Check schemas
class DNSCheckRequest(BaseModel):
    """Request to check DNS records for a domain."""
    domain: str = Field(..., min_length=1, max_length=500, description="Domain to check (e.g., 'example.com')")


class SPFCheckResult(BaseModel):
    """SPF record check result."""
    exists: bool
    record: Optional[str]
    valid: bool
    issues: List[str] = []


class DKIMCheckResult(BaseModel):
    """DKIM record check result."""
    exists: bool
    record: Optional[str]
    note: str


class DMARCCheckResult(BaseModel):
    """DMARC record check result."""
    exists: bool
    record: Optional[str]
    policy: Optional[str]
    valid: bool
    issues: List[str] = []


class MXCheckResult(BaseModel):
    """MX record check result."""
    exists: bool
    records: List[str] = []


class DNSCheckResponse(BaseModel):
    """Complete DNS check response."""
    domain: str
    spf: SPFCheckResult
    dkim: DKIMCheckResult
    dmarc: DMARCCheckResult
    mx: MXCheckResult
    overall_score: int = Field(0, ge=0, le=100)
    recommendations: List[str] = []


# Email Warmup schemas
class EmailWarmupDomainResponse(BaseModel):
    """Response for email warmup domain."""
    id: uuid.UUID
    org_id: uuid.UUID
    domain: str
    daily_limit: int
    warmup_day: int
    emails_sent_today: int
    last_reset_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EmailWarmupDomainCreate(BaseModel):
    """Request to create email warmup tracking for a domain."""
    domain: str = Field(..., min_length=1, max_length=500)
    org_id: Optional[uuid.UUID] = None


class EmailWarmupStatusResponse(BaseModel):
    """Status response for email warmup."""
    domain: str
    warmup_day: int
    daily_limit: int
    emails_sent_today: int
    remaining_today: int
    next_limit: int  # What limit will be tomorrow
    warmup_complete: bool  # True if reached max limit
