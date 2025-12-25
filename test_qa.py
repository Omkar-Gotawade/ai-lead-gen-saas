"""
Complete QA Testing Suite for Lead Generation Application
Tests Backend APIs, Database, Docker Containers, and System Health
"""
import requests
import subprocess
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"
TEST_USER = "test@example.com"
TEST_PASS = "testpass123"

# Test Results
total_tests = 0
passed_tests = 0
failed_tests = 0
test_details = []

def test(category, name, condition, message=""):
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    
    if condition:
        passed_tests += 1
        status = "✓"
    else:
        failed_tests += 1
        status = "✗"
    
    result = f"{status} [{category:15s}] {name:35s} {message}"
    print(result)
    test_details.append((category, name, condition, message))

print("="*90)
print(f"QA TEST SUITE - Lead Generation Application - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*90 + "\n")

# ============================================================================
# SYSTEM TESTS
# ============================================================================
print("\n[SYSTEM TESTS]")
print("-"*90)

# Docker containers
try:
    result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], 
                          capture_output=True, text=True, timeout=5)
    containers = result.stdout.strip().split('\n')
    
    test("System", "Backend Container", "leadgen_backend" in containers)
    test("System", "Database Container", "leadgen_postgres" in containers)
    test("System", "Redis Container", "leadgen_redis" in containers)
    test("System", "Celery Worker", "leadgen_celery_worker" in containers)
    test("System", "Celery Beat", "leadgen_celery_beat" in containers)
    test("System", "Frontend Container", "leadgen_frontend" in containers)
except Exception as e:
    test("System", "Docker Check", False, f"Error: {e}")

# ============================================================================
# BACKEND API TESTS
# ============================================================================
print("\n[BACKEND API TESTS]")
print("-"*90)

token = None

# Health
try:
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    test("API", "Health Endpoint", r.status_code == 200, f"({r.status_code})")
except Exception as e:
    test("API", "Health Endpoint", False, str(e))

# Auth
try:
    r = requests.post(f"{BASE_URL}/api/auth/login",
                     data={"username": TEST_USER, "password": TEST_PASS}, timeout=5)
    if r.status_code == 200:
        token = r.json().get("access_token")
        test("API", "Login", True, "Token obtained")
    else:
        test("API", "Login", False, f"Status: {r.status_code}")
except Exception as e:
    test("API", "Login", False, str(e))

headers = {"Authorization": f"Bearer {token}"} if token else {}

# Leads
if token:
    try:
        r = requests.get(f"{BASE_URL}/api/leads", headers=headers, timeout=5)
        test("API", "GET /api/leads", r.status_code == 200, f"({r.status_code})")
    except Exception as e:
        test("API", "GET /api/leads", False, str(e))
    
    try:
        r = requests.post(f"{BASE_URL}/api/leads", 
                         json={"email": f"test{int(datetime.now().timestamp())}@test.com",
                               "first_name": "Test", "last_name": "User"},
                         headers=headers, timeout=5)
        test("API", "POST /api/leads", r.status_code in [200, 201], f"({r.status_code})")
    except Exception as e:
        test("API", "POST /api/leads", False, str(e))

# Campaigns
if token:
    try:
        r = requests.get(f"{BASE_URL}/api/campaigns", headers=headers, timeout=5)
        test("API", "GET /api/campaigns", r.status_code == 200, f"({r.status_code})")
    except Exception as e:
        test("API", "GET /api/campaigns", False, str(e))

# Email Provider
if token:
    try:
        r = requests.get(f"{BASE_URL}/api/email-provider", headers=headers, timeout=5)
        test("API", "GET /api/email-provider", r.status_code in [200, 404], f"({r.status_code})")
    except Exception as e:
        test("API", "GET /api/email-provider", False, str(e))

# Metrics
if token:
    try:
        r = requests.get(f"{BASE_URL}/api/metrics", headers=headers, timeout=5)
        test("API", "GET /api/metrics", r.status_code == 200, f"({r.status_code})")
    except Exception as e:
        test("API", "GET /api/metrics", False, str(e))

# ============================================================================
# DATABASE TESTS
# ============================================================================
print("\n[DATABASE TESTS]")
print("-"*90)

