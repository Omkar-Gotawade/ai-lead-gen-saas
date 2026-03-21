"""FastAPI application entry point."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import (
    auth_router,
    leads_router,
    email_ai_router,
    email_provider_router,
    email_send_router,
    campaigns_router,
    sequence_steps_router,
    lead_discovery_router,
    ai_config_router
)
from app.routes.webhooks import router as webhooks_router
from app.routes.metrics import router as metrics_router
from app.routes.deliverability import router as deliverability_router
from app.middleware import RateLimitMiddleware
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
_debug = os.getenv("DEBUG", "false").lower() == "true"
app = FastAPI(
    title="AI Lead Generation SaaS",
    description="Lead generation and outreach platform API",
    version="1.0.0",
    docs_url="/docs" if _debug else None,
    redoc_url="/redoc" if _debug else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting (60 requests per minute per IP)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# Include routers
app.include_router(auth_router)
app.include_router(leads_router)
app.include_router(email_ai_router, prefix="/api", tags=["email_ai"])
app.include_router(email_provider_router, prefix="/api", tags=["email_provider"])
app.include_router(email_send_router, prefix="/api", tags=["email_send"])
app.include_router(campaigns_router, prefix="/api", tags=["campaigns"])
app.include_router(sequence_steps_router, prefix="/api", tags=["sequence_steps"])
app.include_router(webhooks_router, prefix="/api", tags=["webhooks"])
app.include_router(metrics_router, prefix="/api", tags=["metrics"])
app.include_router(deliverability_router, prefix="/api", tags=["deliverability"])
app.include_router(lead_discovery_router, tags=["lead_discovery"])
app.include_router(ai_config_router, prefix="/api", tags=["ai_config"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Lead Generation SaaS API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
