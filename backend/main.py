"""FastAPI application entry point."""
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
    sequence_steps_router
)
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="AI Lead Generation SaaS",
    description="Lead generation and outreach platform API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://frontend:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(leads_router)
app.include_router(email_ai_router, prefix="/api", tags=["email_ai"])
app.include_router(email_provider_router, prefix="/api", tags=["email_provider"])
app.include_router(email_send_router, prefix="/api", tags=["email_send"])
app.include_router(campaigns_router, prefix="/api", tags=["campaigns"])
app.include_router(sequence_steps_router, prefix="/api", tags=["sequence_steps"])


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
