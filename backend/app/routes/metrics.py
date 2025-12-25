"""Metrics API endpoints for analytics and reporting."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional, List
from datetime import datetime, date, timedelta
from uuid import UUID
import logging

from app.database import get_db
from app.models.user import User
from app.models.sending_log import SendingLog, SendStatus
from app.models.inbound_event import InboundEvent
from app.models.lead import Lead
from app.models.campaign_lead import CampaignLead
from app.services.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)


class MetricsOverview(BaseModel):
    """Overview metrics response."""
    emails_sent: int
    emails_delivered: int
    replies: int
    reply_rate: float
    bounces: int
    bounce_rate: float
    unique_leads_contacted: int
    period_start: date
    period_end: date


class TimelineDataPoint(BaseModel):
    """Single data point for timeline chart."""
    date: str
    sent: int
    replies: int
    bounces: int
    delivered: int


class TimelineResponse(BaseModel):
    """Timeline metrics response."""
    data: List[TimelineDataPoint]
    period: str
    total_sent: int
    total_replies: int
    total_bounces: int


@router.get("/metrics/org/{org_id}/overview", response_model=MetricsOverview)
async def get_metrics_overview(
    org_id: UUID,
    since: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    until: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get overview metrics for an organization.
    
    Returns totals for:
    - Emails sent
    - Emails delivered (from provider events)
    - Replies received
    - Reply rate
    - Bounces
    - Bounce rate
    - Unique leads contacted
    """
    # Verify user has access to this org
    if str(current_user.id) != str(org_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Set default date range (last 30 days)
    if not until:
        until = date.today()
    if not since:
        since = until - timedelta(days=30)
    
    # Convert dates to datetime for queries
    start_dt = datetime.combine(since, datetime.min.time())
    end_dt = datetime.combine(until, datetime.max.time())
    
    # Query sent emails
    emails_sent = db.query(func.count(SendingLog.id)).filter(
        SendingLog.user_id == org_id,
        SendingLog.created_at >= start_dt,
        SendingLog.created_at <= end_dt,
        SendingLog.status.in_([SendStatus.SENT, SendStatus.FAILED])
    ).scalar() or 0
    
    # Query delivered emails (from sending_logs with sent status)
    emails_delivered = db.query(func.count(SendingLog.id)).filter(
        SendingLog.user_id == org_id,
        SendingLog.created_at >= start_dt,
        SendingLog.created_at <= end_dt,
        SendingLog.status == SendStatus.SENT
    ).scalar() or 0
    
    # Query replies (from inbound_events)
    replies = db.query(func.count(InboundEvent.id)).filter(
        InboundEvent.org_id == org_id,
        InboundEvent.created_at >= start_dt,
        InboundEvent.created_at <= end_dt,
        InboundEvent.event_type == 'reply'
    ).scalar() or 0
    
    # Query bounces
    bounces = db.query(func.count(InboundEvent.id)).filter(
        InboundEvent.org_id == org_id,
        InboundEvent.created_at >= start_dt,
        InboundEvent.created_at <= end_dt,
        InboundEvent.event_type == 'bounce'
    ).scalar() or 0
    
    # Query unique leads contacted
    unique_leads = db.query(func.count(func.distinct(SendingLog.lead_id))).filter(
        SendingLog.user_id == org_id,
        SendingLog.created_at >= start_dt,
        SendingLog.created_at <= end_dt
    ).scalar() or 0
    
    # Calculate rates
    reply_rate = (replies / emails_sent * 100) if emails_sent > 0 else 0.0
    bounce_rate = (bounces / emails_sent * 100) if emails_sent > 0 else 0.0
    
    return MetricsOverview(
        emails_sent=emails_sent,
        emails_delivered=emails_delivered,
        replies=replies,
        reply_rate=round(reply_rate, 2),
        bounces=bounces,
        bounce_rate=round(bounce_rate, 2),
        unique_leads_contacted=unique_leads,
        period_start=since,
        period_end=until
    )


@router.get("/metrics/org/{org_id}/timeline", response_model=TimelineResponse)
async def get_metrics_timeline(
    org_id: UUID,
    period: str = Query("daily", regex="^(daily|weekly)$"),
    since: Optional[date] = Query(None),
    until: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get timeline metrics for charting.
    
    Returns daily or weekly aggregated data for:
    - Emails sent
    - Replies
    - Bounces
    - Delivered
    """
    # Verify access
    if str(current_user.id) != str(org_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Set default date range
    if not until:
        until = date.today()
    if not since:
        since = until - timedelta(days=30 if period == "daily" else 90)
    
    start_dt = datetime.combine(since, datetime.min.time())
    end_dt = datetime.combine(until, datetime.max.time())
    
    # Determine date truncation based on period
    if period == "daily":
        date_trunc = func.date_trunc('day', SendingLog.created_at)
    else:  # weekly
        date_trunc = func.date_trunc('week', SendingLog.created_at)
    
    # Query sent emails by date
    sent_by_date = db.query(
        func.date(date_trunc).label('date'),
        func.count(SendingLog.id).label('count')
    ).filter(
        SendingLog.user_id == org_id,
        SendingLog.created_at >= start_dt,
        SendingLog.created_at <= end_dt
    ).group_by(func.date(date_trunc)).all()
    
    # Query replies by date
    reply_date_trunc = func.date_trunc('day' if period == "daily" else 'week', InboundEvent.created_at)
    replies_by_date = db.query(
        func.date(reply_date_trunc).label('date'),
        func.count(InboundEvent.id).label('count')
    ).filter(
        InboundEvent.org_id == org_id,
        InboundEvent.created_at >= start_dt,
        InboundEvent.created_at <= end_dt,
        InboundEvent.event_type == 'reply'
    ).group_by(func.date(reply_date_trunc)).all()
    
    # Query bounces by date
    bounces_by_date = db.query(
        func.date(reply_date_trunc).label('date'),
        func.count(InboundEvent.id).label('count')
    ).filter(
        InboundEvent.org_id == org_id,
        InboundEvent.created_at >= start_dt,
        InboundEvent.created_at <= end_dt,
        InboundEvent.event_type == 'bounce'
    ).group_by(func.date(reply_date_trunc)).all()
    
    # Query delivered by date
    delivered_by_date = db.query(
        func.date(date_trunc).label('date'),
        func.count(SendingLog.id).label('count')
    ).filter(
        SendingLog.user_id == org_id,
        SendingLog.created_at >= start_dt,
        SendingLog.created_at <= end_dt,
        SendingLog.status == SendStatus.SENT
    ).group_by(func.date(date_trunc)).all()
    
    # Convert to dictionaries for easy lookup
    sent_dict = {str(row.date): row.count for row in sent_by_date}
    replies_dict = {str(row.date): row.count for row in replies_by_date}
    bounces_dict = {str(row.date): row.count for row in bounces_by_date}
    delivered_dict = {str(row.date): row.count for row in delivered_by_date}
    
    # Generate all dates in range
    current_date = since
    timeline_data = []
    total_sent = 0
    total_replies = 0
    total_bounces = 0
    
    while current_date <= until:
        date_str = str(current_date)
        sent = sent_dict.get(date_str, 0)
        replies = replies_dict.get(date_str, 0)
        bounces = bounces_dict.get(date_str, 0)
        delivered = delivered_dict.get(date_str, 0)
        
        timeline_data.append(TimelineDataPoint(
            date=date_str,
            sent=sent,
            replies=replies,
            bounces=bounces,
            delivered=delivered
        ))
        
        total_sent += sent
        total_replies += replies
        total_bounces += bounces
        
        # Increment date
        if period == "daily":
            current_date += timedelta(days=1)
        else:  # weekly
            current_date += timedelta(weeks=1)
    
    return TimelineResponse(
        data=timeline_data,
        period=period,
        total_sent=total_sent,
        total_replies=total_replies,
        total_bounces=total_bounces
    )


@router.get("/metrics/campaign/{campaign_id}/stats")
async def get_campaign_stats(
    campaign_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get metrics for a specific campaign.
    """
    # Query campaign leads stats
    total_leads = db.query(func.count(CampaignLead.id)).filter(
        CampaignLead.campaign_id == campaign_id
    ).scalar() or 0
    
    replied_leads = db.query(func.count(CampaignLead.id)).filter(
        CampaignLead.campaign_id == campaign_id,
        CampaignLead.replied_at.isnot(None)
    ).scalar() or 0
    
    stopped_leads = db.query(func.count(CampaignLead.id)).filter(
        CampaignLead.campaign_id == campaign_id,
        CampaignLead.status == 'stopped'
    ).scalar() or 0
    
    completed_leads = db.query(func.count(CampaignLead.id)).filter(
        CampaignLead.campaign_id == campaign_id,
        CampaignLead.status == 'completed'
    ).scalar() or 0
    
    return {
        "campaign_id": str(campaign_id),
        "total_leads": total_leads,
        "replied_leads": replied_leads,
        "stopped_leads": stopped_leads,
        "completed_leads": completed_leads,
        "reply_rate": round((replied_leads / total_leads * 100) if total_leads > 0 else 0, 2)
    }
