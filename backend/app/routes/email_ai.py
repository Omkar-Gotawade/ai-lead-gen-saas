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
from app.services.rate_limiter import enforce_rate_limit
from app.services.linkedin_enrichment import enrich_linkedin_profile
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


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
            body=generated.body
        )
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate email: {str(e)}"
        )