try:
    sys.path.insert(0, 'backend')
    from app.database import SessionLocal
    from sqlalchemy import inspect
    from app.models.campaign_lead import CampaignLead
    from app.models.campaign import Campaign
    
    db = SessionLocal()
    inspector = inspect(db.bind)
    
    # Tables
    tables = inspector.get_table_names()
    test("Database", "Table: users", "users" in tables)
    test("Database", "Table: leads", "leads" in tables)
    test("Database", "Table: campaigns", "campaigns" in tables)
    test("Database", "Table: campaign_leads", "campaign_leads" in tables)
    test("Database", "Table: sequence_steps", "sequence_steps" in tables)
    test("Database", "Table: sending_logs", "sending_logs" in tables)
    test("Database", "Table: email_provider_settings", "email_provider_settings" in tables)
    
    # Columns
    if 'campaign_leads' in tables:
        cols = [c['name'] for c in inspector.get_columns('campaign_leads')]
        test("Database", "Column: next_run_at", "next_run_at" in cols)
        test("Database", "Column: current_step_index", "current_step_index" in cols)
        test("Database", "Column: last_sent_at", "last_sent_at" in cols)
    
    # Data checks
    campaign_count = db.query(Campaign).count()
    test("Database", "Has Campaigns", campaign_count > 0, f"({campaign_count} found)")
    
    lead_count = db.query(CampaignLead).count()
    test("Database", "Has Campaign Leads", lead_count > 0, f"({lead_count} enrolled)")
    
    db.close()
    
except Exception as e:
    test("Database", "Connection/Schema", False, str(e))

# ============================================================================
# FRONTEND TESTS
# ============================================================================
print("\n[FRONTEND TESTS]")
print("-"*90)

try:
    r = requests.get(FRONTEND_URL, timeout=5)
    test("Frontend", "Server Running", r.status_code == 200, f"({r.status_code})")
except Exception as e:
    test("Frontend", "Server Running", False, str(e))

# ============================================================================
# RESULTS SUMMARY
# ============================================================================
print("\n" + "="*90)
print("TEST SUMMARY")
print("="*90)
print(f"Total Tests:  {total_tests}")
print(f"Passed:       {passed_tests} ✓")
print(f"Failed:       {failed_tests} ✗")

if total_tests > 0:
    pass_rate = (passed_tests / total_tests) * 100
    print(f"Pass Rate:    {pass_rate:.1f}%")

if failed_tests > 0:
    print("\n" + "="*90)
    print("FAILED TESTS:")
    print("="*90)
    for category, name, passed, msg in test_details:
        if not passed:
            print(f"  ✗ [{category}] {name} - {msg}")
    
    print("\n" + "="*90)
    print("RECOMMENDED ACTIONS:")
    print("="*90)
    
    # Check if database columns missing
    db_failed = any(c == "Database" and not p for c, n, p, m in test_details)
    if db_failed:
        print("\n1. FIX DATABASE SCHEMA:")
        print("   docker exec leadgen_postgres psql -U postgres -d leadgen_db -c \\")
        print('   "ALTER TABLE campaign_leads ADD COLUMN IF NOT EXISTS next_run_at TIMESTAMP;"')
        print("   docker exec leadgen_postgres psql -U postgres -d leadgen_db -c \\")
        print('   "ALTER TABLE campaign_leads ADD COLUMN IF NOT EXISTS current_step_index INTEGER DEFAULT 0;"')
    
    # Check if containers not running
    container_failed = any(c == "System" and not p for c, n, p, m in test_details)
    if container_failed:
        print("\n2. START CONTAINERS:")
        print("   docker compose up -d")
    
    # Check if backend issues
    api_failed = any(c == "API" and not p for c, n, p, m in test_details)
    if api_failed:
        print("\n3. CHECK BACKEND LOGS:")
        print("   docker logs leadgen_backend --tail 50")
        print("   docker compose restart backend")
    
    print("\n")
else:
    print("\n" + "="*90)
    print("✅ ALL TESTS PASSED! Application is fully operational.")
    print("="*90 + "\n")
