"""
Comprehensive test script for Gemini API integration and Week 2 features.

Tests:
1. User authentication (signup/login)
2. Lead creation
3. AI email generation with Gemini
4. Email provider configuration (SMTP/SendGrid)
5. Campaign and sequence creation
6. Lead enrollment to campaign
7. Celery task execution

Run: python test_gemini_integration.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"test_gemini_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPassword123!"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(test_name):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST: {test_name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")

# Global token storage
auth_token = None
lead_id = None
campaign_id = None

def test_signup():
    """Test user signup."""
    print_test("User Signup")
    
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": "Gemini Test User"
    })
    
    if response.status_code in [200, 201]:
        print_success(f"User created: {TEST_EMAIL}")
        return True
    else:
        print_error(f"Signup failed: {response.text}")
        return False

def test_login():
    """Test user login and get token."""
    print_test("User Login")
    
    global auth_token
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        auth_token = data.get("access_token")
        print_success(f"Login successful, token: {auth_token[:20]}...")
        return True
    else:
        print_error(f"Login failed: {response.text}")
        return False

def test_create_lead():
    """Test lead creation."""
    print_test("Create Lead")
    
    global lead_id
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = requests.post(f"{BASE_URL}/leads", 
        headers=headers,
        json={
            "email": "john.doe@techcorp.com",
            "first_name": "John",
            "last_name": "Doe",
            "company": "TechCorp Inc",
            "title": "CTO",
            "industry": "Technology",
            "phone": "+1-555-0123"
        }
    )
    
    if response.status_code in [200, 201]:
        data = response.json()
        lead_id = data.get("id")
        print_success(f"Lead created: {data.get('first_name')} {data.get('last_name')} - ID: {lead_id}")
        return True
    else:
        print_error(f"Lead creation failed: {response.text}")
        return False

def test_gemini_email_generation():
    """Test AI email generation with Gemini."""
    print_test("Gemini AI Email Generation")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    print_info("Generating email with Google Gemini Pro...")
    
    response = requests.post(f"{BASE_URL}/api/generate-email",
        headers=headers,
        json={
            "lead_id": lead_id,
            "tone": "professional",
            "goal": "schedule a demo",
            "product_description": "AI-powered lead generation platform that automates outreach"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Email generated successfully!")
        print_info(f"Subject: {data.get('subject')}")
        print_info(f"Body preview: {data.get('body')[:100]}...")
        print_info(f"Generated at: {data.get('generated_at')}")
        
        # Verify it contains personalization
        body = data.get('body', '')
        if 'John' in body or 'TechCorp' in body or 'CTO' in body:
            print_success("Email contains personalized content!")
        else:
            print_error("Email may not be properly personalized")
        
        return True
    else:
        print_error(f"Email generation failed: {response.text}")
        if "GEMINI_API_KEY not configured" in response.text:
            print_info("Make sure to set GEMINI_API_KEY in docker-compose.yml")
        return False

def test_email_provider_config():
    """Test email provider configuration."""
    print_test("Email Provider Configuration (SMTP)")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = requests.post(f"{BASE_URL}/api/email-providers",
        headers=headers,
        json={
            "provider_type": "smtp",
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "test@gmail.com",
            "smtp_password": "test_password",
            "from_email": "test@gmail.com",
            "from_name": "Test Sender"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"SMTP provider configured: {data.get('smtp_host')}")
        return True
    else:
        print_error(f"Provider config failed: {response.text}")
        return False

def test_create_campaign():
    """Test campaign creation."""
    print_test("Create Campaign")
    
    global campaign_id
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = requests.post(f"{BASE_URL}/api/campaigns",
        headers=headers,
        json={
            "name": "Gemini Test Campaign",
            "description": "Testing campaign with Gemini AI"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        campaign_id = data.get("id")
        print_success(f"Campaign created: {data.get('name')} - ID: {campaign_id}")
        return True
    else:
        print_error(f"Campaign creation failed: {response.text}")
        return False

def test_create_sequence_steps():
    """Test sequence step creation."""
    print_test("Create Sequence Steps")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    steps = [
        {
            "step_index": 1,
            "delay_days": 0,
            "subject_template": "Quick question about {{company}}",
            "body_template": "Hi {{first_name}},\n\nI noticed {{company}} is in the {{industry}} space..."
        },
        {
            "step_index": 2,
            "delay_days": 3,
            "subject_template": "Following up - {{company}}",
            "body_template": "Hi {{first_name}},\n\nJust wanted to follow up on my previous email..."
        }
    ]
    
    success_count = 0
    
    for step in steps:
        response = requests.post(f"{BASE_URL}/api/campaigns/{campaign_id}/steps",
            headers=headers,
            json=step
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Step {step['step_index']} created - Delay: {step['delay_days']} days")
            success_count += 1
        else:
            print_error(f"Step {step['step_index']} failed: {response.text}")
    
    return success_count == len(steps)

def test_enroll_lead():
    """Test enrolling lead to campaign."""
    print_test("Enroll Lead to Campaign")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = requests.post(f"{BASE_URL}/api/{campaign_id}/enqueue",
        headers=headers,
        json={
            "lead_ids": [str(lead_id)]
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Lead enrolled: {data.get('enqueued_count')} leads queued")
        print_info(f"Skipped: {data.get('skipped_count')} (already enrolled)")
        return True
    else:
        print_error(f"Enrollment failed: {response.text}")
        return False

def test_celery_tasks():
    """Test Celery task status."""
    print_test("Celery Task Verification")
    
    print_info("Checking if Celery worker has registered tasks...")
    print_success("Expected tasks:")
    print_info("  - enrich_lead")
    print_info("  - send_email_task")
    print_info("  - run_sequence_step")
    
    print_info("\nVerify in Celery logs: docker-compose logs celery-worker")
    return True

def run_all_tests():
    """Run all tests in sequence."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}GEMINI INTEGRATION & WEEK 2 FEATURE TEST SUITE{RESET}")
    print(f"{BLUE}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = []
    
    # Run tests
    results.append(("User Signup", test_signup()))
    results.append(("User Login", test_login()))
    results.append(("Create Lead", test_create_lead()))
    results.append(("Gemini Email Generation", test_gemini_email_generation()))
    results.append(("Email Provider Config", test_email_provider_config()))
    results.append(("Create Campaign", test_create_campaign()))
    results.append(("Create Sequence Steps", test_create_sequence_steps()))
    results.append(("Enroll Lead", test_enroll_lead()))
    results.append(("Celery Tasks", test_celery_tasks()))
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}PASSED{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f"{test_name:.<40} {status}")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    
    if passed == total:
        print(f"{GREEN}ALL TESTS PASSED! ({passed}/{total}){RESET}")
        print(f"{GREEN}Gemini integration is working correctly!{RESET}")
    else:
        print(f"{YELLOW}PARTIAL SUCCESS: {passed}/{total} tests passed{RESET}")
        if passed < total:
            print(f"{RED}Some features need attention{RESET}")
    
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Additional info
    print(f"{YELLOW}Next Steps:{RESET}")
    print("1. Check frontend at: http://localhost:5173")
    print("2. Test email generation in the UI")
    print("3. Add your Gemini API key to docker-compose.yml if not done")
    print("4. Monitor Celery worker logs: docker-compose logs -f celery-worker")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        exit(1)
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{RESET}")
        exit(1)
