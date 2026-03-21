"""Webhook endpoints for receiving email events."""
from fastapi import APIRouter, Depends, HTTPException, Header, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import hmac
import hashlib
import base64
import logging
from datetime import datetime

from app.database import get_db
from app.models.inbound_event import InboundEvent
from app.models.lead import Lead
from app.models.campaign_lead import CampaignLead, CampaignLeadStatus
from app.models.sending_log import SendingLog
from app.services.webhook_parser import parse_sendgrid_event, parse_gmail_event, extract_email_address
from app.services.audit_logger import AuditLogger
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


def verify_sendgrid_signature(
    payload: bytes,
    signature: Optional[str],
    timestamp: Optional[str]
) -> bool:
    """
    Verify SendGrid webhook signature.
    
    SendGrid sends:
    - X-Twilio-Email-Event-Webhook-Signature: ECDSA signature
    - X-Twilio-Email-Event-Webhook-Timestamp: Unix timestamp
    
    Args:
        payload: Raw request body
        signature: Signature header value
        timestamp: Timestamp header value
        
    Returns:
        True if signature is valid
    """
    if not settings.SENDGRID_SIGNING_KEY:
        logger.warning("SENDGRID_SIGNING_KEY not configured - skipping signature verification")
        return True  # Allow in dev/testing
    
    if not signature or not timestamp:
        logger.warning("Missing SendGrid signature or timestamp headers - allowing anyway (dev mode)")
        return True  # Allow if no signature sent
    
    try:
        # SendGrid uses ECDSA with public key verification
        # For simplicity, we'll use HMAC-SHA256 (adjust for your setup)
        # In production, use the official SendGrid verification library
        
        signed_payload = timestamp.encode() + payload
        expected_signature = hmac.new(
            settings.SENDGRID_SIGNING_KEY.encode(),
            signed_payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
        
    except Exception as e:
        logger.error(f"Error verifying SendGrid signature: {e}")
        return False


async def process_webhook_event(
    provider: str,
    event_data: Dict[str, Any],
    org_id: str,
    db: Session
):
    """
    Process a parsed webhook event.
    
    This function:
    1. Saves the event to inbound_events table
    2. Matches to leads and campaign_leads
    3. Updates statuses (replied, bounced, etc.)
    4. Logs the event in sending_logs
    
    Args:
        provider: Email provider name
        event_data: Parsed event data
        org_id: Organization ID
        db: Database session
    """
    try:
        # Extract email address
        to_email = extract_email_address(event_data.to_email)
        from_email = extract_email_address(event_data.from_email)
        
        # Find matching lead
        lead = None
        if to_email or from_email:
            # For inbound/reply, the "from" is the lead's email
            # For bounce/delivered, the "to" is the lead's email
            search_email = from_email if event_data.event_type in ['reply', 'inbound'] else to_email
            
            if search_email:
                lead = db.query(Lead).filter(
                    Lead.email == search_email,
                    Lead.org_id == org_id
                ).first()
        
        # Handle different event types
        if event_data.event_type == 'reply' and lead:
            # Mark campaign_lead as replied
            campaign_leads = db.query(CampaignLead).join(Campaign).filter(
                CampaignLead.lead_id == lead.id,
                CampaignLead.status.in_([
                    CampaignLeadStatus.QUEUED.value,
                    CampaignLeadStatus.IN_PROGRESS.value
                ]),
                Campaign.status == 'active'
            ).all()
            
            for cl in campaign_leads:
                cl.replied_at = event_data.timestamp or datetime.utcnow()
                cl.reply_message_id = event_data.message_id
                cl.stop_reason = 'reply_received'
                cl.status = CampaignLeadStatus.STOPPED.value
                
            logger.info(f"Marked {len(campaign_leads)} campaign leads as replied for lead {lead.id}")
        
        elif event_data.event_type == 'bounce' and lead:
            # Mark lead as bounced and do_not_contact
            old_dnc = lead.do_not_contact
            lead.do_not_contact = True
            lead.bounce_reason = event_data.raw_data.get('reason', 'bounced')
            lead.bounced_at = event_data.timestamp or datetime.utcnow()

            # Audit log the DNC change
            if not old_dnc:
                AuditLogger.log_dnc_change(
                    db=db,
                    lead_id=lead.id,
                    user_id=None,  # System action
                    old_value=old_dnc,
                    new_value=True,
                    reason=f"Bounce webhook: {lead.bounce_reason}"
                )

            # Stop any active campaigns
            campaign_leads = db.query(CampaignLead).filter(
                CampaignLead.lead_id == lead.id,
                CampaignLead.status.in_([
                    CampaignLeadStatus.QUEUED.value,
                    CampaignLeadStatus.IN_PROGRESS.value
                ])
            ).all()

            for cl in campaign_leads:
                cl.stop_reason = 'bounced'
                cl.status = CampaignLeadStatus.STOPPED.value

            logger.info(f"Marked lead {lead.id} as bounced")
        
        elif event_data.event_type == 'spam' and lead:
            # Mark as do_not_contact
            old_dnc = lead.do_not_contact
            lead.do_not_contact = True
            lead.bounce_reason = 'spam_complaint'

            # Audit log the DNC change
            if not old_dnc:
                AuditLogger.log_dnc_change(
                    db=db,
                    lead_id=lead.id,
                    user_id=None,  # System action
                    old_value=old_dnc,
                    new_value=True,
                    reason="Spam complaint webhook"
                )

            # Stop campaigns
            campaign_leads = db.query(CampaignLead).filter(
                CampaignLead.lead_id == lead.id,
                CampaignLead.status.in_([
                    CampaignLeadStatus.QUEUED.value,
                    CampaignLeadStatus.IN_PROGRESS.value
                ])
            ).all()

            for cl in campaign_leads:
                cl.stop_reason = 'spam_complaint'
                cl.status = CampaignLeadStatus.STOPPED.value
        
        # Log in sending_logs if we have a lead
        if lead and event_data.event_type in ['delivered', 'bounce', 'reply']:
            log_entry = SendingLog(
                org_id=org_id,
                lead_id=lead.id,
                campaign_id=None,  # Could link if we track message_id to campaign
                status='replied' if event_data.event_type == 'reply' else event_data.event_type,
                provider_response=str(event_data.raw_data)[:500],
                sent_at=event_data.timestamp or datetime.utcnow()
            )
            db.add(log_entry)
        
        db.commit()
        logger.info(f"Successfully processed {event_data.event_type} event for {search_email}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing webhook event: {e}", exc_info=True)
        raise


@router.post("/webhooks/sendgrid")
async def sendgrid_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    signature: Optional[str] = Header(None, alias="X-Twilio-Email-Event-Webhook-Signature"),
    timestamp: Optional[str] = Header(None, alias="X-Twilio-Email-Event-Webhook-Timestamp")
):
    """
    Receive SendGrid webhook events.
    
    SendGrid documentation:
    https://docs.sendgrid.com/for-developers/tracking-events/event
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Verify signature
        if not verify_sendgrid_signature(body, signature, timestamp):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Parse JSON payload
        payload = await request.json()
        
        # Parse events
        events = parse_sendgrid_event(payload)
        
        # Store each event
        for event in events:
            # ASSUMPTION: Extract org_id from event or use default
            # In production, you'd map this from the recipient domain or a custom header
            org_id = event.raw_data.get('org_id') or settings.DEFAULT_ORG_ID
            
            # Save to inbound_events
            inbound_event = InboundEvent(
                org_id=org_id,
                provider='sendgrid',
                event_type=event.event_type,
                provider_payload=event.raw_data,
                parsed_from=event.from_email,
                parsed_to=event.to_email,
                parsed_subject=event.subject,
                parsed_body_text=event.body_text,
                parsed_message_id=event.message_id,
                parsed_in_reply_to=event.in_reply_to,
                processed='pending'
            )
            db.add(inbound_event)
            db.commit()
            
            # Process in background
            background_tasks.add_task(
                process_webhook_event,
                'sendgrid',
                event,
                org_id,
                db
            )
        
        return {"status": "ok", "events_received": len(events)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling SendGrid webhook: {e}", exc_info=True)
        # Always return 200 to prevent SendGrid from retrying
        return {"status": "error", "message": str(e)}


@router.post("/webhooks/gmail")
async def gmail_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    webhook_secret: Optional[str] = Header(None, alias="X-Webhook-Secret")
):
    """
    Receive Gmail webhook events.
    
    For testing/development, this accepts a simple JSON payload.
    In production, this would handle Gmail Push notifications.
    """
    try:
        # Verify webhook secret
        if not settings.WEBHOOK_SECRET:
            logger.warning("WEBHOOK_SECRET not configured - skipping verification")
        elif webhook_secret != settings.WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Invalid webhook secret")
        
        # Parse payload
        payload = await request.json()
        
        # Parse events
        events = parse_gmail_event(payload)
        
        # Store each event
        for event in events:
            # ASSUMPTION: Extract org_id from payload
            org_id = payload.get('org_id') or settings.DEFAULT_ORG_ID
            
            # Save to inbound_events
            inbound_event = InboundEvent(
                org_id=org_id,
                provider='gmail',
                event_type=event.event_type,
                provider_payload=event.raw_data,
                parsed_from=event.from_email,
                parsed_to=event.to_email,
                parsed_subject=event.subject,
                parsed_body_text=event.body_text,
                parsed_message_id=event.message_id,
                parsed_in_reply_to=event.in_reply_to,
                processed='pending'
            )
            db.add(inbound_event)
            db.commit()
            
            # Process in background
            background_tasks.add_task(
                process_webhook_event,
                'gmail',
                event,
                org_id,
                db
            )
        
        return {"status": "ok", "events_received": len(events)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling Gmail webhook: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@router.get("/webhooks/test")
async def test_webhook_setup():
    """Test endpoint to verify webhook configuration."""
    return {
        "status": "ok",
        "sendgrid_configured": bool(settings.SENDGRID_SIGNING_KEY),
        "gmail_configured": bool(settings.WEBHOOK_SECRET),
        "message": "Webhook endpoints are ready"
    }


@router.post("/webhooks/create-sample-events")
async def create_sample_events(db: Session = Depends(get_db)):
    """Create sample webhook events for testing the UI."""
    try:
        # Use default org ID from settings
        default_org_id = settings.DEFAULT_ORG_ID
        
        sample_events = [
            {
                "event_type": "delivered",
                "provider": "sendgrid",
                "parsed_from": "noreply@yourdomain.com",
                "parsed_to": "test@example.com",
                "parsed_subject": "Test Campaign Email",
                "parsed_message_id": "test-msg-001",
            },
            {
                "event_type": "open",
                "provider": "sendgrid",
                "parsed_from": "noreply@yourdomain.com",
                "parsed_to": "test@example.com",
                "parsed_subject": "Test Campaign Email",
                "parsed_message_id": "test-msg-001",
            },
            {
                "event_type": "click",
                "provider": "sendgrid",
                "parsed_from": "noreply@yourdomain.com",
                "parsed_to": "test@example.com",
                "parsed_subject": "Test Campaign Email",
                "parsed_message_id": "test-msg-001",
            },
            {
                "event_type": "delivered",
                "provider": "sendgrid",
                "parsed_from": "sales@yourdomain.com",
                "parsed_to": "prospect@company.com",
                "parsed_subject": "Re: Partnership Opportunity",
                "parsed_message_id": "test-msg-002",
            },
            {
                "event_type": "bounce",
                "provider": "sendgrid",
                "parsed_from": "sales@yourdomain.com",
                "parsed_to": "invalid@nonexistent.com",
                "parsed_subject": "Follow up email",
                "parsed_message_id": "test-msg-003",
            },
        ]
        
        created_events = []
        for event_data in sample_events:
            event = InboundEvent(
                org_id=default_org_id,
                event_type=event_data["event_type"],
                provider=event_data["provider"],
                parsed_from=event_data["parsed_from"],
                parsed_to=event_data["parsed_to"],
                parsed_subject=event_data["parsed_subject"],
                parsed_message_id=event_data["parsed_message_id"],
                provider_payload=event_data,
                processed="processed",
                created_at=datetime.utcnow()
            )
            db.add(event)
            created_events.append(event_data)
        
        db.commit()
        
        logger.info(f"Created {len(created_events)} sample webhook events")
        return {
            "status": "success",
            "message": f"Created {len(created_events)} sample webhook events",
            "events": created_events
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating sample events: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webhooks/events")
async def get_webhook_events(
    limit: int = 100,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get recent email events including sent emails and webhook events.
    
    Args:
        limit: Maximum number of events to return
        event_type: Filter by event type (sent, reply, bounce, delivered, spam, open, failed)
        db: Database session
        
    Returns:
        Combined list of sending logs and webhook events
    """
    try:
        events_list = []
        
        # Get sending logs (emails sent from campaigns)
        if not event_type or event_type in ['all', 'sent', 'failed']:
            sending_query = db.query(SendingLog).order_by(SendingLog.created_at.desc())
            
            # Apply filter before limiting
            if event_type == 'sent':
                sending_query = sending_query.filter(SendingLog.status == 'SENT')
            elif event_type == 'failed':
                sending_query = sending_query.filter(SendingLog.status == 'FAILED')
            
            sending_logs = sending_query.limit(limit).all()
            
            for log in sending_logs:
                events_list.append({
                    "id": str(log.id),
                    "event_type": log.status.lower(),  # 'sent' or 'failed'
                    "provider": log.provider_type or "unknown",
                    "parsed_from": "You",
                    "parsed_to": log.to_email,
                    "parsed_subject": log.subject,
                    "created_at": log.created_at.isoformat(),
                    "source": "outbound"
                })
        
        # Get webhook events (inbound: replies, bounces, opens, clicks)
        if not event_type or event_type not in ['sent', 'failed']:
            webhook_query = db.query(InboundEvent).order_by(InboundEvent.created_at.desc())
            
            if event_type and event_type != 'all':
                webhook_query = webhook_query.filter(InboundEvent.event_type == event_type)
            
            webhook_events = webhook_query.limit(limit).all()
            
            for event in webhook_events:
                events_list.append({
                    "id": str(event.id),
                    "event_type": event.event_type,
                    "provider": event.provider,
                    "parsed_from": event.parsed_from,
                    "parsed_to": event.parsed_to,
                    "parsed_subject": event.parsed_subject,
                    "created_at": event.created_at.isoformat(),
                    "source": "inbound"
                })
        
        # Sort all events by created_at (most recent first)
        events_list.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Limit to requested number
        events_list = events_list[:limit]
        
        return {
            "events": events_list,
            "total": len(events_list)
        }
    except Exception as e:
        logger.error(f"Error fetching webhook events: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webhooks/sendgrid/activity")
