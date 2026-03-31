"""Celery tasks for campaign execution."""
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
import asyncio
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.campaign import Campaign
from app.models.campaign_lead import CampaignLead, CampaignLeadStatus
from app.models.sequence_step import SequenceStep
from app.models.lead import Lead
from app.workers.email_worker import send_email_task
from app.services.ai_email_service import generate_email
from app.services.audit_logger import AuditLogger
from app.services.campaign_guard import enforce_campaign_send_limit
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="check_pending_campaigns")
def check_pending_campaigns():
    """
    Periodic task to check for campaign leads that need to be processed.
    This runs every minute via Celery Beat.
    """
    db = SessionLocal()
    
    try:
        now = datetime.utcnow()
        
        # Find all campaign leads that are ready to send
        pending_leads = db.query(CampaignLead).filter(
            CampaignLead.status.in_([
                CampaignLeadStatus.PENDING.value,
                CampaignLeadStatus.IN_PROGRESS.value
            ]),
            CampaignLead.next_run_at <= now
        ).all()
        
        print(f"Found {len(pending_leads)} campaign leads ready to process")
        
        for campaign_lead in pending_leads:
            # Check if campaign is still active
            campaign = db.query(Campaign).filter(
                Campaign.id == campaign_lead.campaign_id,
                Campaign.status == 'active'
            ).first()
            
            if not campaign:
                print(f"Campaign {campaign_lead.campaign_id} not active, skipping")
                continue
            
            # Determine which step to run
            if campaign_lead.status == CampaignLeadStatus.PENDING.value:
                step_index = 1  # Start from first step
            else:
                step_index = campaign_lead.last_step_index + 1
            
            print(f"Triggering step {step_index} for campaign_lead {campaign_lead.id}")
            
            # Trigger the sequence step
            run_sequence_step.delay(str(campaign_lead.id), step_index)
            
            # Update next_run_at to prevent duplicate triggering
            campaign_lead.next_run_at = now + timedelta(days=999)
            
        db.commit()
        
    except Exception as e:
        print(f"Error in check_pending_campaigns: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


def render_template(template: str, lead: Lead) -> str:
    """
    Render email template with lead data.
    
    Simple placeholder replacement for now.
    Supports: {{first_name}}, {{last_name}}, {{company}}, {{title}}
    
    Args:
        template: Template string
        lead: Lead object
        
    Returns:
        Rendered template
    """
    result = template
    result = result.replace("{{first_name}}", lead.first_name or "")
    result = result.replace("{{last_name}}", lead.last_name or "")
    result = result.replace("{{company}}", lead.company or "")
    result = result.replace("{{title}}", lead.title or "")
    result = result.replace("{{email}}", lead.email or "")
    
    return result


@celery_app.task(name="run_sequence_step")
def run_sequence_step(campaign_lead_id: str, step_index: int):
    """
    Execute a specific sequence step for a campaign lead.
    
    Args:
        campaign_lead_id: CampaignLead ID
        step_index: Step index to execute (1-based)
    """
    db = SessionLocal()
    
    try:
        # Load campaign lead
        campaign_lead = db.query(CampaignLead).filter(
            CampaignLead.id == UUID(campaign_lead_id)
        ).first()
        
        if not campaign_lead:
            print(f"CampaignLead {campaign_lead_id} not found")
            return
        
        # Week 3: Check if campaign lead is stopped or replied
        if campaign_lead.status == CampaignLeadStatus.STOPPED.value:
            print(f"CampaignLead {campaign_lead_id} is stopped: {campaign_lead.stop_reason}")
            return
        
        if campaign_lead.replied_at is not None:
            print(f"CampaignLead {campaign_lead_id} has replied, stopping sequence")
            campaign_lead.status = CampaignLeadStatus.STOPPED.value
            campaign_lead.stop_reason = 'reply_received'
            db.commit()
            return
        
        # Load campaign
        campaign = db.query(Campaign).filter(
            Campaign.id == campaign_lead.campaign_id
        ).first()
        
        if not campaign:
            print(f"Campaign {campaign_lead.campaign_id} not found")
            return
        
        # Load sequence step
        step = db.query(SequenceStep).filter(
            SequenceStep.campaign_id == campaign.id,
            SequenceStep.step_index == step_index
        ).first()
        
        if not step:
            # No more steps - mark as completed
            campaign_lead.status = CampaignLeadStatus.COMPLETED.value
            db.commit()
            print(f"Campaign completed for lead {campaign_lead.lead_id}")
            return
        
        # Load lead
        lead = db.query(Lead).filter(
            Lead.id == campaign_lead.lead_id
        ).first()
        
        if not lead:
            print(f"Lead {campaign_lead.lead_id} not found")
            return
        
        # Week 3: Check if lead is marked do_not_contact
        if lead.do_not_contact or lead.is_do_not_contact:
            print(f"Lead {lead.id} is marked do_not_contact, stopping campaign")
            campaign_lead.status = CampaignLeadStatus.STOPPED.value
            campaign_lead.stop_reason = 'do_not_contact'
            db.commit()

            # Audit log the blocked send attempt
            AuditLogger.log_dnc_send_attempt(
                db=db,
                lead_id=lead.id,
                campaign_id=campaign.id,
                blocked=True
            )
            return

        # Enforce daily warmup send cap and pause when limit reached
        enforce_campaign_send_limit(
            db=db,
            campaign_id=campaign.id,
            campaign_lead_id=campaign_lead.id,
            user_id=campaign.user_id,
        )

        db.refresh(campaign_lead)
        if campaign_lead.status == CampaignLeadStatus.STOPPED.value and campaign_lead.stop_reason == 'Daily limit reached':
            logger.warning(f"Campaign lead {campaign_lead.id} paused due to daily limit")
            return
        
        # Get user for sender name
        from app.models.user import User
        user = db.query(User).filter(User.id == campaign.user_id).first()
        sender_name = user.full_name if user and user.full_name else (user.email.split('@')[0] if user else 'Your Company')
        
        # Generate email content (AI or template)
        if step.use_ai_generation and step.product_description:
            try:
                logger.info(f"Generating AI email for lead {lead.id} using tone={step.ai_tone}, goal={step.ai_goal}")
                
                # Generate personalized email using AI (run async function in sync context)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    generated = loop.run_until_complete(generate_email(
                        lead=lead,
                        sender_name=sender_name,
                        tone=step.ai_tone or 'professional',
                        goal=step.ai_goal or 'schedule a meeting',
                        product_description=step.product_description
                    ))
                finally:
                    loop.close()
                
                # Extract subject and body from GeneratedEmail object
                subject = generated.subject
                body = generated.body
                
                logger.info(f"AI generated email for {lead.email}: subject='{subject[:50]}...'")
                
            except Exception as e:
                logger.error(f"AI generation failed for lead {lead.id}: {e}. Falling back to templates.")
                # Fallback to templates if AI fails
                subject = render_template(step.subject_template, lead)
                body = render_template(step.body_template, lead)
        else:
            # Use template rendering (original behavior)
            subject = render_template(step.subject_template, lead)
            body = render_template(step.body_template, lead)
        
        # Send email
        send_email_task.delay(
            user_id=str(campaign.user_id),
            to_email=lead.email,
            subject=subject,
            body=body,
            lead_id=str(lead.id)
        )
        
        # Update campaign lead
        campaign_lead.status = CampaignLeadStatus.IN_PROGRESS.value
        campaign_lead.last_step_index = step_index
        campaign_lead.last_sent_at = datetime.utcnow()
        db.commit()
        
        # Schedule next step if exists
        next_step = db.query(SequenceStep).filter(
            SequenceStep.campaign_id == campaign.id,
            SequenceStep.step_index == step_index + 1
        ).first()
        
        if next_step:
            # Calculate ETA based on delay_days
            eta = datetime.utcnow() + timedelta(days=next_step.delay_days)
            
            # Schedule next step
            run_sequence_step.apply_async(
                args=[campaign_lead_id, step_index + 1],
                eta=eta
            )
            print(f"Scheduled step {step_index + 1} for {eta}")
        else:
            # No more steps - mark as completed
            campaign_lead.status = CampaignLeadStatus.COMPLETED.value
            db.commit()
            print(f"Campaign completed for lead {campaign_lead.lead_id}")
            
    except Exception as e:
        print(f"Error in run_sequence_step: {str(e)}")
        raise
    finally:
        db.close()
