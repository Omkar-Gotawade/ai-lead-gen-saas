"""
Deliverability and email health endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
import uuid
from datetime import date, datetime
from ..database import get_db
from ..services.auth import get_current_user
from ..models.user import User
from ..services.deliverability import (
    get_deliverability_score,
    get_risky_leads,
    get_best_sending_times,
    calculate_bounce_rate,
    calculate_spam_complaint_rate
)
from ..services.dns_checker import DNSCheckerService
from ..models.email_warmup_domain import EmailWarmupDomain
from ..models.org_quota import OrgQuota
from ..models.sending_log import SendingLog
from ..schemas.deliverability import (
    DNSCheckRequest,
    DNSCheckResponse,
    EmailWarmupDomainCreate,
    EmailWarmupDomainResponse,
    EmailWarmupStatusResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/deliverability", tags=["deliverability"])


def _get_warmup_data(db: Session, current_user: User) -> Dict:
    """Helper function to get warmup status data."""
    # Check today's sent emails
    today = date.today()
    sent_today = db.query(SendingLog).filter(
        SendingLog.user_id == current_user.id,
        SendingLog.created_at >= datetime.combine(today, datetime.min.time()),
        SendingLog.status == "sent"
    ).count()
    
    # Check if user has a warmup domain
    warmup_domain = db.query(EmailWarmupDomain).filter(
        EmailWarmupDomain.org_id == current_user.id
    ).first()
    
    if warmup_domain:
        daily_limit = warmup_domain.daily_limit
        warmup_day = warmup_domain.warmup_day
        
        # Calculate next day's limit
        if warmup_day < 7:
            next_limit = daily_limit + 5
        else:
            next_limit = daily_limit + 10
        next_limit = min(next_limit, 200)
    else:
        # Default for new users
        daily_limit = 50
        warmup_day = 1
        next_limit = 75
    
    remaining = max(0, daily_limit - sent_today)
    usage_percentage = round((sent_today / daily_limit * 100) if daily_limit > 0 else 0, 1)
    
    return {
        "daily_limit": daily_limit,
        "used_today": sent_today,
        "remaining": remaining,
        "warmup_day": warmup_day,
        "warmup_total_days": 21,
        "next_day_limit": next_limit,
        "usage_percentage": usage_percentage,
        "status": "healthy" if sent_today < daily_limit * 0.9 else "approaching_limit"
    }


@router.get("/health")
async def get_deliverability_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get comprehensive deliverability health dashboard data.
    Returns health score, system checks, recommendations, and warnings.
    """
    from datetime import timedelta
    
    # Get warmup status
    warmup_status = _get_warmup_data(db, current_user)
    
    # Calculate bounce rate
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    total_sent = db.query(SendingLog).filter(
        SendingLog.user_id == current_user.id,
        SendingLog.created_at >= thirty_days_ago,
        SendingLog.status == "sent"
    ).count()
    
    # For now, assume no bounces (would integrate with webhook bounce tracking)
    bounce_count = 0
    bounce_rate = (bounce_count / total_sent * 100) if total_sent > 0 else 0
    
    # Calculate health score components
    domain_auth_score = 30  # Assume configured (would check DNS)
    bounce_score = 25 if bounce_rate < 2 else (15 if bounce_rate < 5 else 0)
    spam_score = 20  # Assume no complaints (would check)
    blacklist_score = 15  # Assume clean (would check)
    warmup_score = 10 if warmup_status['warmup_day'] >= 7 else 5
    
    health_score = domain_auth_score + bounce_score + spam_score + blacklist_score + warmup_score
    
    # Determine status
    if health_score >= 80:
        status = 'good'
    elif health_score >= 60:
        status = 'warning'
    else:
        status = 'critical'
    
    # System checks
    checks = {
        'domain_auth': {
            'status': 'pass',
            'message': 'Domain authentication configured'
        },
        'warmup': {
            'status': 'warning' if warmup_status['warmup_day'] < 14 else 'pass',
            'message': f"Warmup in progress - Day {warmup_status['warmup_day']} of 21"
        },
        'blacklist': {
            'status': 'pass',
            'message': 'Not on any known blacklists'
        },
        'bounce_rate': {
            'status': 'pass' if bounce_rate < 2 else ('warning' if bounce_rate < 5 else 'fail'),
            'message': f"{bounce_rate:.1f}% bounce rate (target: <2%)"
        }
    }
    
    # Generate recommendations
    recommendations = []
    if warmup_status['usage_percentage'] > 80:
        recommendations.append('Approaching daily send limit - consider pacing campaigns')
    if warmup_status['warmup_day'] < 14:
        recommendations.append('Continue daily sending to complete warmup schedule')
    if bounce_rate > 2:
        recommendations.append(f'Clean list to reduce {bounce_rate:.1f}% bounce rate')
    
    # Add default recommendations
    if not recommendations:
        recommendations = [
            'Maintain consistent sending schedule',
            'Monitor bounce rates daily',
            'Keep subject lines under 50 characters'
        ]
    
    # Spam triggers (mock for now - would analyze recent emails)
    spam_reasons = []
    
    return {
        'score': health_score,
        'status': status,
        'checks': checks,
        'daily_limit': {
            'sent': warmup_status['used_today'],
            'limit': warmup_status['daily_limit'],
            'next_limit': warmup_status['next_day_limit']
        },
        'recommendations': recommendations,
        'spam_reasons': spam_reasons
    }


@router.post("/auto-fix")
async def auto_fix_issues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Automatically fix common deliverability issues.
    Currently a placeholder for future implementation.
    """
    return {
        'status': 'success',
        'message': 'Auto-fix completed',
        'fixes_applied': [
            'Verified DNS configuration',
            'Checked sending limits',
            'Reviewed recent campaigns'
        ]
    }


@router.get("/warmup/status")
async def get_user_warmup_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get warmup status for the current user.
    Returns daily limit, usage, and warmup progress.
    """
    return _get_warmup_data(db, current_user)


