"""Email sending routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.lead import Lead
from app.models.sending_log import SendingLog
from app.schemas.email import EmailSendRequest, EmailSendResponse, EmailTestRequest
from app.services.auth import get_current_user
from app.services.rate_limiter import enforce_rate_limit
from app.workers.email_worker import send_email_task

router = APIRouter()


@router.post("/email/send", response_model=EmailSendResponse)
async def send_email_endpoint(
    request: EmailSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Queue an email to be sent via Celery worker.
    
    Args:
        request: Email send request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Response indicating email was queued
    """
    enforce_rate_limit("campaign_send", str(current_user.id))

    # Fetch the lead
    lead = db.query(Lead).filter(
        Lead.id == request.lead_id,
        Lead.org_id == current_user.id
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Enqueue email send task
    send_email_task.delay(
        user_id=str(current_user.id),
        to_email=lead.email,
        subject=request.subject,
        body=request.body,
        lead_id=str(lead.id)
    )
    
    return EmailSendResponse(
        queued=True,
        message="Email queued for sending"
    )


@router.post("/email/send-test")
async def send_test_email_endpoint(
    request: EmailTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a test email immediately (via Celery).
    
    Args:
        request: Test email request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Response indicating email was queued
    """
    enforce_rate_limit("campaign_send", str(current_user.id))

    # Enqueue test email
    send_email_task.delay(
        user_id=str(current_user.id),
        to_email=request.to_email,
        subject=request.subject,
        body=request.body,
        lead_id=None
    )
    
    return {"queued": True, "message": "Test email queued for sending"}


@router.get("/email/logs")
async def get_email_logs(
    lead_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get email sending logs.
    
    Args:
        lead_id: Optional lead ID to filter by
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of sending logs
    """
    query = db.query(SendingLog).filter(
        SendingLog.user_id == current_user.id
    )
    
    if lead_id:
        query = query.filter(SendingLog.lead_id == lead_id)
    
    logs = query.order_by(SendingLog.created_at.desc()).limit(100).all()
    
    return {
        "logs": [
            {
                "id": str(log.id),
                "lead_id": str(log.lead_id) if log.lead_id else None,
                "to_email": log.to_email,
                "subject": log.subject,
                "status": log.status.value,
                "error_message": log.error_message,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ]
    }
