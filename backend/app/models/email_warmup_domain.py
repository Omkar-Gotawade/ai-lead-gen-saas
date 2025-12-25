"""Email Warmup Domain model for managing domain warm-up schedules."""
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from ..database import Base


class EmailWarmupDomain(Base):
    """Model for tracking email domain warm-up schedules."""
    
    __tablename__ = "email_warmup_domains"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Domain information
    domain = Column(String(500), nullable=False, index=True)
    
    # Warm-up configuration
    daily_limit = Column(Integer, default=10, nullable=False)  # Starts at 10 emails/day
    warmup_day = Column(Integer, default=1, nullable=False)  # Current day in warmup schedule
    
    # Tracking
    emails_sent_today = Column(Integer, default=0, nullable=False)
    last_reset_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Warm-up rules:
    # Day 1: 10 emails/day
    # Day 2-7: Increase by 5 each day
    # Day 8+: Increase by 10 each day
    # Cap at 200 emails/day for v1
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<EmailWarmupDomain(id={self.id}, domain={self.domain}, day={self.warmup_day}, limit={self.daily_limit})>"
