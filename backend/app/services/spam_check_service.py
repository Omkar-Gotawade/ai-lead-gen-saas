"""Pre-send spam prevention analysis service."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from uuid import UUID
import re

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.campaign import Campaign, CampaignStatus
from app.models.email_provider import EmailProviderSettings
from app.models.inbound_event import InboundEvent
from app.models.sending_log import SendingLog, SendStatus
from app.services.dns_checker import DNSCheckerService


SPAM_WORDS = ["free", "guarantee", "urgent", "win"]
MAX_LINKS = 2
MAX_EXCLAMATIONS = 3
BOUNCE_RATE_THRESHOLD = 0.02
SPAM_RATE_THRESHOLD = 0.003


def _normalize_for_match(value: str) -> str:
    """Normalize text for robust company/persona containment checks."""
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _mentions_company(body: str, company_name: str) -> bool:
    """Check company mention while tolerating spaces/punctuation differences."""
    if not company_name:
        return True

    body_lower = (body or "").lower()
    company_lower = company_name.lower().strip()
    if not company_lower:
        return True

    if company_lower in body_lower:
        return True

    body_norm = _normalize_for_match(body_lower)
    company_norm = _normalize_for_match(company_lower)
    return bool(company_norm and company_norm in body_norm)


def calculate_spam_score(issues: List[str]) -> Tuple[int, str]:
    """Calculate score/level based on issue count."""
    score = min(100, len(issues) * 20)

    if score < 20:
        level = "safe"
    elif score < 50:
        level = "warning"
    else:
        level = "critical"

    return score, level


def can_send_email(result: Dict[str, object]) -> bool:
    """Critical analysis must block sends."""
    if result["level"] == "critical":
        return False
    return True


def get_user_sending_behavior(db: Session, user_id: UUID, days: int = 30) -> Dict[str, float]:
    """Return bounce/spam complaint rates for the recent period."""
    since = datetime.utcnow() - timedelta(days=days)

    total_sent = db.query(func.count(SendingLog.id)).filter(
        SendingLog.user_id == user_id,
        SendingLog.status == SendStatus.SENT,
        SendingLog.sent_at.isnot(None),
        SendingLog.sent_at >= since,
    ).scalar() or 0

    bounce_count = db.query(func.count(InboundEvent.id)).filter(
        InboundEvent.org_id == user_id,
        InboundEvent.created_at >= since,
        InboundEvent.event_type.in_(["bounce", "failed"]),
    ).scalar() or 0

    spam_count = db.query(func.count(InboundEvent.id)).filter(
        InboundEvent.org_id == user_id,
        InboundEvent.created_at >= since,
        InboundEvent.event_type.in_(["spam", "spam_report"]),
    ).scalar() or 0

    if total_sent == 0:
        return {"bounce_rate": 0.0, "spam_rate": 0.0, "total_sent": 0}

    return {
        "bounce_rate": bounce_count / total_sent,
        "spam_rate": spam_count / total_sent,
        "total_sent": total_sent,
    }


def get_user_domain_authentication(db: Session, user_id: UUID) -> Dict[str, bool]:
    """Check sender domain SPF/DKIM status for the user provider."""
    provider = db.query(EmailProviderSettings).filter(
        EmailProviderSettings.user_id == user_id,
    ).first()

    if not provider or not provider.from_email or "@" not in provider.from_email:
        return {"spf_configured": False, "dkim_configured": False}

    domain = provider.from_email.split("@")[-1].strip().lower()
    if not domain:
        return {"spf_configured": False, "dkim_configured": False}

    dns_result = DNSCheckerService().check_domain(domain)
    return {
        "spf_configured": bool(dns_result.get("spf", {}).get("valid", False)),
        "dkim_configured": bool(dns_result.get("dkim", {}).get("exists", False)),
    }


def analyze_email(
    email_body: str,
    company_name: str | None,
    bounce_rate: float,
    spam_rate: float,
    spf_configured: bool,
    dkim_configured: bool,
) -> Dict[str, object]:
    """Analyze pre-send spam risks and return issues, score and level."""
    body = email_body or ""
    body_lower = body.lower()
    issues: List[str] = []

    spam_hits = [word for word in SPAM_WORDS if word in body_lower]
    if spam_hits:
        issues.append(f"Spam keywords detected: {', '.join(spam_hits)}")

    if body.count("!") > MAX_EXCLAMATIONS:
        issues.append("Excessive exclamation marks")

    link_count = len(re.findall(r"(https?://\S+|www\.\S+)", body_lower))
    if link_count > MAX_LINKS:
        issues.append("Too many links")

    if company_name and company_name.strip() and not _mentions_company(body, company_name):
        issues.append("No personalization: company name missing")

    if bounce_rate > BOUNCE_RATE_THRESHOLD:
        issues.append("High bounce rate")

    if spam_rate > SPAM_RATE_THRESHOLD:
        issues.append("High spam complaint rate")

    if not spf_configured:
        issues.append("SPF not configured")

    if not dkim_configured:
        issues.append("DKIM not configured")

    score, level = calculate_spam_score(issues)
    return {
        "issues": issues,
        "score": score,
        "level": level,
        "behavior": {
            "bounce_rate": bounce_rate,
            "spam_rate": spam_rate,
        },
        "domain": {
            "spf_configured": spf_configured,
            "dkim_configured": dkim_configured,
        },
    }


def enforce_behavior_safety(db: Session, campaign: Campaign, bounce_rate: float, spam_rate: float) -> bool:
    """Pause campaign when behavior thresholds are breached."""
    should_pause = bounce_rate > BOUNCE_RATE_THRESHOLD or spam_rate > SPAM_RATE_THRESHOLD
    if should_pause and campaign.status != CampaignStatus.PAUSED:
        campaign.status = CampaignStatus.PAUSED
        db.commit()
        db.refresh(campaign)
    return should_pause
