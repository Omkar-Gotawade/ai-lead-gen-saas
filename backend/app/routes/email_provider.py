"""Email provider configuration routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.email_provider import EmailProviderSettings, ProviderType
from app.schemas.email import (
    EmailProviderConnectRequest,
    EmailProviderResponse,
    EmailTestRequest
)
from app.services.auth import get_current_user
from app.services.crypto_service import encrypt_value
from app.services.email_sender import send_email

router = APIRouter()


@router.post("/email-providers", response_model=EmailProviderResponse)
@router.post("/email-provider/connect", response_model=EmailProviderResponse)
async def connect_email_provider(
    request: EmailProviderConnectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Connect or update email provider configuration.
    
    Args:
        request: Email provider connection details
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Email provider configuration (without sensitive data)
    """
    # Check if user already has a provider configured
    existing = db.query(EmailProviderSettings).filter(
        EmailProviderSettings.user_id == current_user.id
    ).first()
    
    if existing:
        # Update existing
        provider = existing
    else:
        # Create new
        provider = EmailProviderSettings(user_id=current_user.id)
        db.add(provider)
    
    # Set basic fields
    provider.provider_type = ProviderType(request.provider_type)
    provider.from_name = request.from_name
    provider.from_email = request.from_email
    
    # Set provider-specific fields with encryption
    if request.provider_type == "smtp":
        if not all([request.smtp_host, request.smtp_port, request.smtp_username, request.smtp_password]):
            raise HTTPException(
                status_code=400,
                detail="SMTP requires host, port, username, and password"
            )
        
        provider.smtp_host = request.smtp_host
        provider.smtp_port = request.smtp_port
        provider.smtp_username = request.smtp_username
        provider.smtp_password_encrypted = encrypt_value(request.smtp_password)
        provider.use_tls = request.use_tls if request.use_tls is not None else True
        provider.use_ssl = request.use_ssl if request.use_ssl is not None else False
        
    elif request.provider_type == "sendgrid":
        if not request.sendgrid_api_key:
            raise HTTPException(
                status_code=400,
                detail="SendGrid requires API key"
            )
        
        provider.sendgrid_api_key_encrypted = encrypt_value(request.sendgrid_api_key)
    
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid provider type. Must be 'smtp' or 'sendgrid'"
        )
    
    db.commit()
    db.refresh(provider)
    
    return EmailProviderResponse(
        id=provider.id,
        provider_type=provider.provider_type.value,
        from_name=provider.from_name,
        from_email=provider.from_email,
        configured=True
    )


@router.get("/email-provider/me", response_model=EmailProviderResponse)
async def get_email_provider(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get email provider configuration.
    First checks user's own config, then falls back to any system provider.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Email provider configuration (without sensitive data)
    """
    # First try to get user's own provider
    provider = db.query(EmailProviderSettings).filter(
        EmailProviderSettings.user_id == current_user.id
    ).first()
    
    # If user doesn't have one, return None/null (don't throw 404)
    if not provider:
        return None
    
    return EmailProviderResponse(
        id=provider.id,
        provider_type=provider.provider_type.value,
        from_name=provider.from_name,
        from_email=provider.from_email,
        configured=True
    )


@router.post("/email-provider/test")
async def test_email_provider(
    request: EmailTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a test email using configured provider.
    Falls back to any system provider if user doesn't have own config.
    
    Args:
        request: Test email request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    # Try user's own provider first, then any system provider
    provider = db.query(EmailProviderSettings).filter(
        EmailProviderSettings.user_id == current_user.id
    ).first()
    
    if not provider:
        provider = db.query(EmailProviderSettings).first()
    
    if not provider:
        raise HTTPException(
            status_code=404,
            detail="Email provider not configured. Please configure one first."
        )
    
    try:
        send_email(
            provider_settings=provider,
            to_email=request.to_email,
            subject=request.subject,
            body=request.body
        )
        
        return {"success": True, "message": "Test email sent successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send test email: {str(e)}"
        )


@router.delete("/email-provider/me")
async def delete_email_provider(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete/disconnect email provider configuration.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    provider = db.query(EmailProviderSettings).filter(
        EmailProviderSettings.user_id == current_user.id
    ).first()
    
    if not provider:
        raise HTTPException(
            status_code=404,
            detail="No email provider configured"
        )
    
    db.delete(provider)
    db.commit()
    
    return {"success": True, "message": "Email provider disconnected successfully"}
