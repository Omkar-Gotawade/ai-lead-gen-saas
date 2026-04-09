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
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Lead duplicate handling
    LEAD_DUPLICATE_STRATEGY: str = "skip"  # skip|update
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Google Gemini - READ FROM .env FILE
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_RESEARCH_MODEL: str = ""
    GEMINI_RESEARCH_ENABLE_WEB_SEARCH: bool = True
    
    # Encryption (for sensitive data like SMTP passwords) - READ FROM .env FILE
    ENCRYPTION_KEY: str = ""
    
    # Week 3: Webhook configuration - READ FROM .env FILE
    SENDGRID_API_KEY: str = ""  # SendGrid API key for sending emails
    SENDGRID_SIGNING_KEY: str = ""  # SendGrid webhook verification key
    WEBHOOK_SECRET: str = ""
    DEFAULT_ORG_ID: str = "00000000-0000-0000-0000-000000000000"
    
    # v1: Lead Discovery & Enrichment - READ FROM .env FILE
    SERP_API_KEY: str = ""  # Optional: SerpAPI key for better search results
    ZENROWS_API_KEY: str = ""  # Optional: ZenRows key for website scraping
    APIFY_API_TOKEN: str = ""  # Optional: Apify token for LinkedIn/profile enrichment
    HUNTER_API_KEY: str = ""  # Optional: Hunter.io key for business email discovery
    ABSTRACT_API_KEY: str = ""  # Optional: Abstract email validation key
    ENRICHMENT_API_KEY: str = ""  # For LinkedIn enrichment (Clearbit/Apollo/Snov)
    ENRICHMENT_PROVIDER: str = "clearbit"  # clearbit, apollo, or snov
    # Note: Company enrichment uses GEMINI_API_KEY (already configured above)

    # People Search APIs - READ FROM .env FILE
    PDL_API_KEY: str = ""         # People Data Labs (primary, free 1k/mo) - https://app.peopledatalabs.com/signup
    ICYPEAS_API_KEY: str = ""     # Icypeas (free 5k/mo, Gmail OK) - https://app.icypeas.com → Settings → API
    APOLLO_API_KEY: str = ""      # Apollo.io people search (paid API plan needed)
    SNOV_CLIENT_ID: str = ""      # Snov.io OAuth2 client ID (secondary) - https://app.snov.io
    SNOV_CLIENT_SECRET: str = ""  # Snov.io OAuth2 client secret
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
