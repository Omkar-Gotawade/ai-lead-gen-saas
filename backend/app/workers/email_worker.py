"""Celery tasks for email sending."""
from typing import Optional
from uuid import UUID
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.email_provider import EmailProviderSettings
from app.models.lead import Lead
from app.models.sending_log import SendingLog, SendStatus
from app.services.email_sender import send_email


@celery_app.task(name="send_email_task")
def send_email_task(
    user_id: str,
    to_email: str,
    subject: str,
    body: str,
    lead_id: Optional[str] = None
):
    """
    Celery task to send an email.
    
    Args:
        user_id: User ID
        to_email: Recipient email address
        subject: Email subject
        body: Email body
        lead_id: Optional lead ID for tracking
    """
    db = SessionLocal()
    
    try:
        # Get user's email provider settings
        provider = db.query(EmailProviderSettings).filter(
            EmailProviderSettings.user_id == UUID(user_id)
        ).first()
        
        if not provider:
            raise Exception("Email provider not configured")
        
        # Create sending log
        log = SendingLog(
            user_id=UUID(user_id),
            lead_id=UUID(lead_id) if lead_id else None,
            provider_type=provider.provider_type.value,
            to_email=to_email,
            subject=subject,
            status=SendStatus.QUEUED
        )
        db.add(log)
        db.commit()
        
        try:
            # Send email
            send_email(
                provider_settings=provider,
                to_email=to_email,
                subject=subject,
                body=body
            )
            
            # Update log as sent
            log.status = SendStatus.SENT
            db.commit()
            
        except Exception as e:
            # Update log as failed
            log.status = SendStatus.FAILED
            log.error_message = str(e)
            db.commit()
            raise
            
    finally:
        db.close()
