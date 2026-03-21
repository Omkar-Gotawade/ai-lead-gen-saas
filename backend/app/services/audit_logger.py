"""Audit logging service for tracking critical changes."""
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


class AuditLogger:
    """Service for audit logging critical events"""

    @staticmethod
    def log_dnc_change(
        db: Session,
        lead_id: UUID,
        user_id: Optional[UUID],
        old_value: bool,
        new_value: bool,
        reason: Optional[str] = None
    ):
        """
        Log a change to do_not_contact status.

        Args:
            db: Database session
            lead_id: Lead UUID
            user_id: User who made the change (None for system)
            old_value: Previous DNC status
            new_value: New DNC status
            reason: Optional reason for the change
        """
        # Structured logging for audit trail
        logger.warning(
            f"DNC_CHANGE | lead_id={lead_id} | user_id={user_id} | "
            f"old={old_value} | new={new_value} | reason={reason} | "
            f"timestamp={datetime.utcnow().isoformat()}"
        )

        # TODO: In production, also store in dedicated audit_log table
        # This ensures audit trail persists even if logs are rotated

    @staticmethod
    def log_dnc_send_attempt(
        db: Session,
        lead_id: UUID,
        campaign_id: UUID,
        blocked: bool
    ):
        """
        Log an attempt to send email to a DNC lead.

        Args:
            db: Database session
            lead_id: Lead UUID
            campaign_id: Campaign UUID
            blocked: Whether the send was blocked
        """
        status = "BLOCKED" if blocked else "ALLOWED"
        logger.warning(
            f"DNC_SEND_ATTEMPT | lead_id={lead_id} | campaign_id={campaign_id} | "
            f"status={status} | timestamp={datetime.utcnow().isoformat()}"
        )

    @staticmethod
    def log_security_event(
        event_type: str,
        user_id: Optional[UUID],
        details: str,
        severity: str = "INFO"
    ):
        """
        Log a security-related event.

        Args:
            event_type: Type of event (e.g., AUTH_FAILURE, RATE_LIMIT)
            user_id: User ID if applicable
            details: Event details
            severity: INFO, WARNING, or CRITICAL
        """
        log_func = getattr(logger, severity.lower(), logger.info)
        log_func(
            f"SECURITY_EVENT | type={event_type} | user_id={user_id} | "
            f"details={details} | timestamp={datetime.utcnow().isoformat()}"
        )
