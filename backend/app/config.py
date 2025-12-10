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
    
    # Google Gemini
    GEMINI_API_KEY: str = "AIzaSyANwxEGKbdzOYsDCW-aPyLCnsO413ZHXSw"
    GEMINI_MODEL: str = "models/gemini-2.5-flash"  # Model name without models/ prefix
    
    # Encryption (for sensitive data like SMTP passwords)
    ENCRYPTION_KEY: str = ""
    
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
