"""API routes for Lead Discovery feature."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from ..database import get_db
from ..models.lead_discovery_job import LeadDiscoveryJob
from ..models.discovered_domain import DiscoveredDomain
from ..models.lead import Lead
from ..schemas.lead_discovery import (
    LeadDiscoveryStartRequest,
    LeadDiscoveryJobResponse,
    LeadDiscoveryStatusResponse,
    DiscoveredDomainResponse
)
from ..workers.lead_discovery_worker import run_lead_discovery
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lead-discovery", tags=["lead-discovery"])


@router.post("/start", response_model=LeadDiscoveryJobResponse, status_code=status.HTTP_201_CREATED)
async def start_lead_discovery(
    request: LeadDiscoveryStartRequest,
    db: Session = Depends(get_db)
):
    """Start a new lead discovery job.
    
    This endpoint creates a new lead discovery job and enqueues a background task
    to search for companies, crawl their websites, and create lead records.
    
    Args:
        request: Lead discovery parameters (keywords, location, industry)
        db: Database session
        
    Returns:
        Created job details with job ID for status checking
    """
    try:
        # Create new discovery job
        job = LeadDiscoveryJob(
            id=uuid.uuid4(),
            keywords=request.keywords,
            location=request.location,
            industry=request.industry,
            status="pending",
            domains_found=0,
            domains_crawled=0,
            leads_created=0,
            created_at=datetime.utcnow()
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Enqueue Celery task
        try:
            run_lead_discovery.delay(str(job.id), max_results=request.max_results or 20)
            logger.info(f"Enqueued lead discovery job {job.id}")
        except Exception as e:
            logger.error(f"Failed to enqueue Celery task: {str(e)}")
            # Update job status to failed
            job.status = "failed"
            job.error_message = f"Failed to start background task: {str(e)}"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start discovery task"
            )
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create lead discovery job: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create discovery job: {str(e)}"
        )


@router.get("/{job_id}", response_model=LeadDiscoveryStatusResponse)
async def get_lead_discovery_status(
    job_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get the status of a lead discovery job.
    
    Returns job details, discovered domains, and progress information.
    Poll this endpoint to track job progress.
    
    Args:
        job_id: UUID of the discovery job
        db: Database session
        
    Returns:
        Job status with discovered domains and progress
    """
    # Get job
    job = db.query(LeadDiscoveryJob).filter(LeadDiscoveryJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Discovery job {job_id} not found"
        )
    
    # Get discovered domains (limit to 50 for preview)
    domains = db.query(DiscoveredDomain).filter(
        DiscoveredDomain.discovery_job_id == job_id
    ).limit(50).all()
    
    # Calculate progress
    progress_percent = 0
    if job.domains_found > 0:
        progress_percent = int((job.domains_crawled / job.domains_found) * 100)
    
    return LeadDiscoveryStatusResponse(
        job=LeadDiscoveryJobResponse.from_orm(job),
        discovered_domains=[DiscoveredDomainResponse.from_orm(d) for d in domains],
        progress_percent=progress_percent
    )


@router.get("/", response_model=List[LeadDiscoveryJobResponse])
async def list_discovery_jobs(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List all lead discovery jobs.
    
    Returns a paginated list of discovery jobs, ordered by creation date (newest first).
    
    Args:
        limit: Maximum number of jobs to return
        offset: Number of jobs to skip
        db: Database session
        
    Returns:
        List of discovery jobs
    """
    jobs = db.query(LeadDiscoveryJob).order_by(
        LeadDiscoveryJob.created_at.desc()
    ).limit(limit).offset(offset).all()
    
    return jobs


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discovery_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Delete a lead discovery job and its discovered domains.
    
    Note: This does NOT delete the leads that were created from this job.
    
    Args:
        job_id: UUID of the discovery job
        db: Database session
    """
    job = db.query(LeadDiscoveryJob).filter(LeadDiscoveryJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Discovery job {job_id} not found"
        )
    
    # Delete discovered domains (will cascade due to FK constraint)
    db.query(DiscoveredDomain).filter(
        DiscoveredDomain.discovery_job_id == job_id
    ).delete()
    
    # Delete job
    db.delete(job)
    db.commit()
    
    logger.info(f"Deleted lead discovery job {job_id}")
