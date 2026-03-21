"""Celery tasks for email sending."""
from typing import Optional
from uuid import UUID
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.email_provider import EmailProviderSettings
from app.models.lead import Lead
from app.models.sending_log import SendingLog, SendStatus
from app.services.email_sender import send_email
from app.services.redis_service import RedisService
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="send_email_task", bind=True, max_retries=3)
def send_email_task(
    self,
    user_id: str,
    to_email: str,
    subject: str,
    body: str,
    lead_id: Optional[str] = None
):
    """
    Celery task to send an email with duplicate prevention.

    This task is idempotent - calling it multiple times with the same
    parameters will only send the email once.

    Args:
        user_id: User ID
        to_email: Recipient email address
        subject: Email subject
        body: Email body
        lead_id: Optional lead ID for tracking
    """
    db = SessionLocal()

    try:
        # Generate unique message_id for deduplication
        message_id = RedisService.generate_message_id(
            user_id=user_id,
            lead_id=lead_id or "none",
            subject=subject,
            body=body
        )

        logger.info(f"Processing email task: message_id={message_id}, to={to_email}")

        # Check for duplicate using Redis (atomic check-and-set)
        can_send = RedisService.check_and_mark_sent(message_id)

        if not can_send:
            logger.warning(f"Duplicate send prevented: message_id={message_id}, to={to_email}")
            # Check if we already have a successful send in database
            existing_log = db.query(SendingLog).filter(
                SendingLog.message_id == message_id,
                SendingLog.status == SendStatus.SENT
            ).first()

            if existing_log:
                logger.info(f"Email already sent successfully: {message_id}")
                return {"status": "duplicate", "message_id": message_id}
            else:
                # Redis says duplicate but no successful DB record - could be retry of failed send
                logger.info(f"Redis marked as duplicate but no successful send found - allowing retry")
                # Clear Redis and allow send
                RedisService.clear_sent_message(message_id)

        # Database-level check (fallback if Redis is unavailable)
        existing_db_log = db.query(SendingLog).filter(
            SendingLog.message_id == message_id
        ).first()

        if existing_db_log:
            if existing_db_log.status == SendStatus.SENT:
                logger.warning(f"Duplicate found in database: {message_id}")
                return {"status": "duplicate_db", "message_id": message_id}
            else:
                logger.info(f"Retrying previously failed send: {message_id}")

        # Get user's email provider settings
        provider = db.query(EmailProviderSettings).filter(
            EmailProviderSettings.user_id == UUID(user_id)
        ).first()

        # Fallback to any configured provider
        if not provider:
            provider = db.query(EmailProviderSettings).first()

        if not provider:
            raise Exception("Email provider not configured")

        # Create sending log if doesn't exist
        if not existing_db_log:
            log = SendingLog(
                user_id=UUID(user_id),
                lead_id=UUID(lead_id) if lead_id else None,
                provider_type=provider.provider_type.value,
                to_email=to_email,
                subject=subject,
                message_id=message_id,
                status=SendStatus.QUEUED
            )
            db.add(log)
            db.commit()
            db.refresh(log)
        else:
            log = existing_db_log
            log.status = SendStatus.QUEUED
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

            logger.info(f"Email sent successfully: message_id={message_id}, to={to_email}")

            return {"status": "sent", "message_id": message_id}

        except Exception as e:
            # Update log as failed
            log.status = SendStatus.FAILED
            log.error_message = str(e)
            db.commit()

            # Clear Redis marker to allow retry
            RedisService.clear_sent_message(message_id)

            logger.error(f"Email send failed: message_id={message_id}, error={str(e)}")

            # Retry the task
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))

    except Exception as e:
        logger.error(f"Email task error: {str(e)}")
        raise
    finally:
        db.close()
