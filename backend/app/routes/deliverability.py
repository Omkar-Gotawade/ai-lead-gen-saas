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
        SendingLog.status == "SENT"
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
    
    # Calculate real metrics for scoring
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    total_sent = db.query(SendingLog).filter(
        SendingLog.user_id == current_user.id,
        SendingLog.created_at >= thirty_days_ago,
        SendingLog.status == "SENT"
    ).count()
    
    failed_sends = db.query(SendingLog).filter(
        SendingLog.user_id == current_user.id,
        SendingLog.created_at >= thirty_days_ago,
        SendingLog.status == "FAILED"
    ).count()
    
    # Check if email provider is connected
    from ..models.email_provider import EmailProviderSettings
    provider_connected = db.query(EmailProviderSettings).filter(
        EmailProviderSettings.user_id == current_user.id
    ).first() is not None
    
    # Calculate bounce and spam metrics from inbound_events
    from ..models.inbound_event import InboundEvent
    
    bounce_count = db.query(InboundEvent).filter(
        InboundEvent.org_id == current_user.id,
        InboundEvent.event_type == 'bounce',
        InboundEvent.created_at >= thirty_days_ago
    ).count()
    
    spam_count = db.query(InboundEvent).filter(
        InboundEvent.org_id == current_user.id,
        InboundEvent.event_type == 'spam',
        InboundEvent.created_at >= thirty_days_ago
    ).count()
    
    delivered_count = db.query(InboundEvent).filter(
        InboundEvent.org_id == current_user.id,
        InboundEvent.event_type == 'delivered',
        InboundEvent.created_at >= thirty_days_ago
    ).count()
    
    # Calculate rates
    total_delivered_or_bounced = delivered_count + bounce_count
    if total_delivered_or_bounced > 0:
        bounce_rate = (bounce_count / total_delivered_or_bounced) * 100
    else:
        bounce_rate = 0.0
    
    if total_sent > 0:
        spam_rate = (spam_count / total_sent) * 100
    else:
        spam_rate = 0.0
    
    has_webhook_data = bounce_count > 0 or spam_count > 0 or delivered_count > 0
    
    # ========================================
    # HEALTH SCORE - COMPREHENSIVE METRICS
    # ========================================
    # Score based on all available metrics:
    # 1. Warmup progress (20 points)
    # 2. Send volume management (20 points)
    # 3. Provider connection (15 points)
    # 4. Send success ratio (15 points)
    # 5. Bounce rate (15 points)
    # 6. Spam complaint rate (15 points)
    
    # 1. Warmup progress (0-20 points)
    if warmup_status['warmup_day'] >= 21:
        warmup_score = 20  # Completed
    elif warmup_status['warmup_day'] >= 14:
        warmup_score = 17  # Almost done
    elif warmup_status['warmup_day'] >= 7:
        warmup_score = 14  # Halfway
    else:
        warmup_score = 10  # Just started
    
    # 2. Send volume management (0-20 points)
    usage_pct = warmup_status['usage_percentage']
    if usage_pct <= 80:
        volume_score = 20  # Safe usage
    elif usage_pct <= 95:
        volume_score = 14  # Approaching limit
    else:
        volume_score = 5  # Over limit
    
    # 3. Provider connection (0-15 points)
    provider_score = 15 if provider_connected else 0
    
    # 4. Send success ratio (0-15 points)
    if total_sent > 0:
        success_rate = ((total_sent - failed_sends) / total_sent) * 100
        if success_rate >= 95:
            success_score = 15
        elif success_rate >= 85:
            success_score = 12
        elif success_rate >= 70:
            success_score = 8
        else:
            success_score = 0
    else:
        success_score = 15  # No sends yet, no failures
    
    # 5. Bounce rate (0-15 points)
    if bounce_rate == 0:
        bounce_score = 15
    elif bounce_rate < 2:
        bounce_score = 13  # Excellent
    elif bounce_rate < 5:
        bounce_score = 8  # Acceptable
    elif bounce_rate < 10:
        bounce_score = 3  # Warning
    else:
        bounce_score = 0  # Critical
    
    # 6. Spam complaint rate (0-15 points)
    if spam_rate == 0:
        spam_score = 15
    elif spam_rate < 0.1:
        spam_score = 13  # Excellent
    elif spam_rate < 0.5:
        spam_score = 8  # Acceptable
    elif spam_rate < 1:
        spam_score = 3  # Warning
    else:
        spam_score = 0  # Critical
    
    health_score = warmup_score + volume_score + provider_score + success_score + bounce_score + spam_score
    
    # Determine status based on comprehensive metrics
    if health_score >= 85:
        status = 'good'
    elif health_score >= 70:
        status = 'warning'
    else:
        status = 'critical'
    
    # Confidence level: "high" if we have webhook data, "partial" otherwise
    if has_webhook_data:
        score_confidence = 'high'
        confidence_note = 'High confidence - Score based on comprehensive metrics including webhook data.'
    else:
        score_confidence = 'partial'
        confidence_note = 'Partial confidence - No webhook events received yet. Configure SendGrid webhooks for complete tracking.'
    
    # System checks - HONEST about implementation status
    checks = {
        'provider_connection': {
            'status': 'pass' if provider_connected else 'fail',
            'message': 'Email provider connected and configured' if provider_connected else 'No email provider configured',
            'implemented': True
        },
        'warmup': {
            'status': 'warning' if warmup_status['warmup_day'] < 14 else 'pass',
            'message': f"Day {warmup_status['warmup_day']} of 21 (recommended warmup period)",
            'note': 'Advisory only - not enforced by provider',
            'implemented': True
        },
        'send_success': {
            'status': 'pass' if (total_sent == 0 or success_rate >= 85) else 'warning',
            'message': f"{success_rate:.1f}% successful sends" if total_sent > 0 else 'No sends yet',
            'implemented': True
        },
        'bounce_rate': {
            'status': 'pass' if bounce_rate < 2 else ('warning' if bounce_rate < 5 else 'fail'),
            'message': f"{bounce_rate:.1f}% bounce rate ({bounce_count} bounces / {total_delivered_or_bounced} delivered)" if total_delivered_or_bounced > 0 else 'No delivery events yet',
            'note': 'Based on webhook events' if bounce_count > 0 else None,
            'implemented': True
        },
        'spam_complaints': {
            'status': 'pass' if spam_rate < 0.1 else ('warning' if spam_rate < 0.5 else 'fail'),
            'message': f"{spam_rate:.2f}% spam rate ({spam_count} complaints / {total_sent} sent)" if total_sent > 0 else 'No sends yet',
            'note': 'Based on webhook events' if spam_count > 0 else None,
            'implemented': True
        },
        'blacklist_status': {
            'status': 'unknown',
            'message': 'Basic check only - Full monitoring not implemented',
            'note': 'Use external tools like MXToolbox for comprehensive checks',
            'implemented': False
        }
    }
    
    # Generate comprehensive, actionable recommendations
    recommendations = []
    warnings = []
    
    # Critical warnings first
    if not provider_connected:
        warnings.append('⚠️ No email provider configured - Cannot send emails')
    
    if warmup_status['usage_percentage'] > 95:
        warnings.append('⚠️ Exceeded recommended daily limit - High risk of reputation damage')
    elif warmup_status['usage_percentage'] > 80:
        warnings.append('⚠️ Approaching recommended daily send limit')
    
    # Bounce rate warnings
    if bounce_rate > 10:
        warnings.append(f'🚨 CRITICAL: Bounce rate is {bounce_rate:.1f}% (should be <2%)')
        recommendations.append('URGENT: Stop sending immediately and clean your email list')
    elif bounce_rate > 5:
        warnings.append(f'⚠️ High bounce rate: {bounce_rate:.1f}% (should be <2%)')
        recommendations.append('Review and clean your email list - Remove invalid addresses')
    
    # Spam rate warnings
    if spam_rate > 1:
        warnings.append(f'🚨 CRITICAL: Spam complaint rate is {spam_rate:.2f}% (should be <0.1%)')
        recommendations.append('URGENT: Review email content and sending practices')
    elif spam_rate > 0.5:
        warnings.append(f'⚠️ High spam rate: {spam_rate:.2f}% (should be <0.1%)')
        recommendations.append('Improve email relevance and personalization')
    
    # Actionable recommendations
    if warmup_status['warmup_day'] < 21:
        recommendations.append(f"Continue warmup: Send consistently for {21 - warmup_status['warmup_day']} more days")
    
    if total_sent == 0:
        recommendations.append('Send test emails to verify your configuration')
    
    if failed_sends > 0 and total_sent > 0:
        fail_rate = (failed_sends / (total_sent + failed_sends)) * 100
        if fail_rate > 10:
            recommendations.append(f'High failure rate ({fail_rate:.1f}%) - Check email provider credentials')
    
    # Best practice reminders
    if not has_webhook_data:
        recommendations.append('⚠️ Configure SendGrid webhooks for complete bounce & spam tracking')
    
    if bounce_rate < 2 and spam_rate < 0.1:
        recommendations.append('✅ Excellent delivery metrics - Keep up the good practices!')
    
    recommendations.append('Verify email list quality before sending campaigns')
    recommendations.append('Test emails with mail-tester.com before bulk sends')
    
    # Advisory notices
    advisory_notices = [
        {
            'type': 'info',
            'message': 'Daily send limits are advisory only - not enforced automatically'
        }
    ]
    
    if has_webhook_data:
        advisory_notices.append({
            'type': 'success',
            'message': 'Webhook events are being tracked - Bounce and spam metrics are accurate'
        })
    else:
        advisory_notices.append({
            'type': 'warning',
            'message': 'Configure SendGrid webhooks for real-time bounce and spam tracking'
        })
    
    advisory_notices.append({
        'type': 'info',
        'message': 'Use external tools (MXToolbox, mail-tester.com) to verify email health'
    })
    
    return {
        'score': health_score,
        'status': status,
        'score_confidence': score_confidence,
        'confidence_note': confidence_note,
        'checks': checks,
        'daily_limit': {
            'sent': warmup_status['used_today'],
            'limit': warmup_status['daily_limit'],
            'next_limit': warmup_status['next_day_limit'],
            'note': 'Recommended safe limit - Not enforced by provider'
        },
        'recommendations': recommendations,
        'warnings': warnings,
        'advisory_notices': advisory_notices,
        'metrics_status': {
            'implemented': ['warmup_tracking', 'send_volume', 'provider_connection', 'send_success_rate', 'bounce_tracking', 'spam_complaints'],
            'not_implemented': ['blacklist_monitoring', 'open_tracking', 'click_tracking']
        },
        'metrics': {
            'bounce_rate': round(bounce_rate, 2),
            'spam_rate': round(spam_rate, 3),
            'bounce_count': bounce_count,
            'spam_count': spam_count,
            'delivered_count': delivered_count,
            'has_webhook_data': has_webhook_data
        }
    }


