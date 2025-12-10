"""Webhook parser service for processing inbound email events."""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParsedEvent:
    """Parsed email event data."""
    event_type: str
    from_email: Optional[str]
    to_email: Optional[str]
    subject: Optional[str]
    body_text: Optional[str]
    message_id: Optional[str]
    in_reply_to: Optional[str]
    timestamp: Optional[datetime]
    raw_data: Dict[str, Any]


def parse_sendgrid_event(payload: Dict[str, Any]) -> List[ParsedEvent]:
    """
    Parse SendGrid webhook events.
    
    SendGrid sends arrays of events. Each event has:
    - event: 'inbound', 'processed', 'delivered', 'bounce', 'spam_report', etc.
    - email: recipient email
    - from: sender email (for inbound)
    - subject, text, html (for inbound)
    - sg_message_id: SendGrid message ID
    - timestamp: Unix timestamp
    
    Args:
        payload: Raw SendGrid webhook payload (can be array or single object)
        
    Returns:
        List of ParsedEvent objects
    """
    events = []
    
    # Handle both array and single object
    event_list = payload if isinstance(payload, list) else [payload]
    
    for event_data in event_list:
        try:
            event_type = event_data.get('event', 'unknown')
            
            # Map SendGrid event types
            if event_type == 'inbound':
                mapped_type = 'reply' if event_data.get('in_reply_to') else 'inbound'
            elif event_type in ['bounce', 'dropped']:
                mapped_type = 'bounce'
            elif event_type == 'spam_report':
                mapped_type = 'spam'
            elif event_type in ['delivered', 'processed']:
                mapped_type = 'delivered'
            else:
                mapped_type = event_type
            
            # Parse timestamp
            timestamp = None
            if 'timestamp' in event_data:
                try:
                    timestamp = datetime.fromtimestamp(int(event_data['timestamp']))
                except (ValueError, TypeError):
                    logger.warning(f"Invalid timestamp in SendGrid event: {event_data.get('timestamp')}")
            
            parsed = ParsedEvent(
                event_type=mapped_type,
                from_email=event_data.get('from', event_data.get('sender')),
                to_email=event_data.get('to', event_data.get('email')),
                subject=event_data.get('subject'),
                body_text=event_data.get('text', event_data.get('html')),
                message_id=event_data.get('sg_message_id', event_data.get('smtp-id')),
                in_reply_to=event_data.get('in_reply_to'),
                timestamp=timestamp,
                raw_data=event_data
            )
            
            events.append(parsed)
            
        except Exception as e:
            logger.error(f"Error parsing SendGrid event: {e}", extra={'event': event_data})
            continue
    
    return events


def parse_gmail_event(payload: Dict[str, Any]) -> List[ParsedEvent]:
    """
    Parse Gmail webhook events.
    
    For Gmail Push notifications, the payload structure is:
    {
        "message": {
            "data": "base64-encoded-json",
            "messageId": "...",
            "publishTime": "..."
        }
    }
    
    For testing/dev, we accept a simplified structure:
    {
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "subject": "...",
        "body": "...",
        "messageId": "...",
        "inReplyTo": "...",
        "timestamp": "2025-01-01T00:00:00Z"
    }
    
    Args:
        payload: Raw Gmail webhook payload
        
    Returns:
        List of ParsedEvent objects
    """
    events = []
    
    try:
        # Simple format for dev/testing
        if 'from' in payload and 'to' in payload:
            # Determine event type
            event_type = 'reply' if payload.get('inReplyTo') else 'inbound'
            
            # Parse timestamp
            timestamp = None
            if 'timestamp' in payload:
                try:
                    timestamp = datetime.fromisoformat(payload['timestamp'].replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    logger.warning(f"Invalid timestamp in Gmail event: {payload.get('timestamp')}")
            
            parsed = ParsedEvent(
                event_type=event_type,
                from_email=payload.get('from'),
                to_email=payload.get('to'),
                subject=payload.get('subject'),
                body_text=payload.get('body'),
                message_id=payload.get('messageId'),
                in_reply_to=payload.get('inReplyTo'),
                timestamp=timestamp or datetime.utcnow(),
                raw_data=payload
            )
            
            events.append(parsed)
        
        # TODO: Add proper Gmail Push notification parsing
        # This would involve:
        # 1. Decoding the base64 data
        # 2. Parsing the Gmail message format
        # 3. Extracting headers and body
        
    except Exception as e:
        logger.error(f"Error parsing Gmail event: {e}", extra={'payload': payload})
    
    return events


def extract_email_address(email_str: Optional[str]) -> Optional[str]:
    """
    Extract clean email address from various formats.
    
    Handles formats like:
    - "John Doe <john@example.com>"
    - "john@example.com"
    - "<john@example.com>"
    
    Args:
        email_str: Email string to parse
        
    Returns:
        Clean email address or None
    """
    if not email_str:
        return None
    
    # Extract email from "Name <email@example.com>" format
    if '<' in email_str and '>' in email_str:
        start = email_str.index('<') + 1
        end = email_str.index('>')
        return email_str[start:end].strip().lower()
    
    return email_str.strip().lower()
