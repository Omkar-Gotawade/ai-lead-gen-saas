"""
Simple test script for Gemini API integration - Windows compatible.
Run: python test_simple.py
"""

import requests
import time

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"test_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPassword123!"

print("="*60)
print("TESTING GEMINI INTEGRATION")
print("="*60)

# Test 1: Signup
print("\n[1/8] Testing signup...")
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": TEST_EMAIL,
    "password": TEST_PASSWORD,
    "full_name": "Test User"
})
if response.status_code in [200, 201]:
    print(f"PASS - User created: {TEST_EMAIL}")
    user_data = response.json()
else:
    print(f"FAIL - {response.text}")
    exit(1)

# Test 2: Login
print("\n[2/8] Testing login...")
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": TEST_EMAIL,
    "password": TEST_PASSWORD
})
if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"PASS - Token: {token[:20]}...")
    headers = {"Authorization": f"Bearer {token}"}
else:
    print(f"FAIL - {response.text}")
    exit(1)

# Test 3: Create Lead
print("\n[3/8] Testing lead creation...")
response = requests.post(f"{BASE_URL}/leads", headers=headers, json={
    "email": "john.doe@techcorp.com",
    "first_name": "John",
    "last_name": "Doe",
    "company": "TechCorp Inc",
    "title": "CTO",
    "industry": "Technology",
    "phone": "+1-555-0123"
})
if response.status_code in [200, 201]:
    lead = response.json()
    lead_id = lead["id"]
    print(f"PASS - Lead created: {lead['first_name']} {lead['last_name']}")
    print(f"       Lead ID: {lead_id}")
else:
    print(f"FAIL - {response.text}")
    exit(1)

# Test 4: Gemini Email Generation
print("\n[4/8] Testing Gemini AI email generation...")
print("       (This requires GEMINI_API_KEY in docker-compose.yml)")
response = requests.post(f"{BASE_URL}/api/generate-email", headers=headers, json={
    "lead_id": lead_id,
    "tone": "professional",
    "goal": "schedule a demo",
    "product_description": "AI-powered lead generation platform"
})
if response.status_code == 200:
    email_data = response.json()
    print(f"PASS - Email generated!")
    print(f"       Subject: {email_data['subject']}")
    print(f"       Body preview: {email_data['body'][:80]}...")
    
    # Check personalization
    if 'John' in email_data['body'] or 'TechCorp' in email_data['body']:
        print("       Personalization: YES")
    else:
        print("       Personalization: Not detected")
else:
    print(f"FAIL - {response.text}")
    if "GEMINI_API_KEY" in response.text:
        print("       ACTION NEEDED: Add GEMINI_API_KEY to docker-compose.yml")

# Test 5: Email Provider Config
print("\n[5/8] Testing email provider configuration...")
response = requests.post(f"{BASE_URL}/api/email-providers", headers=headers, json={
    "provider_type": "smtp",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "test@gmail.com",
    "smtp_password": "test_password",
    "from_email": "test@gmail.com",
    "from_name": "Test Sender"
})
if response.status_code in [200, 201]:
    print(f"PASS - Email provider configured")
else:
    print(f"FAIL - {response.text}")

# Test 6: Create Campaign
print("\n[6/8] Testing campaign creation...")
response = requests.post(f"{BASE_URL}/api/campaigns", headers=headers, json={
    "name": "Test Campaign",
    "description": "Testing Gemini integration"
})
if response.status_code in [200, 201]:
    campaign = response.json()
    campaign_id = campaign["id"]
    print(f"PASS - Campaign created: {campaign['name']}")
    print(f"       Campaign ID: {campaign_id}")
else:
    print(f"FAIL - {response.text}")
    exit(1)

# Test 7: Create Sequence Steps
print("\n[7/8] Testing sequence steps...")
step_data = [
    {"step_index": 1, "delay_days": 0, "subject_template": "Hi {{first_name}}", "body_template": "Message 1"},
    {"step_index": 2, "delay_days": 3, "subject_template": "Follow-up", "body_template": "Message 2"}
]
steps_created = 0
for step in step_data:
    response = requests.post(f"{BASE_URL}/api/campaigns/{campaign_id}/steps", headers=headers, json=step)
    if response.status_code in [200, 201]:
        steps_created += 1
        print(f"       Step {step['step_index']}: PASS (Delay: {step['delay_days']} days)")
    else:
        print(f"       Step {step['step_index']}: FAIL - {response.text}")

if steps_created == len(step_data):
    print(f"PASS - All {steps_created} steps created")
else:
    print(f"PARTIAL - {steps_created}/{len(step_data)} steps created")

# Test 8: Enroll Lead
print("\n[8/8] Testing lead enrollment...")
response = requests.post(f"{BASE_URL}/api/{campaign_id}/enqueue", headers=headers, json={
    "lead_ids": [str(lead_id)]
})
if response.status_code in [200, 201]:
    result = response.json()
    print(f"PASS - {result['enqueued_count']} lead(s) enrolled")
    print(f"       Message: {result['message']}")
else:
    print(f"FAIL - {response.text}")

# Summary
print("\n" + "="*60)
print("TESTING COMPLETE")
print("="*60)
print("\nNext steps:")
print("1. Check frontend: http://localhost:5173")
print("2. Add Gemini API key to docker-compose.yml if not done")
print("3. Monitor Celery worker: docker-compose logs -f celery-worker")
print("\nCelery worker should have these tasks registered:")
print("  - enrich_lead")
print("  - send_email_task")
print("  - run_sequence_step")
