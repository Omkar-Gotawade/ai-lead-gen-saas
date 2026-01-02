#!/usr/bin/env python3
"""
Orphan Record Detector - Finds orphaned campaign_leads with invalid foreign keys
Usage: python detect_orphans.py [--cleanup]
Exit Code: 0 = no orphans, 1 = orphans found
"""

import sys
import subprocess
import argparse
from typing import List, Dict

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

def run_python_code(code: str) -> tuple[int, str]:
    """Run Python code in backend container"""
    cmd = [
        "docker-compose", "exec", "-T", "backend",
        "python", "-c", code
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout + result.stderr
    except Exception as e:
        return 1, str(e)

def find_orphan_campaign_leads() -> List[Dict]:
    """Find campaign_leads with invalid campaign_id or lead_id"""
    code = """
from app.database import SessionLocal
from app.models.campaign_lead import CampaignLead
from app.models.campaign import Campaign
from app.models.lead import Lead
from sqlalchemy import and_

db = SessionLocal()

# Find campaign_leads where campaign doesn't exist
orphans = []
all_campaign_leads = db.query(CampaignLead).all()

for cl in all_campaign_leads:
    # Check if campaign exists
    campaign_exists = db.query(Campaign).filter(Campaign.id == cl.campaign_id).first() is not None
    # Check if lead exists
    lead_exists = db.query(Lead).filter(Lead.id == cl.lead_id).first() is not None
    
    if not campaign_exists or not lead_exists:
        print(f"ORPHAN|{cl.id}|{cl.campaign_id}|{cl.lead_id}|{campaign_exists}|{lead_exists}")

db.close()
print("DONE")
"""
    
    exit_code, output = run_python_code(code)
    
    orphans = []
    for line in output.split('\n'):
        if line.startswith('ORPHAN|'):
            parts = line.split('|')
            orphans.append({
                'id': int(parts[1]),
                'campaign_id': int(parts[2]),
                'lead_id': int(parts[3]),
                'campaign_exists': parts[4] == 'True',
                'lead_exists': parts[5] == 'True'
            })
    
    return orphans

def find_orphan_sending_logs() -> List[Dict]:
    """Find sending_logs with invalid lead_id"""
    code = """
from app.database import SessionLocal
from app.models.sending_log import SendingLog
from app.models.lead import Lead

db = SessionLocal()

logs = db.query(SendingLog).all()
for log in logs:
    if log.lead_id:
        lead_exists = db.query(Lead).filter(Lead.id == log.lead_id).first() is not None
        if not lead_exists:
            print(f"ORPHAN_LOG|{log.id}|{log.lead_id}|{log.to_email}")

db.close()
print("DONE")
"""
    
    exit_code, output = run_python_code(code)
    
    orphans = []
    for line in output.split('\n'):
        if line.startswith('ORPHAN_LOG|'):
            parts = line.split('|')
            orphans.append({
                'id': int(parts[1]),
                'lead_id': int(parts[2]),
                'to_email': parts[3]
            })
    
    return orphans

def cleanup_orphan_campaign_leads(orphan_ids: List[int]) -> bool:
    """Delete orphaned campaign_leads"""
    code = f"""
from app.database import SessionLocal
from app.models.campaign_lead import CampaignLead

db = SessionLocal()
ids = {orphan_ids}

deleted = db.query(CampaignLead).filter(CampaignLead.id.in_(ids)).delete(synchronize_session=False)
db.commit()
print(f"DELETED:{{deleted}}")
db.close()
"""
    
    exit_code, output = run_python_code(code)
    return "DELETED:" in output

def main():
    parser = argparse.ArgumentParser(description='Detect orphaned records with invalid foreign keys')
    parser.add_argument('--cleanup', action='store_true', help='Delete orphaned records')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔍 Orphan Record Detector")
    print("=" * 60)
    print()
    
    has_issues = False
    
    # Check campaign_leads
    print("Scanning campaign_leads for orphans...")
    orphan_cls = find_orphan_campaign_leads()
    
    if orphan_cls:
        has_issues = True
        print(f"\n{Colors.RED}✗ Found {len(orphan_cls)} orphaned campaign_lead(s):{Colors.RESET}\n")
        
        for orphan in orphan_cls[:10]:  # Show first 10
            print(f"  ID: {orphan['id']}")
            if not orphan['campaign_exists']:
                print(f"    {Colors.RED}✗ Campaign {orphan['campaign_id']} does not exist{Colors.RESET}")
            if not orphan['lead_exists']:
                print(f"    {Colors.RED}✗ Lead {orphan['lead_id']} does not exist{Colors.RESET}")
        
        if len(orphan_cls) > 10:
            print(f"  ... and {len(orphan_cls) - 10} more")
        
        if args.cleanup:
            print(f"\n{Colors.YELLOW}Cleaning up orphaned campaign_leads...{Colors.RESET}", end=" ")
            if cleanup_orphan_campaign_leads([o['id'] for o in orphan_cls]):
                print(f"{Colors.GREEN}✓ Deleted{Colors.RESET}")
            else:
                print(f"{Colors.RED}✗ Failed{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}✓ No orphaned campaign_leads{Colors.RESET}")
    
    # Check sending_logs
    print("\nScanning sending_logs for orphans...")
    orphan_logs = find_orphan_sending_logs()
    
    if orphan_logs:
        has_issues = True
        print(f"\n{Colors.YELLOW}⚠ Found {len(orphan_logs)} orphaned sending_log(s):{Colors.RESET}\n")
        
        for orphan in orphan_logs[:10]:
            print(f"  Log ID: {orphan['id']}, Lead ID: {orphan['lead_id']}, Email: {orphan['to_email']}")
        
        if len(orphan_logs) > 10:
            print(f"  ... and {len(orphan_logs) - 10} more")
        
        print(f"\n{Colors.YELLOW}Note: Sending logs are historical - consider keeping them.{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}✓ No orphaned sending_logs{Colors.RESET}")
    
    # Summary
    print("\n" + "=" * 60)
    
    if not has_issues:
        print(f"{Colors.GREEN}✓ No orphaned records found!{Colors.RESET}")
        print("=" * 60)
        return 0
    else:
        print(f"{Colors.RED}✗ Orphaned records detected{Colors.RESET}")
        if not args.cleanup:
            print(f"\n{Colors.YELLOW}To clean up orphaned records, run:{Colors.RESET}")
            print(f"  python {sys.argv[0]} --cleanup")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
