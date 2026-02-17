"""AI Configuration routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.config import settings

router = APIRouter()


class AIConfigRequest(BaseModel):
    """AI configuration request."""
    api_key: str
    model: Optional[str] = "gemini-pro"


class AIConfigResponse(BaseModel):
    """AI configuration response."""
    provider: str
    model: str
    is_configured: bool


@router.get("/ai-config/me", response_model=AIConfigResponse)
async def get_ai_config(
    current_user: User = Depends(get_current_user)
):
    """
    Get current AI configuration.
    
    Note: This is read-only. AI configuration is set via environment variables.
    """
    is_configured = bool(settings.GEMINI_API_KEY)
    
    return AIConfigResponse(
        provider="Google Gemini",
        model=settings.GEMINI_MODEL,
        is_configured=is_configured
    )


@router.post("/ai-config/configure", response_model=AIConfigResponse)
async def configure_ai(
    request: AIConfigRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Configure AI settings.
    
    Note: This endpoint accepts the configuration but AI is actually
    configured via GEMINI_API_KEY environment variable in docker-compose.yml.
    
    This is here for UI compatibility but doesn't persist changes.
    """
    # In a production system, you'd store this in database per user
    # For now, just return success with env variable status
    
    return AIConfigResponse(
        provider="Google Gemini",
        model=request.model or "gemini-pro",
        is_configured=bool(settings.GEMINI_API_KEY)
    )
