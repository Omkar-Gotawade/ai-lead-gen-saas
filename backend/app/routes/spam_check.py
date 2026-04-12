"""Spam prevention API route."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.campaign import Campaign
from app.models.lead import Lead
from app.models.user import User
from app.schemas.spam_check import SpamCheckRequest, SpamCheckResponse
from app.services.auth import get_current_user
from app.services.spam_check_service import (
    analyze_email,
    get_user_domain_authentication,
    get_user_sending_behavior,
)

router = APIRouter()


@router.post("/spam-check", response_model=SpamCheckResponse)
async def spam_check(
    request: SpamCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze email body and return pre-send spam risk assessment."""

    lead = None
    if request.lead_id:
        lead = db.query(Lead).filter(
            Lead.id == request.lead_id,
            Lead.org_id == current_user.id,
        ).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

    if request.campaign_id:
        campaign = db.query(Campaign).filter(
            Campaign.id == request.campaign_id,
            Campaign.user_id == current_user.id,
        ).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

    behavior = get_user_sending_behavior(db=db, user_id=current_user.id)
    domain_auth = get_user_domain_authentication(db=db, user_id=current_user.id)

    result = analyze_email(
        email_body=request.email_body,
        company_name=lead.company if lead else None,
        bounce_rate=behavior["bounce_rate"],
        spam_rate=behavior["spam_rate"],
        spf_configured=domain_auth["spf_configured"],
        dkim_configured=domain_auth["dkim_configured"],
    )

    return SpamCheckResponse(
        score=result["score"],
        level=result["level"],
        issues=result["issues"],
    )
