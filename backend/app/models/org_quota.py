"""Organization quota model for rate limiting."""
from sqlalchemy import Column, Integer, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, date
import uuid

from app.database import Base


class OrgQuota(Base):
    """Track email sending quotas per organization."""
    
    __tablename__ = "org_quotas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    
    # Current period tracking
    emails_sent_this_period = Column(Integer, default=0, nullable=False)
    period_start = Column(Date, default=date.today, nullable=False)
    
    # Quota limits
    email_limit_per_period = Column(Integer, default=1000, nullable=False)  # Default 1000/day
    period_type = Column(String(20), default="daily", nullable=False)  # daily|weekly|monthly
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @property
    def emails_remaining(self):
        """Calculate remaining emails in current period."""
        return max(0, self.email_limit_per_period - self.emails_sent_this_period)
    
    @property
    def is_quota_exceeded(self):
        """Check if quota is exceeded."""
        return self.emails_sent_this_period >= self.email_limit_per_period
    
    @property
    def usage_percentage(self):
        """Calculate usage percentage."""
        if self.email_limit_per_period == 0:
            return 100.0
        return (self.emails_sent_this_period / self.email_limit_per_period) * 100
