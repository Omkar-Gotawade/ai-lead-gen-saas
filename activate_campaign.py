"""Manually activate campaign and set next_run_at for all leads."""
import sys
sys.path.insert(0, 'backend')

from datetime import datetime
from app.database import SessionLocal
from app.models.campaign import Campaign, CampaignStatus
from app.models.campaign_lead import CampaignLead, CampaignLeadStatus

db = SessionLocal()

try:
    # Get the latest campaign
    campaign = db.query(Campaign).order_by(Campaign.created_at.desc()).first()
    
    if not campaign:
        print("No campaign found")
        sys.exit(1)
    
    print(f"Campaign: {campaign.name}")
    print(f"Current status: {campaign.status}")
    
    # Set campaign to active
    campaign.status = CampaignStatus.ACTIVE
    
    # Get all campaign leads
    campaign_leads = db.query(CampaignLead).filter(
        CampaignLead.campaign_id == campaign.id
    ).all()
    
    print(f"\nFound {len(campaign_leads)} enrolled leads")
    
    # Set next_run_at to now for all pending/in_progress leads
    now = datetime.utcnow()
    updated = 0
    
    for cl in campaign_leads:
        if cl.status in [CampaignLeadStatus.PENDING.value, CampaignLeadStatus.IN_PROGRESS.value]:
            cl.next_run_at = now
            cl.status = CampaignLeadStatus.PENDING.value
            cl.current_step_index = 0
            updated += 1
            print(f"  Updated lead {cl.lead_id}: next_run_at={now}")
    
    db.commit()
    
    print(f"\n✅ Campaign activated!")
    print(f"✅ Set next_run_at for {updated} leads")
    print(f"\nCelery Beat will process these leads within 60 seconds.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
