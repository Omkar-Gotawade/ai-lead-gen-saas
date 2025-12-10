"""Lead management routes."""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..database import get_db
from ..schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadListResponse
from ..services.leads import LeadService
from ..services.auth import get_current_user
from ..models.user import User
from ..workers.tasks import enrich_lead_task

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("", response_model=LeadListResponse)
async def list_leads(
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated list of leads.
    
    Args:
        page: Page number (default: 1)
        page_size: Number of leads per page (default: 50)
        db: Database session
        current_user: Authenticated user
        
    Returns:
        LeadListResponse: Paginated list of leads
    """
    lead_service = LeadService(db)
    result = lead_service.get_leads(page=page, page_size=page_size)
    return result


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new lead.
    
    Args:
        lead_data: Lead creation data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        LeadResponse: Created lead information
    """
    lead_service = LeadService(db)
    lead = lead_service.create_lead(lead_data)
    # Set the org_id to the current user's ID
    lead.org_id = current_user.id
    db.commit()
    db.refresh(lead)
    return lead


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a single lead by ID.
    
    Args:
        lead_id: Lead UUID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        LeadResponse: Lead information
        
    Raises:
        HTTPException: If lead not found
    """
    lead_service = LeadService(db)
    lead = lead_service.get_lead(lead_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a lead.
    
    Args:
        lead_id: Lead UUID
        lead_data: Lead update data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        LeadResponse: Updated lead information
        
    Raises:
        HTTPException: If lead not found
    """
    lead_service = LeadService(db)
    lead = lead_service.update_lead(lead_id, lead_data)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a lead.
    
    Args:
        lead_id: Lead UUID
        db: Database session
        current_user: Authenticated user
        
    Raises:
        HTTPException: If lead not found
    """
    lead_service = LeadService(db)
    success = lead_service.delete_lead(lead_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )


@router.post("/upload_csv", status_code=status.HTTP_201_CREATED)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload CSV file to create multiple leads.
    
    Args:
        file: CSV file
        db: Database session
        current_user: Authenticated user
        
    Returns:
        dict: Upload result with count of created leads
        
    Raises:
        HTTPException: If CSV is invalid or processing fails
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    lead_service = LeadService(db)
    
    try:
        contents = await file.read()
        created_count = lead_service.create_leads_from_csv(contents)
        
        return {
            "message": "CSV uploaded successfully",
            "leads_created": created_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing CSV: {str(e)}"
        )


@router.post("/{lead_id}/enrich", status_code=status.HTTP_202_ACCEPTED)
async def enrich_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Enqueue background job to enrich lead data.
    
    Args:
        lead_id: Lead UUID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        dict: Job enqueued confirmation
        
    Raises:
        HTTPException: If lead not found
    """
    lead_service = LeadService(db)
    lead = lead_service.get_lead(lead_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Enqueue Celery task
    task = enrich_lead_task.delay(str(lead_id))
    
    return {
        "message": "Lead enrichment job enqueued",
        "lead_id": str(lead_id),
        "task_id": task.id
    }