async def get_sendgrid_activity(
    limit: int = 100,
    query: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Fetch email activity directly from SendGrid API.
    
    Uses SendGrid's Email Activity Feed API to get real-time email events.
    """
    try:
        from app.models.email_provider import EmailProviderSettings, ProviderType
        from app.services.crypto_service import decrypt_value
        from sendgrid import SendGridAPIClient
        import json
        
        # Get SendGrid provider settings
        provider = db.query(EmailProviderSettings).filter(
            EmailProviderSettings.type == ProviderType.SENDGRID
        ).first()
        
        if not provider:
            raise HTTPException(status_code=404, detail="SendGrid not configured")
        
        # Decrypt API key
        api_key = decrypt_value(provider.sendgrid_api_key_encrypted)
        
        # Initialize SendGrid client
        sg = SendGridAPIClient(api_key)
        
        # Build query parameters
        query_params = {
            "limit": min(limit, 1000)  # SendGrid max is 1000
        }
        
        if query:
            query_params["query"] = query
        
        # Fetch email activity using correct Email Activity Feed API endpoint
        # The correct endpoint is /v3/messages (Email Activity Feed)
        response = sg.client.messages.get(query_params=query_params)
        
        if response.status_code == 200:
            data = json.loads(response.body)
            messages = data.get('messages', [])
            
            logger.info(f"SendGrid API response: {len(messages)} messages retrieved")
            
            # Transform SendGrid format to our format
            events_list = []
            for msg in messages:
                events_list.append({
                    "id": msg.get('msg_id'),
                    "event_type": msg.get('status', 'unknown'),
                    "provider": "sendgrid",
                    "parsed_from": msg.get('from_email'),
                    "parsed_to": msg.get('to_email'),
                    "parsed_subject": msg.get('subject'),
                    "created_at": msg.get('last_event_time'),
                    "opens_count": msg.get('opens_count', 0),
                    "clicks_count": msg.get('clicks_count', 0),
                    "source": "sendgrid_api"
                })
            
            return {
                "events": events_list,
                "total": len(events_list)
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"SendGrid API error: {response.body}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching SendGrid activity: {e}", exc_info=True)
        # Return empty results instead of error so UI still works
        return {
            "events": [],
            "total": 0,
            "error": str(e)
        }
