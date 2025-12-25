"""
Health check script to verify all project components.
Run this to validate that the Week 3 implementation is complete.
"""
import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists."""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {filepath}")
    return exists

def check_imports():
    """Check if Python imports work."""
    print("\n=== Checking Python Imports ===")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from app.models import (
            User, Lead, Campaign, CampaignLead, SequenceStep,
            EmailProviderSettings, SendingLog, InboundEvent, OrgQuota, LeadTag
        )
        print("✓ All models imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def main():
    """Run all health checks."""
    print("=" * 60)
    print("AI Lead Gen SaaS - Week 3 Health Check")
    print("=" * 60)
    
    backend_path = "backend"
    frontend_path = "frontend"
    
    results = []
    
    # Backend Models
    print("\n=== Backend Models ===")
    results.append(check_file_exists(f"{backend_path}/app/models/inbound_event.py", "InboundEvent model"))
    results.append(check_file_exists(f"{backend_path}/app/models/org_quota.py", "OrgQuota model"))
    results.append(check_file_exists(f"{backend_path}/app/models/lead_tag.py", "LeadTag model"))
    
    # Backend Routes
    print("\n=== Backend Routes ===")
    results.append(check_file_exists(f"{backend_path}/app/routes/webhooks.py", "Webhooks routes"))
    results.append(check_file_exists(f"{backend_path}/app/routes/metrics.py", "Metrics routes"))
    results.append(check_file_exists(f"{backend_path}/app/routes/deliverability.py", "Deliverability routes"))
    
    # Backend Services
    print("\n=== Backend Services ===")
    results.append(check_file_exists(f"{backend_path}/app/services/webhook_parser.py", "Webhook parser"))
    results.append(check_file_exists(f"{backend_path}/app/services/quota.py", "Quota service"))
    
    # Migrations
    print("\n=== Database Migrations ===")
    results.append(check_file_exists(f"{backend_path}/alembic/versions/007_week3_webhooks.py", "Week 3 migration"))
    
    # Frontend Pages
    print("\n=== Frontend Pages ===")
    results.append(check_file_exists(f"{frontend_path}/src/pages/MetricsDashboard.jsx", "Metrics Dashboard"))
    results.append(check_file_exists(f"{frontend_path}/src/pages/WebhooksDebug.jsx", "Webhooks Debug"))
    results.append(check_file_exists(f"{frontend_path}/src/pages/Deliverability.jsx", "Deliverability"))
    
    # Configuration
    print("\n=== Configuration Files ===")
    results.append(check_file_exists("docker-compose.yml", "Docker Compose"))
    results.append(check_file_exists(f"{backend_path}/requirements.txt", "Backend requirements"))
    results.append(check_file_exists(f"{frontend_path}/package.json", "Frontend package.json"))
    
    # Scripts
    print("\n=== Utility Scripts ===")
    results.append(check_file_exists("scripts/backup.ps1", "Backup script"))
    results.append(check_file_exists("scripts/restore.ps1", "Restore script"))
    
    # Check Python imports
    results.append(check_imports())
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"Health Check Results: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("✓ All checks passed! Project is ready.")
        return 0
    else:
        print(f"✗ {total - passed} check(s) failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