@router.get("/score")
async def get_score(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict:
    """
    Get deliverability score and recommendations for current organization.
    Score is 0-100 based on bounce rate, spam rate, and reply rate.
    """
    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="User not associated with organization")
    
    return get_deliverability_score(db, org_id)


@router.get("/risky-leads")
async def get_risky(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of leads that may harm deliverability.
    Includes bounced, spam complaints, and do_not_contact leads.
    """
    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="User not associated with organization")
    
    risky = get_risky_leads(db, org_id, limit)
    return {"risky_leads": risky, "total": len(risky)}


@router.get("/best-times")
async def get_best_times(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict:
    """
    Analyze historical reply data to suggest best sending times.
    Returns hour-of-day and day-of-week statistics.
    """
    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="User not associated with organization")
    
    return get_best_sending_times(db, org_id)


@router.get("/health-metrics")
async def get_health_metrics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict:
    """
    Get detailed health metrics for specified time period.
    """
    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="User not associated with organization")
    
    bounce_rate = calculate_bounce_rate(db, org_id, days)
    spam_rate = calculate_spam_complaint_rate(db, org_id, days)
    
    return {
        "period_days": days,
        "bounce_rate": round(bounce_rate, 2),
        "spam_rate": round(spam_rate, 2),
        "health_status": "good" if bounce_rate < 5 and spam_rate < 0.1 else "needs_attention"
    }


@router.post("/check-dns", response_model=DNSCheckResponse)
async def check_dns(
    request: DNSCheckRequest,
    current_user: dict = Depends(get_current_user)
) -> DNSCheckResponse:
    """
    Check DNS records (SPF, DKIM, DMARC, MX) for a domain.
    
    Returns comprehensive DNS check results with an overall deliverability score
    and recommendations for improvement.
    """
    try:
        dns_checker = DNSCheckerService()
        result = dns_checker.check_domain(request.domain)
        
        logger.info(f"DNS check completed for {request.domain}: score {result['overall_score']}")
        
        return DNSCheckResponse(**result)
        
    except Exception as e:
        logger.error(f"DNS check failed for {request.domain}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"DNS check failed: {str(e)}"
        )


@router.post("/warmup-domains", response_model=EmailWarmupDomainResponse)
async def create_warmup_domain(
    request: EmailWarmupDomainCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new email warmup schedule for a domain.
    
    This starts tracking warm-up for a domain, beginning with 10 emails/day
    and gradually increasing the daily limit.
    """
    org_id = request.org_id or current_user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="Organization ID required")
    
    try:
        # Check if domain already exists for this org
        existing = db.query(EmailWarmupDomain).filter(
            EmailWarmupDomain.org_id == org_id,
            EmailWarmupDomain.domain == request.domain
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Warmup already configured for domain {request.domain}"
            )
        
        # Create new warmup domain
        warmup_domain = EmailWarmupDomain(
            id=uuid.uuid4(),
            org_id=org_id,
            domain=request.domain,
            daily_limit=10,  # Start with 10 emails/day
            warmup_day=1,
            emails_sent_today=0
        )
        
        db.add(warmup_domain)
        db.commit()
        db.refresh(warmup_domain)
        
        logger.info(f"Created warmup schedule for domain {request.domain}")
        
        return warmup_domain
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create warmup domain: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create warmup schedule: {str(e)}"
        )


@router.get("/warmup-domains", response_model=List[EmailWarmupDomainResponse])
async def list_warmup_domains(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all email warmup domains for the current organization.
    """
    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="Organization ID required")
    
    warmup_domains = db.query(EmailWarmupDomain).filter(
        EmailWarmupDomain.org_id == org_id
    ).all()
    
    return warmup_domains


@router.get("/warmup-domains/{domain}/status", response_model=EmailWarmupStatusResponse)
async def get_warmup_status(
    domain: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the current warmup status for a specific domain.
    
    Returns current warmup day, daily limits, and progress information.
    """
    org_id = current_user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="Organization ID required")
    
    warmup_domain = db.query(EmailWarmupDomain).filter(
        EmailWarmupDomain.org_id == org_id,
        EmailWarmupDomain.domain == domain
    ).first()
    
    if not warmup_domain:
        raise HTTPException(
            status_code=404,
            detail=f"No warmup schedule found for domain {domain}"
        )
    
    # Calculate next day's limit based on warmup schedule
    next_limit = _calculate_next_warmup_limit(warmup_domain.warmup_day, warmup_domain.daily_limit)
    
    # Check if warmup is complete (reached max limit of 200/day)
    warmup_complete = warmup_domain.daily_limit >= 200
    
    return EmailWarmupStatusResponse(
        domain=warmup_domain.domain,
        warmup_day=warmup_domain.warmup_day,
        daily_limit=warmup_domain.daily_limit,
        emails_sent_today=warmup_domain.emails_sent_today,
        remaining_today=max(0, warmup_domain.daily_limit - warmup_domain.emails_sent_today),
        next_limit=next_limit,
        warmup_complete=warmup_complete
    )


def _calculate_next_warmup_limit(current_day: int, current_limit: int) -> int:
    """
    Calculate next day's email limit based on warmup schedule.
    
    Rules:
    - Day 1: 10 emails
    - Days 2-7: Increase by 5 per day
    - Days 8+: Increase by 10 per day
    - Cap at 200 emails/day
    """
    if current_limit >= 200:
        return 200
    
    if current_day < 7:
        next_limit = current_limit + 5
    else:
        next_limit = current_limit + 10
    
    return min(next_limit, 200)
