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
    Get paginated list of leads for the current user.

    Args:
        page: Page number (default: 1)
        page_size: Number of leads per page (default: 50)
        db: Database session
        current_user: Authenticated user

    Returns:
        LeadListResponse: Paginated list of leads
    """
    lead_service = LeadService(db)
    result = lead_service.get_leads(page=page, page_size=page_size, org_id=current_user.id)
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
    Get a single lead by ID (only if owned by current user).

    Args:
        lead_id: Lead UUID
        db: Database session
        current_user: Authenticated user

    Returns:
        LeadResponse: Lead information

    Raises:
        HTTPException: If lead not found or not authorized
    """
    lead_service = LeadService(db)
    lead = lead_service.get_lead(lead_id, org_id=current_user.id)

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
    Update a lead (only if owned by current user).

    Args:
        lead_id: Lead UUID
        lead_data: Lead update data
        db: Database session
        current_user: Authenticated user

    Returns:
        LeadResponse: Updated lead information

    Raises:
        HTTPException: If lead not found or not authorized
    """
    lead_service = LeadService(db)
    # First verify ownership
    existing_lead = lead_service.get_lead(lead_id, org_id=current_user.id)
    if not existing_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    lead = lead_service.update_lead(lead_id, lead_data, user_id=current_user.id)

    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a lead (only if owned by current user).

    Args:
        lead_id: Lead UUID
        db: Database session
        current_user: Authenticated user

    Raises:
        HTTPException: If lead not found or not authorized
    """
    lead_service = LeadService(db)
    # First verify ownership
    existing_lead = lead_service.get_lead(lead_id, org_id=current_user.id)
    if not existing_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

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


@router.post("/{lead_id}/linkedin-enrich", response_model=LeadResponse)
async def enrich_lead_from_linkedin(
    lead_id: UUID,
    linkedin_url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Enrich lead data from LinkedIn profile URL.
    
    Uses 3rd-party enrichment API (configured in settings) to fetch:
    - Job title
    - Seniority level
    - Company size
    - LinkedIn headline
    
    Args:
        lead_id: Lead UUID
        linkedin_url: LinkedIn profile URL
        db: Database session
        current_user: Authenticated user
        
    Returns:
        LeadResponse: Updated lead with enriched data
        
    Raises:
        HTTPException: If lead not found or enrichment fails
    """
    from ..services.linkedin_enrichment import enrich_linkedin_profile
    from ..config import settings
    import logging
    
    logger = logging.getLogger(__name__)
    
    lead_service = LeadService(db)
    lead = lead_service.get_lead(lead_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Get enrichment API key from settings
    enrichment_api_key = getattr(settings, 'ENRICHMENT_API_KEY', None)
    enrichment_provider = getattr(settings, 'ENRICHMENT_PROVIDER', 'clearbit')
    
    if not enrichment_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LinkedIn enrichment not configured. Set ENRICHMENT_API_KEY in environment."
        )
    
    try:
        # Call enrichment service
        result = enrich_linkedin_profile(
            linkedin_url=linkedin_url,
            provider=enrichment_provider,
            api_key=enrichment_api_key
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"LinkedIn enrichment failed: {result.get('error', 'Unknown error')}"
            )
        
        # Update lead with enriched data
        lead.linkedin_url = linkedin_url
        if result.get('job_title'):
            lead.job_title = result['job_title']
        if result.get('seniority'):
            lead.seniority = result['seniority']
        if result.get('company_size'):
            lead.company_size = result['company_size']
        if result.get('linkedin_headline'):
            lead.linkedin_headline = result['linkedin_headline']
        
        db.commit()
        db.refresh(lead)
        
        logger.info(f"Successfully enriched lead {lead_id} from LinkedIn")
        
        return lead
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LinkedIn enrichment failed for lead {lead_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enrichment failed: {str(e)}"
        )


@router.post("/{lead_id}/tags", status_code=status.HTTP_201_CREATED)
async def add_lead_tag(
    lead_id: UUID,
    tag: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a tag to a lead."""
    from ..models.lead_tag import LeadTag
    
    lead_service = LeadService(db)
    lead = lead_service.get_lead(lead_id)
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check if tag already exists
    existing_tag = db.query(LeadTag).filter(
        LeadTag.lead_id == lead_id,
        LeadTag.tag == tag
    ).first()
    
    if existing_tag:
        return {"message": "Tag already exists", "tag": tag}
    
    # Create new tag
    lead_tag = LeadTag(lead_id=lead_id, tag=tag)
    db.add(lead_tag)
    db.commit()
    
    return {"message": "Tag added successfully", "tag": tag}


@router.delete("/{lead_id}/tags/{tag}")
async def remove_lead_tag(
    lead_id: UUID,
    tag: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a tag from a lead."""
    from ..models.lead_tag import LeadTag
    
    lead_service = LeadService(db)
    lead = lead_service.get_lead(lead_id)
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Find and delete tag
    lead_tag = db.query(LeadTag).filter(
        LeadTag.lead_id == lead_id,
        LeadTag.tag == tag
    ).first()
    
    if not lead_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    db.delete(lead_tag)
    db.commit()
    
    return {"message": "Tag removed successfully"}


@router.get("/{lead_id}/tags")
async def get_lead_tags(
    lead_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all tags for a lead."""
    from ..models.lead_tag import LeadTag
    
    lead_service = LeadService(db)
    lead = lead_service.get_lead(lead_id)
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    tags = db.query(LeadTag).filter(LeadTag.lead_id == lead_id).all()
    
    return {
        "lead_id": str(lead_id),
        "tags": [tag.tag for tag in tags]
    }


@router.post("/bulk/tags", status_code=status.HTTP_202_ACCEPTED)
async def bulk_add_tags(
    lead_ids: List[UUID],
    tags: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add tags to multiple leads in bulk."""
    from ..models.lead_tag import LeadTag
    
    if not lead_ids or not tags:
        raise HTTPException(status_code=400, detail="lead_ids and tags are required")
    
    # Verify leads exist
    lead_service = LeadService(db)
    added_count = 0
    
    for lead_id in lead_ids:
        lead = lead_service.get_lead(lead_id)
        if not lead:
            continue
        
        for tag in tags:
            # Check if tag exists
            existing = db.query(LeadTag).filter(
                LeadTag.lead_id == lead_id,
                LeadTag.tag == tag
            ).first()
            
            if not existing:
                lead_tag = LeadTag(lead_id=lead_id, tag=tag)
                db.add(lead_tag)
                added_count += 1
    
    db.commit()
    
    return {
        "message": "Bulk tag operation completed",
        "leads_processed": len(lead_ids),
        "tags_added": added_count
    }
