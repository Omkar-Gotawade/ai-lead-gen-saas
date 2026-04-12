"""Schemas for pre-send spam check API."""
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel


class SpamCheckRequest(BaseModel):
    """Spam check request payload."""

    email_body: str
    lead_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None


class SpamCheckResponse(BaseModel):
    """Spam check analysis result."""

    score: int
    level: Literal["safe", "warning", "critical"]
    issues: List[str]
