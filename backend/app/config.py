"""Application configuration using Pydantic Settings."""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/leadgen_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Google Gemini - READ FROM .env FILE
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Encryption (for sensitive data like SMTP passwords) - READ FROM .env FILE
    ENCRYPTION_KEY: str = ""
    
    # Week 3: Webhook configuration - READ FROM .env FILE
    SENDGRID_API_KEY: str = ""  # SendGrid API key for sending emails
    SENDGRID_SIGNING_KEY: str = ""  # SendGrid webhook verification key
    WEBHOOK_SECRET: str = ""
    DEFAULT_ORG_ID: str = "00000000-0000-0000-0000-000000000000"
    
    # v1: Lead Discovery & Enrichment - READ FROM .env FILE
    SERP_API_KEY: str = ""  # Optional: For better search results
    ENRICHMENT_API_KEY: str = ""  # For LinkedIn enrichment (Clearbit/Apollo/Snov)
    ENRICHMENT_PROVIDER: str = "clearbit"  # clearbit, apollo, or snov
    # Note: Company enrichment uses GEMINI_API_KEY (already configured above)
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
