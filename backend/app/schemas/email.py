"""Email-related Pydantic schemas."""
from pydantic import BaseModel, EmailStr
from typing import Any, Dict, List, Optional
from uuid import UUID


class EmailGenerateRequest(BaseModel):
    """Request to generate email copy."""
    lead_id: UUID
    tone: Optional[str] = "professional"
    goal: Optional[str] = "schedule a meeting"
    product_description: Optional[str] = "our product or service"


class EmailGenerateResponse(BaseModel):
    """Generated email response with Human SDR Copywriter Agent metadata."""
    subject: str
    body: str
    research_notes: Optional[str] = None
    research_status: Optional[str] = None
    # A/B test metadata from Human SDR Copywriter Agent
    email_angle: Optional[str] = None                  # pain_point|curiosity|question|case_study|direct
    word_count: Optional[int] = None
    selected_subject: Optional[str] = None
    alternative_subjects: Optional[List[str]] = None
    quality_report: Optional[Dict[str, Any]] = None


class EmailSendRequest(BaseModel):
    """Request to send an email."""
    lead_id: UUID
    subject: str
    body: str


class EmailSendResponse(BaseModel):
    """Email send response."""
    queued: bool
    message: str


class EmailTestRequest(BaseModel):
    """Request to send a test email."""
    to_email: EmailStr
    subject: str
    body: str


class EmailProviderConnectRequest(BaseModel):
    """Request to connect email provider."""
    provider_type: str  # "smtp" or "sendgrid"
    from_name: str
    from_email: EmailStr
    
    # SMTP fields
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    use_tls: Optional[bool] = True
    use_ssl: Optional[bool] = False
    
    # SendGrid fields
    sendgrid_api_key: Optional[str] = None


class EmailProviderResponse(BaseModel):
    """Email provider configuration response (without sensitive data)."""
    id: UUID
    provider_type: str
    from_name: str
    from_email: str
    configured: bool
    
    class Config:
        from_attributes = True
