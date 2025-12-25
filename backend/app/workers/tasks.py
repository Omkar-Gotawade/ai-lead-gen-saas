"""Celery tasks for background job processing."""
import time
from uuid import UUID
from datetime import datetime
from ..celery_app import celery_app
from ..database import SessionLocal
from ..models.lead import Lead
from ..models.campaign_lead import CampaignLead
from ..models.inbound_event import InboundEvent


@celery_app.task(name="enrich_lead")
def enrich_lead_task(lead_id: str):
    """
    Background task to enrich lead data.
    
    This is a placeholder implementation that simulates enrichment.
    In production, this would call external APIs (Clearbit, Hunter.io, etc.)
    to gather additional information about the lead.
    
    Args:
        lead_id: Lead UUID as string
        
    Returns:
        dict: Enrichment result
    """
    print(f"[CELERY] Starting enrichment for lead: {lead_id}")
    
    # Simulate API call delay
    time.sleep(3)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Find the lead
        lead = db.query(Lead).filter(Lead.id == UUID(lead_id)).first()
        
        if not lead:
            print(f"[CELERY] Lead not found: {lead_id}")
            return {"status": "error", "message": "Lead not found"}
        
        # Simulate enrichment data
        enriched_data = {
            "linkedin_url": f"https://linkedin.com/in/{lead.first_name.lower()}-{lead.last_name.lower()}",
            "title": "Software Engineer",
            "company_size": "51-200",
            "industry": "Technology",
            "location": "San Francisco, CA",
            "enriched_at": time.time()
        }
        
        # Update lead with enriched data
        lead.enriched_data = enriched_data
        db.commit()
        
        print(f"[CELERY] Successfully enriched lead: {lead_id}")
        
        return {
            "status": "success",
            "lead_id": lead_id,
            "enriched_data": enriched_data
        }
        
    except Exception as e:
        print(f"[CELERY] Error enriching lead {lead_id}: {str(e)}")
        db.rollback()
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()


@celery_app.task(name="check_campaign_replies", bind=True, max_retries=3)
def check_campaign_replies_task(self, campaign_id: str):
    """
    Check for replies to campaign emails and stop sequences.
    
    This task is idempotent - safe to run multiple times.
    Checks InboundEvent table for replies and updates CampaignLead status.
    
    Args:
        campaign_id: Campaign UUID as string
        
    Returns:
        dict: Processing result with counts
    """
    print(f"[CELERY] Checking replies for campaign: {campaign_id}")
    
    db = SessionLocal()
    
    try:
        # Get all campaign leads that are still active (not stopped)
        active_leads = db.query(CampaignLead).filter(
            CampaignLead.campaign_id == UUID(campaign_id),
            CampaignLead.status.in_(['pending', 'in_progress'])
        ).all()
        
        stopped_count = 0
        
        for campaign_lead in active_leads:
            # Check if lead has replied
            reply_event = db.query(InboundEvent).filter(
                InboundEvent.parsed_from == campaign_lead.lead.email,
                InboundEvent.event_type == 'reply',
                InboundEvent.created_at > campaign_lead.created_at
            ).order_by(InboundEvent.created_at.desc()).first()
            
            if reply_event and not campaign_lead.replied_at:
                # Mark lead as replied and stop sequence
                campaign_lead.replied_at = reply_event.created_at
                campaign_lead.reply_message_id = reply_event.message_id
                campaign_lead.status = 'stopped'
                campaign_lead.stop_reason = 'replied'
                stopped_count += 1
                
                print(f"[CELERY] Stopped campaign for lead {campaign_lead.lead_id} - reply detected")
        
        db.commit()
        
        print(f"[CELERY] Campaign reply check completed: {stopped_count} leads stopped")
        
        return {
            "status": "success",
            "campaign_id": campaign_id,
            "checked_leads": len(active_leads),
            "stopped_leads": stopped_count
        }
        
    except Exception as e:
        print(f"[CELERY] Error checking campaign replies {campaign_id}: {str(e)}")
        db.rollback()
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    
    finally:
        db.close()


