"""Campaign management routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Annotated
from uuid import UUID
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.campaign import Campaign, CampaignStatus
from app.models.sequence_step import SequenceStep
from app.models.campaign_lead import CampaignLead, CampaignLeadStatus
from app.models.lead import Lead
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignWithSteps
)
from app.services.auth import get_current_user

router = APIRouter()


class EnqueueLeadsRequest(BaseModel):
    """Request to enqueue leads to a campaign."""
    lead_ids: List[str]


@router.get("/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all campaigns for the current user.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of campaigns
    """
    campaigns = db.query(Campaign).filter(
        Campaign.user_id == current_user.id
    ).order_by(Campaign.created_at.desc()).all()
    
    return campaigns


@router.post("/campaigns", response_model=CampaignResponse)
async def create_campaign(
    campaign: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new campaign.
    
    Args:
        campaign: Campaign data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Created campaign
    """
    db_campaign = Campaign(
        user_id=current_user.id,
        name=campaign.name,
        description=campaign.description,
        status=CampaignStatus.DRAFT
    )
    
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    
    return db_campaign


@router.get("/campaigns/{campaign_id}", response_model=CampaignWithSteps)
async def get_campaign(
    campaign_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a campaign with its sequence steps.
    
    Args:
        campaign_id: Campaign ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Campaign with steps
    """
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Get sequence steps
    steps = db.query(SequenceStep).filter(
        SequenceStep.campaign_id == campaign_id
    ).order_by(SequenceStep.step_index).all()
    
    return CampaignWithSteps(
        id=campaign.id,
        user_id=campaign.user_id,
        name=campaign.name,
        description=campaign.description,
        status=campaign.status.value,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        steps=steps
    )


@router.put("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    campaign_update: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a campaign.
    
    Args:
        campaign_id: Campaign ID
        campaign_update: Updated campaign data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Updated campaign
    """
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Update fields
    if campaign_update.name is not None:
        campaign.name = campaign_update.name
    if campaign_update.description is not None:
        campaign.description = campaign_update.description
    if campaign_update.status is not None:
        campaign.status = CampaignStatus(campaign_update.status)
    
    db.commit()
    db.refresh(campaign)
    
    return campaign


@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(
    campaign_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a campaign.
    
    Args:
        campaign_id: Campaign ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    db.delete(campaign)
    db.commit()
    
    return {"message": "Campaign deleted successfully"}


@router.post("/{campaign_id}/enqueue")
async def enqueue_leads_to_campaign(
    campaign_id: str,
    request: EnqueueLeadsRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Enqueue multiple leads to a campaign sequence.
    
    Creates CampaignLead records for each lead and queues the first
    sequence step to be sent immediately via Celery worker.
    
    Args:
        campaign_id: Campaign ID
        request: Payload containing list of lead_ids
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message with count of enqueued leads
    """
    # Verify campaign exists and belongs to user
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Verify campaign has at least one sequence step
    step_count = db.query(SequenceStep).filter(
        SequenceStep.campaign_id == campaign_id
    ).count()
    
    if step_count == 0:
        raise HTTPException(
            status_code=400,
            detail="Campaign has no sequence steps configured"
        )
    
    # Verify all leads exist and belong to user
    leads = db.query(Lead).filter(
        Lead.id.in_(request.lead_ids),
        Lead.org_id == current_user.id
    ).all()
    
    if len(leads) != len(request.lead_ids):
        raise HTTPException(
            status_code=400,
            detail="One or more lead IDs are invalid or do not belong to you"
        )
    
    enqueued_count = 0
    
    for lead_id in request.lead_ids:
        # Check if lead is already in this campaign
        existing = db.query(CampaignLead).filter(
            CampaignLead.campaign_id == campaign_id,
            CampaignLead.lead_id == lead_id
        ).first()
        
        if existing:
            # Skip if already enrolled
            continue
        
        # Create CampaignLead record
        campaign_lead = CampaignLead(
            campaign_id=campaign_id,
            lead_id=lead_id,
            status="queued",
            last_step_index=0
        )
        db.add(campaign_lead)
        db.commit()
        db.refresh(campaign_lead)
        
        # Queue first step (step_index 1) immediately
        from app.workers.campaign_worker import run_sequence_step
        run_sequence_step.delay(
            campaign_lead_id=str(campaign_lead.id),
            step_index=1
        )
        
        enqueued_count += 1
    
    return {
        "message": f"Successfully enqueued {enqueued_count} lead(s) to campaign",
        "enqueued_count": enqueued_count,
        "skipped_count": len(request.lead_ids) - enqueued_count
    }
