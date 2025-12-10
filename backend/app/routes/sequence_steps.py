"""Sequence step management routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Annotated
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.campaign import Campaign
from app.models.sequence_step import SequenceStep
from app.schemas.campaign import (
    SequenceStepCreate,
    SequenceStepUpdate,
    SequenceStepResponse
)
from app.services.auth import get_current_user

router = APIRouter()


@router.get("/campaigns/{campaign_id}/steps", response_model=List[SequenceStepResponse])
async def list_sequence_steps(
    campaign_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all sequence steps for a campaign.
    
    Args:
        campaign_id: Campaign ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of sequence steps
    """
    # Verify campaign belongs to user
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    steps = db.query(SequenceStep).filter(
        SequenceStep.campaign_id == campaign_id
    ).order_by(SequenceStep.step_index).all()
    
    return steps


@router.post("/campaigns/{campaign_id}/steps", response_model=SequenceStepResponse)
async def create_sequence_step(
    campaign_id: UUID,
    step: SequenceStepCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new sequence step.
    
    Args:
        campaign_id: Campaign ID
        step: Sequence step data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Created sequence step
    """
    # Verify campaign belongs to user
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    db_step = SequenceStep(
        campaign_id=campaign_id,
        step_index=step.step_index,
        delay_days=step.delay_days,
        subject_template=step.subject_template,
        body_template=step.body_template
    )
    
    db.add(db_step)
    db.commit()
    db.refresh(db_step)
    
    return db_step


@router.put("/sequence-steps/{step_id}", response_model=SequenceStepResponse)
async def update_sequence_step(
    step_id: UUID,
    step_update: SequenceStepUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a sequence step.
    
    Args:
        step_id: Sequence step ID
        step_update: Updated step data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Updated sequence step
    """
    step = db.query(SequenceStep).filter(
        SequenceStep.id == step_id
    ).first()
    
    if not step:
        raise HTTPException(status_code=404, detail="Sequence step not found")
    
    # Verify campaign belongs to user
    campaign = db.query(Campaign).filter(
        Campaign.id == step.campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Update fields
    if step_update.step_index is not None:
        step.step_index = step_update.step_index
    if step_update.delay_days is not None:
        step.delay_days = step_update.delay_days
    if step_update.subject_template is not None:
        step.subject_template = step_update.subject_template
    if step_update.body_template is not None:
        step.body_template = step_update.body_template
    
    db.commit()
    db.refresh(step)
    
    return step


@router.delete("/sequence-steps/{step_id}")
async def delete_sequence_step(
    step_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a sequence step.
    
    Args:
        step_id: Sequence step ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    step = db.query(SequenceStep).filter(
        SequenceStep.id == step_id
    ).first()
    
    if not step:
        raise HTTPException(status_code=404, detail="Sequence step not found")
    
    # Verify campaign belongs to user
    campaign = db.query(Campaign).filter(
        Campaign.id == step.campaign_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    db.delete(step)
    db.commit()
    
    return {"message": "Sequence step deleted successfully"}
