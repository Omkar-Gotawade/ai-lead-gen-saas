"""Campaign send safety guards (daily warmup caps, DNC checks)."""
from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.campaign import Campaign, CampaignStatus
from app.models.campaign_lead import CampaignLead, CampaignLeadStatus
from app.models.sending_log import SendingLog, SendStatus


STRICT_SAFE_MODE_CAP_WARMUP = 30
STRICT_SAFE_MODE_CAP_STABLE = 60


def warmup_limit_for_user(day: int) -> int:
    """Warmup function: day1=10, +5/day, cap=200."""
    if day <= 1:
        return 10
    return min(10 + (day - 1) * 5, 200)


def get_user_day_number(db: Session, user_id: UUID) -> int:
    first_sent = db.query(func.min(SendingLog.sent_at)).filter(
        SendingLog.user_id == user_id,
        SendingLog.status == SendStatus.SENT,
        SendingLog.sent_at.isnot(None),
    ).scalar()

    if not first_sent:
        return 1

    delta = datetime.utcnow().date() - first_sent.date()
    return max(delta.days + 1, 1)


def sent_today_count(db: Session, user_id: UUID) -> int:
    today = datetime.utcnow().date()
    return db.query(SendingLog).filter(
        SendingLog.user_id == user_id,
        SendingLog.status == SendStatus.SENT,
        func.date(SendingLog.sent_at) == today,
    ).count()


def strict_safe_mode_daily_cap(db: Session, user_id: UUID) -> int:
    """Return strict safe-mode daily cap for autopilot splitting.

    - Day 1-14: 30/day
    - Day 15+: 60/day
    """
    day = get_user_day_number(db, user_id)
    if day <= 14:
        return STRICT_SAFE_MODE_CAP_WARMUP
    return STRICT_SAFE_MODE_CAP_STABLE


def next_utc_day_window_start(now: Optional[datetime] = None) -> datetime:
    """Return next UTC day start plus a small offset for queue smoothing."""
    ts = now or datetime.utcnow()
    next_day = (ts + timedelta(days=1)).date()
    return datetime.combine(next_day, datetime.min.time()) + timedelta(minutes=5)


def enforce_campaign_send_limit(db: Session, campaign_id: UUID, campaign_lead_id: UUID, user_id: UUID) -> Optional[datetime]:
    """Defer sends to next day when strict safe-mode daily cap is reached.

    Returns:
        datetime for deferred retry window when capped, otherwise None.
    """
    limit = strict_safe_mode_daily_cap(db, user_id)
    sent_today = sent_today_count(db, user_id)

    if sent_today >= limit:
        deferred_until = next_utc_day_window_start()

        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        campaign_lead = db.query(CampaignLead).filter(CampaignLead.id == campaign_lead_id).first()

        if campaign:
            campaign.status = CampaignStatus.ACTIVE
        if campaign_lead:
            campaign_lead.status = CampaignLeadStatus.PENDING.value
            campaign_lead.next_run_at = deferred_until
            campaign_lead.stop_reason = "deferred_daily_quota"

        db.commit()
        return deferred_until

    return None
