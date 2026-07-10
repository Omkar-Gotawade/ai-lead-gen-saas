"""Email AI generation routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
import logging

from app.database import get_db
from app.models.user import User
from app.models.lead import Lead
from app.schemas.email import EmailGenerateRequest, EmailGenerateResponse
from app.services.auth import get_current_user
from app.services.ai_email_service import generate_email
from app.services.lead_research_service import (
    research_lead_with_status,
    RESEARCH_STATUS_NONE,
)
from app.services.rate_limiter import enforce_rate_limit
from app.services.linkedin_enrichment import enrich_linkedin_profile
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


def _is_quota_error(message: str) -> bool:
    text = (message or "").lower()
    return any(marker in text for marker in ["429", "quota exceeded", "rate limit", "resourceexhausted"])


def _first_research_line(notes: str) -> str:
    if not notes:
        return ""
    for line in notes.splitlines():
        cleaned = line.strip().lstrip("- ").strip()
        if cleaned.lower().startswith("research fallback"):
            continue
        if cleaned:
            return cleaned
    return ""


def _build_quota_fallback_email(lead: Lead, sender_name: str, product_description: str):
    first_name = lead.first_name or "there"
    company = lead.company or "your team"
    subject = f"Quick idea for {company}"

    research_line = _first_research_line(lead.research_notes or "")
    if research_line:
        opening = f"{first_name} - noticed {research_line}."
    else:
        title = lead.title or lead.job_title or "your role"
        opening = f"{first_name} - saw you're leading {title} at {company}."

    body = (
        f"{opening}\n\n"
        f"Teams like yours use {product_description} to catch deliverability issues early "
        f"and keep outbound performance steady.\n\n"
        "Open to a quick 10-minute walkthrough this week?\n\n"
        f"Best regards,\n{sender_name}"
    )

    return subject, body


@router.post("/generate-email", response_model=EmailGenerateResponse)
async def generate_email_endpoint(
    request: EmailGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate personalized email copy using AI.
    
    Args:
        request: Email generation request with lead_id and preferences
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Generated email with subject and body
    """
    enforce_rate_limit("email_generation", str(current_user.id))

    # Fetch the lead
    lead = db.query(Lead).filter(
        Lead.id == request.lead_id,
        Lead.org_id == current_user.id
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Always attempt fresh lead research before writing email copy.
    # If research fails, continue with existing context to keep generation non-blocking.
    research_notes_used = lead.research_notes
    research_status = "existing" if lead.research_notes else RESEARCH_STATUS_NONE
    try:
        logger.info("Starting lead research before email generation for %s", lead.id)
        researched_notes, resolved_status = await research_lead_with_status(lead)
        if researched_notes:
            lead.research_notes = researched_notes
            research_notes_used = researched_notes
            research_status = resolved_status
            db.commit()
            db.refresh(lead)
            logger.info("Lead research completed for %s (%d chars)", lead.id, len(researched_notes))
        elif lead.research_notes:
            research_status = "existing"
            logger.info("No fresh research found for %s; using existing stored notes", lead.id)
        else:
            research_status = resolved_status
    except Exception as exc:
        logger.warning("Lead research failed for %s (continuing): %s", lead.id, exc)
        if lead.research_notes:
            research_status = "existing"

    # Lazy enrichment: if lead has LinkedIn URL but lacks profile details,
    # fetch enrichment before generating so prompts include research context.
    needs_linkedin_enrichment = bool(
        lead.linkedin_url and not any([
            lead.job_title,
            lead.seniority,
            lead.company_size,
            lead.linkedin_headline,
        ])
    )

    if needs_linkedin_enrichment and settings.ENRICHMENT_API_KEY:
        try:
            enrichment = enrich_linkedin_profile(
                linkedin_url=lead.linkedin_url,
                provider=settings.ENRICHMENT_PROVIDER,
                api_key=settings.ENRICHMENT_API_KEY,
            )

            if enrichment.get("success"):
                if enrichment.get("job_title"):
                    lead.job_title = enrichment["job_title"]
                if enrichment.get("seniority"):
                    lead.seniority = enrichment["seniority"]
                if enrichment.get("company_size") and not lead.company_size:
                    lead.company_size = enrichment["company_size"]
                if enrichment.get("linkedin_headline"):
                    lead.linkedin_headline = enrichment["linkedin_headline"]

                db.commit()
                db.refresh(lead)
            else:
                logger.warning(
                    "LinkedIn enrichment did not return success for lead %s: %s",
                    lead.id,
                    enrichment.get("error"),
                )
        except Exception as exc:
            # Do not block email generation on enrichment failures.
            logger.warning("LinkedIn enrichment skipped for lead %s: %s", lead.id, exc)
    
    try:
        # Generate email using AI service
        generated = await generate_email(
            lead=lead,
            sender_name=current_user.full_name or current_user.email.split('@')[0],
            tone=request.tone or "professional",
            goal=request.goal or "schedule a meeting",
            product_description=request.product_description or "our product or service"
        )
        
        return EmailGenerateResponse(
            subject=generated.subject,
            body=generated.body,
            research_notes=research_notes_used,
            research_status=research_status,
            # A/B metadata from Human SDR Copywriter Agent
            email_angle=generated.email_angle,
            word_count=generated.word_count,
            selected_subject=generated.selected_subject,
            alternative_subjects=generated.alternative_subjects,
            quality_report=generated.quality_report,
        )
        
    except ValueError as e:
        if _is_quota_error(str(e)):
            sender_name = current_user.full_name or current_user.email.split('@')[0]
            subject, body = _build_quota_fallback_email(
                lead=lead,
                sender_name=sender_name,
                product_description=request.product_description or "our product or service",
            )
            logger.warning("Gemini quota hit for lead %s, returning deterministic email fallback", lead.id)
            return EmailGenerateResponse(
                subject=subject,
                body=body,
                research_notes=research_notes_used,
                research_status=research_status,
            )
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate email: {str(e)}"
        )