@celery_app.task(name="send_campaign_step", bind=True, max_retries=3)
def send_campaign_step_task(self, campaign_id: str, step_number: int):
    """
    Send emails for a specific campaign step with quota and bounce checks.
    
    This task:
    1. Checks org quota before sending
    2. Filters out bounced/do_not_contact leads
    3. Skips leads that have replied
    4. Sends emails with rate limiting
    5. Updates quota usage
    
    Args:
        campaign_id: Campaign UUID as string
        step_number: Sequence step number (1, 2, 3, etc.)
        
    Returns:
        dict: Send result with counts
    """
    print(f"[CELERY] Starting campaign step {step_number} for campaign: {campaign_id}")
    
    db = SessionLocal()
    
    try:
        from ..models.campaign import Campaign
        from ..models.sending_log import SendingLog
        from ..services.quota import enforce_quota, increment_quota_usage, QuotaExceededError
        
        # Get campaign
        campaign = db.query(Campaign).filter(Campaign.id == UUID(campaign_id)).first()
        
        if not campaign:
            print(f"[CELERY] Campaign not found: {campaign_id}")
            return {"status": "error", "message": "Campaign not found"}
        
        # Get leads ready for this step
        ready_leads = db.query(CampaignLead).join(Lead).filter(
            CampaignLead.campaign_id == UUID(campaign_id),
            CampaignLead.current_step == step_number,
            CampaignLead.status == 'in_progress',
            CampaignLead.replied_at.is_(None),  # Skip replied leads
            Lead.do_not_contact == False  # Skip bounced/spam leads
        ).all()
        
        if not ready_leads:
            print(f"[CELERY] No leads ready for step {step_number}")
            return {"status": "success", "sent": 0, "message": "No leads ready"}
        
        # Check quota before starting
        try:
            enforce_quota(db, campaign.org_id, len(ready_leads))
        except QuotaExceededError as e:
            print(f"[CELERY] Quota exceeded for org {campaign.org_id}: {str(e)}")
            return {"status": "error", "message": str(e), "sent": 0}
        
        sent_count = 0
        failed_count = 0
        
        for campaign_lead in ready_leads:
            try:
                # Simulate sending email (replace with actual email service)
                print(f"[CELERY] Sending step {step_number} to {campaign_lead.lead.email}")
                
                # Create sending log
                sending_log = SendingLog(
                    org_id=campaign.org_id,
                    campaign_id=campaign.id,
                    lead_id=campaign_lead.lead_id,
                    subject=f"Campaign {campaign.name} - Step {step_number}",
                    body_preview="Email body preview...",
                    status="sent",
                    sent_at=datetime.utcnow()
                )
                db.add(sending_log)
                
                # Update campaign lead
                campaign_lead.last_sent_at = datetime.utcnow()
                campaign_lead.current_step = step_number + 1
                
                # Mark as completed if this was the last step
                if step_number >= 3:  # Assuming 3 steps max
                    campaign_lead.status = 'completed'
                
                sent_count += 1
                
                # Rate limiting delay
                time.sleep(0.5)  # 2 emails per second
                
            except Exception as e:
                print(f"[CELERY] Error sending to {campaign_lead.lead.email}: {str(e)}")
                failed_count += 1
        
        # Increment quota usage
        if sent_count > 0:
            increment_quota_usage(db, campaign.org_id, sent_count)
        
        db.commit()
        
        print(f"[CELERY] Campaign step completed: {sent_count} sent, {failed_count} failed")
        
        return {
            "status": "success",
            "campaign_id": campaign_id,
            "step_number": step_number,
            "sent": sent_count,
            "failed": failed_count
        }
        
    except Exception as e:
        print(f"[CELERY] Error in campaign step {campaign_id}/{step_number}: {str(e)}")
        db.rollback()
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    
    finally:
        db.close()

