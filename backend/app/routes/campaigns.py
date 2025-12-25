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
    from datetime import datetime
    
    for lead_id in request.lead_ids:
        # Check if lead is already in this campaign
        existing = db.query(CampaignLead).filter(
            CampaignLead.campaign_id == campaign_id,
            CampaignLead.lead_id == lead_id
        ).first()
        
        if existing:
            # Skip if already enrolled
            continue
        
        # Create CampaignLead record with next_run_at set to now
        campaign_lead = CampaignLead(
            campaign_id=campaign_id,
            lead_id=lead_id,
            status=CampaignLeadStatus.PENDING.value,
            current_step_index=0,
            last_step_index=0,
            next_run_at=datetime.utcnow()  # Set to trigger immediately
        )
        db.add(campaign_lead)
        
        enqueued_count += 1
    
    db.commit()
    
    return {
        "message": f"Successfully enqueued {enqueued_count} lead(s) to campaign",
        "enqueued_count": enqueued_count,
        "skipped_count": len(request.lead_ids) - enqueued_count
    }


@router.post("/{campaign_id}/activate")
async def activate_campaign(
    campaign_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Activate a campaign and trigger sending for all enrolled leads.
    
    Args:
        campaign_id: Campaign ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    from datetime import datetime
    
    # Verify campaign exists and belongs to user
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Update campaign status
    campaign.status = CampaignStatus.ACTIVE
    
    # Set next_run_at for all pending/in_progress leads to now
    now = datetime.utcnow()
    db.query(CampaignLead).filter(
        CampaignLead.campaign_id == campaign_id,
        CampaignLead.status.in_([
            CampaignLeadStatus.PENDING.value,
            CampaignLeadStatus.IN_PROGRESS.value
        ])
    ).update({
        "next_run_at": now
    }, synchronize_session=False)
    
    db.commit()
    
    return {"message": "Campaign activated successfully"}


@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Pause a campaign.
    
    Args:
        campaign_id: Campaign ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    # Verify campaign exists and belongs to user
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Update campaign status
    campaign.status = CampaignStatus.PAUSED
    db.commit()
    
    return {"message": "Campaign paused successfully"}


@router.get("/campaigns/{campaign_id}/leads")
async def get_campaign_leads(
    campaign_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all enrolled leads for a campaign.
    
    Args:
        campaign_id: Campaign ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of enrolled leads with their campaign status
    """
    # Verify campaign exists and belongs to user
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Get campaign leads with lead details
    campaign_leads = db.query(CampaignLead, Lead).join(
        Lead, CampaignLead.lead_id == Lead.id
    ).filter(
        CampaignLead.campaign_id == campaign_id
    ).order_by(CampaignLead.created_at.desc()).all()
    
    result = []
    for campaign_lead, lead in campaign_leads:
        result.append({
            "id": str(campaign_lead.id),
            "lead_id": str(lead.id),
            "email": lead.email,
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "company": lead.company,
            "title": lead.title,
            "status": campaign_lead.status,
            "current_step_index": campaign_lead.current_step_index,
            "last_step_index": campaign_lead.last_step_index,
            "next_run_at": campaign_lead.next_run_at.isoformat() if campaign_lead.next_run_at else None,
            "last_sent_at": campaign_lead.last_sent_at.isoformat() if campaign_lead.last_sent_at else None,
            "created_at": campaign_lead.created_at.isoformat() if campaign_lead.created_at else None
        })
    
    return result
