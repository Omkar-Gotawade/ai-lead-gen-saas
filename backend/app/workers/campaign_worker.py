"""Celery tasks for campaign execution."""
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.campaign import Campaign
from app.models.campaign_lead import CampaignLead, CampaignLeadStatus
from app.models.sequence_step import SequenceStep
from app.models.lead import Lead
from app.workers.email_worker import send_email_task


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
        
        if campaign_lead.status == CampaignLeadStatus.STOPPED.value:
            print(f"CampaignLead {campaign_lead_id} is stopped")
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
        
        # Render email templates
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
