"""Quota enforcement service for email sending limits."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from uuid import UUID
import logging

from app.models.org_quota import OrgQuota
from app.models.sending_log import SendingLog

logger = logging.getLogger(__name__)


class QuotaExceededError(Exception):
    """Raised when organization exceeds email sending quota."""
    pass


def get_or_create_quota(db: Session, org_id: UUID) -> OrgQuota:
    """
    Get or create quota record for organization.
    Creates default quota if not exists.
    """
    quota = db.query(OrgQuota).filter(OrgQuota.org_id == org_id).first()
    
    if not quota:
        # Create default quota: 500 emails per day
        quota = OrgQuota(
            org_id=org_id,
            emails_sent_this_period=0,
            period_start=datetime.utcnow(),
            email_limit_per_period=500,
            period_type="daily"
        )
        db.add(quota)
        db.commit()
        db.refresh(quota)
        logger.info(f"Created default quota for org {org_id}: 500 emails/day")
    
    return quota


def check_and_reset_quota(db: Session, org_id: UUID) -> OrgQuota:
    """
    Check if quota period has expired and reset if needed.
    Returns current quota record.
    """
    quota = get_or_create_quota(db, org_id)
    
    now = datetime.utcnow()
    period_duration = timedelta(days=1) if quota.period_type == "daily" else timedelta(days=30)
    period_end = quota.period_start + period_duration
    
    # Reset quota if period has expired
    if now >= period_end:
        logger.info(f"Resetting quota for org {org_id}. Previous period: {quota.emails_sent_this_period}/{quota.email_limit_per_period}")
        quota.emails_sent_this_period = 0
        quota.period_start = now
        db.commit()
        db.refresh(quota)
    
    return quota


def check_quota_available(db: Session, org_id: UUID, emails_to_send: int = 1) -> bool:
    """
    Check if organization has quota available to send emails.
    Returns True if quota is available, False otherwise.
    """
    quota = check_and_reset_quota(db, org_id)
    
    emails_remaining = quota.email_limit_per_period - quota.emails_sent_this_period
    return emails_remaining >= emails_to_send


def enforce_quota(db: Session, org_id: UUID, emails_to_send: int = 1) -> OrgQuota:
    """
    Enforce quota before sending emails.
    Raises QuotaExceededError if quota is exceeded.
    Returns quota record if check passes.
    """
    quota = check_and_reset_quota(db, org_id)
    
    if quota.is_quota_exceeded:
        raise QuotaExceededError(
            f"Organization has exceeded email quota: {quota.emails_sent_this_period}/{quota.email_limit_per_period} for this {quota.period_type} period"
        )
    
    emails_remaining = quota.email_limit_per_period - quota.emails_sent_this_period
    
    if emails_to_send > emails_remaining:
        raise QuotaExceededError(
            f"Insufficient quota: requested {emails_to_send}, available {emails_remaining}"
        )
    
    return quota


def increment_quota_usage(db: Session, org_id: UUID, emails_sent: int = 1) -> OrgQuota:
    """
    Increment quota usage after successfully sending emails.
    Should be called after emails are sent.
    """
    quota = check_and_reset_quota(db, org_id)
    
    quota.emails_sent_this_period += emails_sent
    db.commit()
    db.refresh(quota)
    
    logger.info(f"Incremented quota for org {org_id}: {quota.emails_sent_this_period}/{quota.email_limit_per_period} ({quota.usage_percentage:.1f}%)")
    
    return quota


def get_quota_status(db: Session, org_id: UUID) -> dict:
    """
    Get current quota status for organization.
    Returns dict with quota details.
    """
    quota = check_and_reset_quota(db, org_id)
    
    return {
        "org_id": str(org_id),
        "emails_sent": quota.emails_sent_this_period,
        "email_limit": quota.email_limit_per_period,
        "emails_remaining": quota.emails_remaining,
        "period_type": quota.period_type,
        "period_start": quota.period_start.isoformat(),
        "usage_percentage": round(quota.usage_percentage, 2),
        "is_exceeded": quota.is_quota_exceeded
    }


def update_quota_limit(db: Session, org_id: UUID, new_limit: int, period_type: str = "daily") -> OrgQuota:
    """
    Update quota limit for organization.
    Admin function to adjust limits.
    """
    quota = get_or_create_quota(db, org_id)
    
    old_limit = quota.email_limit_per_period
    quota.email_limit_per_period = new_limit
    quota.period_type = period_type
    
    db.commit()
    db.refresh(quota)
    
    logger.info(f"Updated quota for org {org_id}: {old_limit} -> {new_limit} emails/{period_type}")
    
    return quota
