"""Check campaign status and enrolled leads."""
import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from app.models.campaign import Campaign
from app.models.campaign_lead import CampaignLead
from app.models.lead import Lead
from datetime import datetime

db = SessionLocal()

try:
    # Get campaign
    campaign = db.query(Campaign).order_by(Campaign.created_at.desc()).first()
    if not campaign:
        print("No campaigns found")
        sys.exit(1)
    
    print(f"Campaign: {campaign.name}")
    print(f"Active: {campaign.is_active}")
    print(f"Created: {campaign.created_at}")
    print()
    
    # Get enrolled leads
    campaign_leads = db.query(CampaignLead).filter(
        CampaignLead.campaign_id == campaign.id
    ).all()
    
    print(f"Total enrolled leads: {len(campaign_leads)}")
    print()
    
    if campaign_leads:
        for i, cl in enumerate(campaign_leads[:10], 1):
            lead = db.query(Lead).filter(Lead.id == cl.lead_id).first()
            print(f"Lead {i}: {lead.email if lead else 'Unknown'}")
            print(f"  Status: {cl.status}")
            print(f"  Current step: {cl.current_step_index}")
            print(f"  Next run: {cl.next_run_at}")
            print(f"  Created: {cl.created_at}")
            print()
    
finally:
    db.close()
