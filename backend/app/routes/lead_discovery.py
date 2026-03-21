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
from ..models.user import User
from ..schemas.lead_discovery import (
    LeadDiscoveryStartRequest,
    LeadDiscoveryJobResponse,
    LeadDiscoveryStatusResponse,
    DiscoveredDomainResponse
)
from ..workers.lead_discovery_worker import run_lead_discovery
from ..routes.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lead-discovery", tags=["lead-discovery"])


@router.post("/start", response_model=LeadDiscoveryJobResponse, status_code=status.HTTP_201_CREATED)
async def start_lead_discovery(
    request: LeadDiscoveryStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a new lead discovery job.

    Automatically selects the best available source:
      1. Apollo.io  (if APOLLO_API_KEY is configured)
      2. Hunter.io  (if HUNTER_API_KEY is configured)
      3. SERP + website crawl (fallback)
    """
    try:
        job = LeadDiscoveryJob(
            id=uuid.uuid4(),
            user_id=current_user.id,
            org_id=current_user.id,
            keywords=request.keywords,
            location=request.location,
            industry=request.industry,
            status="pending",
            domains_found=0,
            domains_crawled=0,
            leads_created=0,
            created_at=datetime.utcnow(),
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        try:
            run_lead_discovery.delay(str(job.id), max_results=request.max_results or 25)
            logger.info("Enqueued lead discovery job %s for user %s", job.id, current_user.id)
        except Exception as e:
            logger.error("Failed to enqueue Celery task: %s", e)
            job.status = "failed"
            job.error_message = f"Failed to start background task: {e}"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start discovery task",
            )

        return job

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create lead discovery job: %s", e)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create discovery job: {e}",
        )


@router.get("/{job_id}", response_model=LeadDiscoveryStatusResponse)
async def get_lead_discovery_status(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the status and preview results of a lead discovery job."""
    job = db.query(LeadDiscoveryJob).filter(
        LeadDiscoveryJob.id == job_id,
        LeadDiscoveryJob.user_id == current_user.id,
    ).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Discovery job {job_id} not found")

    domains = db.query(DiscoveredDomain).filter(
        DiscoveredDomain.discovery_job_id == job_id
    ).order_by(DiscoveredDomain.created_at.desc()).limit(100).all()

    progress_percent = 0
    if job.domains_found > 0:
        progress_percent = min(100, int((job.domains_crawled / job.domains_found) * 100))

    return LeadDiscoveryStatusResponse(
        job=LeadDiscoveryJobResponse.from_orm(job),
        discovered_domains=[DiscoveredDomainResponse.from_orm(d) for d in domains],
        progress_percent=progress_percent,
    )


@router.get("/", response_model=List[LeadDiscoveryJobResponse])
async def list_discovery_jobs(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List the current user's lead discovery jobs (newest first)."""
    jobs = db.query(LeadDiscoveryJob).filter(
        LeadDiscoveryJob.user_id == current_user.id
    ).order_by(LeadDiscoveryJob.created_at.desc()).limit(limit).offset(offset).all()
    return jobs


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discovery_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a lead discovery job and its discovered domain / person records.

    Note: this does NOT delete the leads that were created from this job.
    """
    job = db.query(LeadDiscoveryJob).filter(
        LeadDiscoveryJob.id == job_id,
        LeadDiscoveryJob.user_id == current_user.id,
    ).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Discovery job {job_id} not found")

    db.query(DiscoveredDomain).filter(
        DiscoveredDomain.discovery_job_id == job_id
    ).delete()
    db.delete(job)
    db.commit()
    logger.info("Deleted lead discovery job %s", job_id)