@router.post("/safety-diagnostics")
@router.post("/auto-fix")  # Keep old endpoint for compatibility
async def run_safety_diagnostics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Run safety diagnostics and provide manual action recommendations.
    Does NOT automatically fix issues - provides guidance only.
    """
    from ..models.email_provider import EmailProviderSettings
    
    # Check provider connection
    provider = db.query(EmailProviderSettings).filter(
        EmailProviderSettings.user_id == current_user.id
    ).first()
    
    # Check recent send activity
    today = date.today()
    sent_today = db.query(SendingLog).filter(
        SendingLog.user_id == current_user.id,
        SendingLog.created_at >= datetime.combine(today, datetime.min.time())
    ).count()
    
    passed_checks = []
    risky_behaviors = []
    manual_actions = []
    
    # Run diagnostics
    if provider:
        passed_checks.append('✅ Email provider is configured')
    else:
        risky_behaviors.append('❌ No email provider configured')
        manual_actions.append('Configure an email provider in Settings')
    
    warmup = db.query(EmailWarmupDomain).filter(
        EmailWarmupDomain.org_id == current_user.id
    ).first()
    
    if warmup and sent_today > warmup.daily_limit:
        risky_behaviors.append(f'❌ Exceeded daily recommended limit ({sent_today}/{warmup.daily_limit})')
        manual_actions.append('Wait until tomorrow before sending more emails')
    elif warmup and sent_today > warmup.daily_limit * 0.9:
        risky_behaviors.append(f'⚠️ Approaching daily limit ({sent_today}/{warmup.daily_limit})')
        manual_actions.append('Pace remaining sends throughout the day')
    else:
        passed_checks.append('✅ Send volume within recommended limits')
    
    if sent_today > 0:
        passed_checks.append('✅ Active sending schedule maintained')
    
    # Always include these reminders
    manual_actions.extend([
        'Verify email list quality manually',
        'Check your email provider dashboard for bounce/spam metrics',
        'Test emails with mail-tester.com before bulk campaigns',
        'Monitor your domain reputation using MXToolbox'
    ])
    
    return {
        'diagnostic_complete': True,
        'passed_checks': passed_checks,
        'risky_behaviors': risky_behaviors,
        'manual_actions_required': manual_actions,
        'note': 'This tool does NOT automatically fix issues. Please review manual actions and implement them yourself.'
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
