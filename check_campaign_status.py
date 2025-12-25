"""Check campaign enrollment status"""
import sys
sys.path.insert(0, 'd:/lead gen/backend')

from app.database import SessionLocal
from app.models.campaign import Campaign
from app.models.campaign_lead import CampaignLead
from app.models.lead import Lead

db = SessionLocal()

print("="*60)
print("CAMPAIGN STATUS CHECK")
print("="*60)

# Find campaign
campaign = db.query(Campaign).filter(
    Campaign.name == "Lead outreach"
).first()

if not campaign:
    print("\n❌ Campaign 'Lead outreach' not found")
else:
    print(f"\n✓ Campaign: {campaign.name}")
    print(f"✓ Status: {campaign.status.value}")
    print(f"✓ Created: {campaign.created_at}")
    
    # Check enrolled leads
    enrolled = db.query(CampaignLead).filter(
        CampaignLead.campaign_id == campaign.id
    ).all()
    
    print(f"\n📊 Enrolled Leads: {len(enrolled)}")
    
    if len(enrolled) == 0:
        print("\n" + "="*60)
        print("⚠️  NO LEADS ENROLLED IN CAMPAIGN!")
        print("="*60)
        print("\nTo add leads:")
        print("1. Go to Leads page")
        print("2. Select leads (checkboxes)")
        print("3. Click 'Add to Campaign' button")
        print("4. Choose 'Lead outreach' campaign")
        print("5. Click 'Add'")
    else:
        print("\nEnrolled Leads:")
        for i, cl in enumerate(enrolled, 1):
            lead = db.query(Lead).filter(Lead.id == cl.lead_id).first()
            print(f"\n  {i}. {lead.first_name} {lead.last_name} ({lead.email})")
            print(f"     Status: {cl.status}")
            print(f"     Last Step: {cl.last_step_index}")
            print(f"     Last Sent: {cl.last_sent_at or 'Never'}")

db.close()
