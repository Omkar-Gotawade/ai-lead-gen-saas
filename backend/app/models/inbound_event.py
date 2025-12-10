"""Inbound event model for storing webhook payloads."""
from sqlalchemy import Column, String, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class InboundEvent(Base):
    """Store raw webhook events from email providers."""
    
    __tablename__ = "inbound_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # sendgrid|gmail|custom
    event_type = Column(String(50), nullable=False)  # inbound|reply|bounce|spam|delivered
    
    # Raw provider payload for auditing
    provider_payload = Column(JSON, nullable=False)
    
    # Parsed fields
    parsed_from = Column(String(255), nullable=True)
    parsed_to = Column(String(255), nullable=True, index=True)
    parsed_subject = Column(String(500), nullable=True)
    parsed_body_text = Column(String, nullable=True)
    parsed_message_id = Column(String(255), nullable=True)
    parsed_in_reply_to = Column(String(255), nullable=True)
    
    # Processing status
    processed = Column(String(20), default="pending")  # pending|processed|failed
    processed_at = Column(DateTime, nullable=True)
    processing_error = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_inbound_events_org_created', 'org_id', 'created_at'),
        Index('idx_inbound_events_parsed_to', 'parsed_to'),
        Index('idx_inbound_events_event_type', 'event_type'),
    )
