"""Campaign and sequence step schemas."""
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class SequenceStepBase(BaseModel):
    """Base sequence step schema."""
    step_index: int
    delay_days: int = 0
    subject_template: str
    body_template: str


class SequenceStepCreate(SequenceStepBase):
    """Create sequence step."""
    pass


class SequenceStepUpdate(BaseModel):
    """Update sequence step."""
    step_index: Optional[int] = None
    delay_days: Optional[int] = None
    subject_template: Optional[str] = None
    body_template: Optional[str] = None


class SequenceStepResponse(SequenceStepBase):
    """Sequence step response."""
    id: UUID
    campaign_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CampaignBase(BaseModel):
    """Base campaign schema."""
    name: str
    description: Optional[str] = None


class CampaignCreate(CampaignBase):
    """Create campaign."""
    pass


class CampaignUpdate(BaseModel):
    """Update campaign."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class CampaignResponse(CampaignBase):
    """Campaign response."""
    id: UUID
    user_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CampaignWithSteps(CampaignResponse):
    """Campaign with its sequence steps."""
    steps: List[SequenceStepResponse] = []
