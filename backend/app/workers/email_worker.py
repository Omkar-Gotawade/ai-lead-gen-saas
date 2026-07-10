"""Celery tasks for email sending."""
from typing import Optional
from uuid import UUID
from datetime import datetime
import random
import time
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.email_provider import EmailProviderSettings
from app.models.lead import Lead
from app.models.sending_log import SendingLog, SendStatus
from app.services.email_sender import send_email
from app.services.redis_service import RedisService
import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    name="send_email_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def send_email_task(
    self,
    user_id: str,
    to_email: str,
    subject: str,
    body: str,
    lead_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    step_index: Optional[int] = None,
    in_reply_to: Optional[str] = None,
    references: Optional[str] = None,
):
    """
    Celery task to send an email with duplicate prevention and threading support.

    This task is idempotent - calling it multiple times with the same
    parameters will only send the email once.

    Threading: when in_reply_to is supplied, the email is sent as a reply inside
    the same conversation thread (In-Reply-To + References headers set).  When
    in_reply_to is None the email is sent as a fresh message — full backward compat.

    Args:
        user_id:      User ID
        to_email:     Recipient email address
        subject:      Email subject
        body:         Email body
        lead_id:      Optional lead ID for tracking
        campaign_id:  Campaign ID (for threading lookup on subsequent steps)
        step_index:   Sequence step number (for threading lookup)
        in_reply_to:  Message-ID of the root email to thread against
        references:   References header (same as in_reply_to for single-anchor threading)
    """
    db = SessionLocal()

    try:
        # Generate unique message_id for deduplication
        context_parts = []
        if campaign_id:
            context_parts.append(f"campaign:{campaign_id}")
        if step_index is not None:
            context_parts.append(f"step:{step_index}")

        message_id = RedisService.generate_message_id(
            user_id=user_id,
            lead_id=lead_id or "none",
            subject=subject,
            body=body,
            context="|".join(context_parts),
        )

        logger.info(
            "Processing email task: message_id=%s, to=%s, step=%s, threading=%s",
            message_id, to_email, step_index,
            "yes" if in_reply_to else "no",
        )

        # Check for duplicate using Redis (atomic check-and-set)
        can_send = RedisService.check_and_mark_sent(message_id)

        if not can_send:
            logger.warning("Duplicate send prevented: message_id=%s, to=%s", message_id, to_email)
            existing_log = db.query(SendingLog).filter(
                SendingLog.message_id == message_id,
                SendingLog.status == SendStatus.SENT,
            ).first()

            if existing_log:
                logger.info("Email already sent successfully: %s", message_id)
                return {"status": "duplicate", "message_id": message_id}
            else:
                logger.info("Redis marked as duplicate but no successful send found - allowing retry")
                RedisService.clear_sent_message(message_id)

        # Database-level check (fallback if Redis is unavailable)
        existing_db_log = db.query(SendingLog).filter(
            SendingLog.message_id == message_id,
        ).first()

        if existing_db_log:
            if existing_db_log.status == SendStatus.SENT:
                logger.warning("Duplicate found in database: %s", message_id)
                return {"status": "duplicate_db", "message_id": message_id}
            else:
                logger.info("Retrying previously failed send: %s", message_id)

        # Get user's email provider settings
        provider = db.query(EmailProviderSettings).filter(
            EmailProviderSettings.user_id == UUID(user_id),
        ).first()

        # Fallback to any configured provider
        if not provider:
            provider = db.query(EmailProviderSettings).first()

        if not provider:
            raise Exception("Email provider not configured")

        # Load lead and enforce DNC before any send attempt
        lead = None
        if lead_id:
            lead = db.query(Lead).filter(Lead.id == UUID(lead_id)).first()
            if lead and (lead.do_not_contact or lead.is_do_not_contact):
                logger.warning("Blocked send to DNC lead %s", lead.id)
                if existing_db_log:
                    existing_db_log.status = SendStatus.FAILED
                    existing_db_log.error_message = "Blocked by do-not-contact policy"
                    existing_db_log.failed_at = datetime.utcnow()
                    existing_db_log.retry_count = self.request.retries
                    db.commit()
                return {"status": "blocked_dnc", "message_id": message_id}

        # Create sending log if it doesn't exist
        if not existing_db_log:
            log = SendingLog(
                user_id=UUID(user_id),
                lead_id=UUID(lead_id) if lead_id else None,
                campaign_id=UUID(campaign_id) if campaign_id else None,
                step_index=step_index,
                provider_type=provider.provider_type.value,
                to_email=to_email,
                subject=subject,
                body=body,
                message_id=message_id,
                status=SendStatus.QUEUED,
                retry_count=self.request.retries,
            )
            db.add(log)
            db.commit()
            db.refresh(log)
        else:
            log = existing_db_log
            log.status = SendStatus.QUEUED
            log.retry_count = self.request.retries
            # Backfill threading columns on retry if missing
            if campaign_id and log.campaign_id is None:
                log.campaign_id = UUID(campaign_id)
            if step_index is not None and log.step_index is None:
                log.step_index = step_index
            db.commit()

        try:
            # Rate control jitter to reduce bursty send patterns.
            time.sleep(random.randint(30, 90))

            # Send email — provider returns the outgoing Message-ID
            outgoing_message_id = send_email(
                provider_settings=provider,
                to_email=to_email,
                subject=subject,
                body=body,
                in_reply_to=in_reply_to,
                references=references,
            )

            # Update log: store the real outgoing Message-ID so subsequent steps
            # can look it up as the thread anchor (step 1 only — don't overwrite
            # the deduplication key for follow-ups which already have a message_id).
            log.status = SendStatus.SENT
            log.sent_at = datetime.utcnow()
            if outgoing_message_id and step_index == 1:
                # For the root email we want the actual SMTP Message-ID as the anchor.
                # Update only if different from the deduplication hash.
                if log.message_id != outgoing_message_id:
                    # Check no other row already owns this outgoing id
                    collision = db.query(SendingLog).filter(
                        SendingLog.message_id == outgoing_message_id,
                        SendingLog.id != log.id,
                    ).first()
                    if not collision:
                        log.message_id = outgoing_message_id
            db.commit()

            logger.info(
                "Email sent successfully: message_id=%s, to=%s, step=%s",
                log.message_id, to_email, step_index,
            )

            return {"status": "sent", "message_id": log.message_id}

        except Exception as e:
            log.status = SendStatus.FAILED
            log.error_message = str(e)
            log.retry_count = self.request.retries
            log.failed_at = datetime.utcnow()
            db.commit()

            # Clear Redis marker to allow retry
            RedisService.clear_sent_message(message_id)

            logger.error("Email send failed: message_id=%s, error=%s", message_id, str(e))
            raise

    except Exception as e:
        # Dead-letter style terminal marking when retries are exhausted
        if self.request.retries >= self.max_retries:
            try:
                log = db.query(SendingLog).filter(SendingLog.message_id == message_id).first()
                if log:
                    log.status = SendStatus.FAILED
                    log.error_message = f"Retries exhausted: {str(e)}"
                    log.retry_count = self.request.retries
                    log.failed_at = datetime.utcnow()
                    db.commit()
            except Exception:
                db.rollback()
        logger.error("Email task error: %s", str(e))
        raise
    finally:
        db.close()
