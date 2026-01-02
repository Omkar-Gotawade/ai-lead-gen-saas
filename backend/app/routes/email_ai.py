"""Email AI generation routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.lead import Lead
from app.schemas.email import EmailGenerateRequest, EmailGenerateResponse
from app.services.auth import get_current_user
from app.services.ai_email_service import generate_email

router = APIRouter()


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
    # Fetch the lead
    lead = db.query(Lead).filter(
        Lead.id == request.lead_id,
        Lead.org_id == current_user.id
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
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
