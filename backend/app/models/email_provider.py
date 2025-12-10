"""Email provider settings model."""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.database import Base


class ProviderType(str, enum.Enum):
    """Email provider types."""
    SMTP = "smtp"
    SENDGRID = "sendgrid"


class EmailProviderSettings(Base):
    """Email provider configuration."""
    __tablename__ = "email_provider_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Provider configuration
    provider_type = Column(SQLEnum(ProviderType), nullable=False)
    from_name = Column(String, nullable=False)
    from_email = Column(String, nullable=False)
    
    # SMTP configuration (encrypted)
    smtp_host = Column(String, nullable=True)
    smtp_port = Column(Integer, nullable=True)
    smtp_username = Column(String, nullable=True)
    smtp_password_encrypted = Column(String, nullable=True)  # Encrypted
    use_tls = Column(Boolean, default=True)
    use_ssl = Column(Boolean, default=False)
    
    # SendGrid configuration (encrypted)
    sendgrid_api_key_encrypted = Column(String, nullable=True)  # Encrypted
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
