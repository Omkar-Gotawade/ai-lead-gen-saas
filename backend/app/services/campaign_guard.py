"""Campaign send safety guards (daily warmup caps, DNC checks)."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.campaign import Campaign, CampaignStatus
from app.models.campaign_lead import CampaignLead, CampaignLeadStatus
from app.models.sending_log import SendingLog, SendStatus


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


def enforce_campaign_send_limit(db: Session, campaign_id: UUID, campaign_lead_id: UUID, user_id: UUID) -> None:
    """Pause campaign lead if user has reached daily warmup limit."""
    day = get_user_day_number(db, user_id)
    limit = warmup_limit_for_user(day)
    sent_today = sent_today_count(db, user_id)

    if sent_today >= limit:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        campaign_lead = db.query(CampaignLead).filter(CampaignLead.id == campaign_lead_id).first()

        if campaign:
            campaign.status = CampaignStatus.PAUSED
        if campaign_lead:
            campaign_lead.status = CampaignLeadStatus.STOPPED.value
            campaign_lead.stop_reason = "Daily limit reached"

        db.commit()
