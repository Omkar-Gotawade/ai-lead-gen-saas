"""Diagnose campaign issues."""
import sys
sys.path.insert(0, 'backend')

from datetime import datetime
from app.database import SessionLocal
from app.models.campaign import Campaign
from app.models.campaign_lead import CampaignLead
from app.models.lead import Lead
from sqlalchemy import inspect

db = SessionLocal()

try:
    inspector = inspect(db.bind)
    columns = [col['name'] for col in inspector.get_columns('campaign_leads')]
    
    print("=" * 60)
    print("CAMPAIGN COLUMNS:", columns)
    print("=" * 60)
    
    campaign = db.query(Campaign).first()
    print(f"\nCampaign: {campaign.name if campaign else 'None'}")
    print(f"Status: {campaign.status if campaign else 'N/A'}")
    
    cls = db.query(CampaignLead).limit(3).all()
    print(f"\nEnrolled leads: {len(cls)}")
    
    for cl in cls:
        lead = db.query(Lead).filter(Lead.id == cl.lead_id).first()
        print(f"\n  {lead.email if lead else 'Unknown'}")
        print(f"    status: {cl.status}")
        for col in ['current_step_index', 'next_run_at', 'last_step_index', 'last_sent_at']:
            if col in columns:
                val = getattr(cl, col, 'N/A')
                print(f"    {col}: {val}")
    
    print("\n" + "=" * 60)
    if 'next_run_at' not in columns:
        print("❌ MISSING: next_run_at column")
        print("RUN: docker exec leadgen_postgres psql -U postgres -d leadgen_db -c \"ALTER TABLE campaign_leads ADD COLUMN next_run_at TIMESTAMP;\"")
    if 'current_step_index' not in columns:
        print("❌ MISSING: current_step_index column")  
        print("RUN: docker exec leadgen_postgres psql -U postgres -d leadgen_db -c \"ALTER TABLE campaign_leads ADD COLUMN current_step_index INTEGER DEFAULT 0;\"")
    
    if campaign and campaign.status != 'active':
        print(f"❌ Campaign not active (status={campaign.status})")
        print(f"RUN: docker exec leadgen_postgres psql -U postgres -d leadgen_db -c \"UPDATE campaigns SET status = 'active';\"")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
