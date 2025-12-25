"""Manually trigger campaign email for testing."""
import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from app.models.campaign_lead import CampaignLead
from app.workers.campaign_worker import run_sequence_step

db = SessionLocal()

try:
    # Get first campaign lead
    campaign_lead = db.query(CampaignLead).first()
    
    if not campaign_lead:
        print("No campaign leads found")
        sys.exit(1)
    
    print(f"Campaign Lead ID: {campaign_lead.id}")
    print(f"Status: {campaign_lead.status}")
    print(f"Current step: {campaign_lead.current_step_index}")
    print(f"\nManually triggering step 1...")
    
    # Call the function directly
    run_sequence_step(str(campaign_lead.id), 1)
    
    print("✅ Done! Check email.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
