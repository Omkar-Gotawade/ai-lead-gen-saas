"""API routes."""
from .auth import router as auth_router
from .leads import router as leads_router
from .email_ai import router as email_ai_router
from .email_provider import router as email_provider_router
from .email_send import router as email_send_router
from .campaigns import router as campaigns_router
from .sequence_steps import router as sequence_steps_router

__all__ = [
    "auth_router",
    "leads_router",
    "email_ai_router",
    "email_provider_router",
    "email_send_router",
    "campaigns_router",
    "sequence_steps_router"
]
