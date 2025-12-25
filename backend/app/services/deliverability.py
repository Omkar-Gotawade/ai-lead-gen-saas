"""
Deliverability guidance and email health monitoring service.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Dict, List
from ..models.campaign_lead import CampaignLead
from ..models.lead import Lead


def calculate_bounce_rate(db: Session, org_id: int, days: int = 30) -> float:
    """Calculate bounce rate for organization over specified days."""
    since = datetime.utcnow() - timedelta(days=days)
    
    total_sent = db.query(func.count(CampaignLead.id)).filter(
        CampaignLead.org_id == org_id,
        CampaignLead.sent_at.isnot(None),
        CampaignLead.sent_at >= since
    ).scalar() or 0
    
    if total_sent == 0:
        return 0.0
    
    bounced = db.query(func.count(Lead.id)).join(
        CampaignLead, CampaignLead.lead_id == Lead.id
    ).filter(
        Lead.org_id == org_id,
        Lead.bounced_at.isnot(None),
        Lead.bounced_at >= since
    ).scalar() or 0
    
    return (bounced / total_sent) * 100


def calculate_spam_complaint_rate(db: Session, org_id: int, days: int = 30) -> float:
    """Calculate spam complaint rate for organization."""
    since = datetime.utcnow() - timedelta(days=days)
    
    total_sent = db.query(func.count(CampaignLead.id)).filter(
        CampaignLead.org_id == org_id,
        CampaignLead.sent_at.isnot(None),
        CampaignLead.sent_at >= since
    ).scalar() or 0
    
    if total_sent == 0:
        return 0.0
    
    spam_complaints = db.query(func.count(Lead.id)).join(
        CampaignLead, CampaignLead.lead_id == Lead.id
    ).filter(
        Lead.org_id == org_id,
        Lead.bounce_reason == "spam_complaint",
        Lead.bounced_at >= since
    ).scalar() or 0
    
    return (spam_complaints / total_sent) * 100


def get_deliverability_score(db: Session, org_id: int) -> Dict:
    """
    Calculate overall deliverability score (0-100) and provide guidance.
    Score factors: bounce rate, spam rate, reply rate.
    """
    bounce_rate = calculate_bounce_rate(db, org_id, days=30)
    spam_rate = calculate_spam_complaint_rate(db, org_id, days=30)
    
    # Calculate reply rate (30 days)
    since = datetime.utcnow() - timedelta(days=30)
    total_sent = db.query(func.count(CampaignLead.id)).filter(
        CampaignLead.org_id == org_id,
        CampaignLead.sent_at.isnot(None),
        CampaignLead.sent_at >= since
    ).scalar() or 0
    
    replied = db.query(func.count(CampaignLead.id)).filter(
        CampaignLead.org_id == org_id,
        CampaignLead.replied_at.isnot(None),
        CampaignLead.replied_at >= since
    ).scalar() or 0
    
    reply_rate = (replied / total_sent * 100) if total_sent > 0 else 0.0
    
    # Calculate score (0-100)
    # Perfect: 0% bounce, 0% spam, high reply rate
    score = 100.0
    
    # Penalize bounce rate (each 1% bounce = -10 points, cap at -50)
    score -= min(bounce_rate * 10, 50)
    
    # Penalize spam rate heavily (each 0.1% spam = -10 points, cap at -40)
    score -= min(spam_rate * 100, 40)
    
    # Reward reply rate (each 1% reply = +1 point, cap at +20)
    score += min(reply_rate, 20)
    
    score = max(0, min(100, score))  # Clamp to 0-100
    
    # Generate recommendations
    recommendations = []
    
    if bounce_rate > 5:
        recommendations.append({
            "severity": "high",
            "issue": f"High bounce rate ({bounce_rate:.1f}%)",
            "action": "Clean your email list. Remove invalid addresses. Consider email verification service."
        })
    elif bounce_rate > 2:
        recommendations.append({
            "severity": "medium",
            "issue": f"Moderate bounce rate ({bounce_rate:.1f}%)",
            "action": "Monitor bounced emails and update your list regularly."
        })
    
    if spam_rate > 0.1:
        recommendations.append({
            "severity": "critical",
            "issue": f"Spam complaints detected ({spam_rate:.2f}%)",
            "action": "Review email content. Ensure clear unsubscribe link. Only email engaged leads."
        })
    
    if reply_rate < 1 and total_sent > 50:
        recommendations.append({
            "severity": "medium",
            "issue": f"Low reply rate ({reply_rate:.1f}%)",
            "action": "Improve personalization. Test different subject lines. Ensure emails provide value."
        })
    
    if total_sent < 10:
        recommendations.append({
            "severity": "info",
            "issue": "Limited sending history",
            "action": "Send more emails to build reliable deliverability metrics. Start with small batches."
        })
    
    # Determine health status
    if score >= 90:
        health = "excellent"
    elif score >= 75:
        health = "good"
    elif score >= 60:
        health = "fair"
    elif score >= 40:
        health = "poor"
    else:
        health = "critical"
    
    return {
        "score": round(score, 1),
        "health": health,
        "metrics": {
            "bounce_rate": round(bounce_rate, 2),
            "spam_rate": round(spam_rate, 2),
            "reply_rate": round(reply_rate, 2),
            "total_sent_30d": total_sent,
            "total_replied_30d": replied
        },
        "recommendations": recommendations
    }


def get_risky_leads(db: Session, org_id: int, limit: int = 50) -> List[Dict]:
    """
    Identify leads that may harm deliverability.
    Returns leads with repeated bounces, invalid formats, etc.
    """
    risky = []
    
    # Leads marked as do_not_contact
    dnc_leads = db.query(Lead).filter(
        Lead.org_id == org_id,
        Lead.do_not_contact == True
    ).limit(limit).all()
    
    for lead in dnc_leads:
        risky.append({
            "lead_id": lead.id,
            "email": lead.email,
            "risk_type": "do_not_contact",
            "reason": lead.bounce_reason or "Unknown",
            "date": lead.bounced_at.isoformat() if lead.bounced_at else None
        })
    
    return risky


def get_best_sending_times(db: Session, org_id: int) -> Dict:
    """
    Analyze reply patterns to suggest best sending times.
    Returns hour-of-day and day-of-week statistics.
    """
    # Get all replied campaign leads
    replied_leads = db.query(CampaignLead).filter(
        CampaignLead.org_id == org_id,
        CampaignLead.replied_at.isnot(None)
    ).all()
    
    if not replied_leads:
        return {
            "recommendation": "Not enough data. Send emails at 9 AM on Tuesday-Thursday (industry best practice).",
            "hours": {},
            "days": {}
        }
    
    # Count replies by hour and day
    hour_counts = {}
    day_counts = {}
    
    for cl in replied_leads:
        if cl.replied_at:
            hour = cl.replied_at.hour
            day = cl.replied_at.strftime("%A")
            
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
            day_counts[day] = day_counts.get(day, 0) + 1
    
    # Find best hour and day
    best_hour = max(hour_counts, key=hour_counts.get) if hour_counts else 9
    best_day = max(day_counts, key=day_counts.get) if day_counts else "Tuesday"
    
    return {
        "recommendation": f"Best time: {best_day}s at {best_hour}:00",
        "best_hour": best_hour,
        "best_day": best_day,
        "hours": hour_counts,
        "days": day_counts
    }
