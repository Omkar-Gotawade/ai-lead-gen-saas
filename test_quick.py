"""Quick test of improved AI email generation"""
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "test@example.com",
    "password": "testpass123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create lead with rich research notes
print("\n" + "="*70)
print("Creating lead with detailed research notes...")
print("="*70)

lead_data = {
    "first_name": "Sarah",
    "last_name": "Chen",
    "email": "sarah@rocketreach.com",
    "company": "RocketReach",
    "title": "VP of Sales",
    "industry": "B2B SaaS",
    "company_size": "200+",
    "location": "San Francisco, CA",
    "research_notes": "Raised Series A $5M Dec 2024 | Hiring 7 SDRs (growing from 5 to 12) | Uses Outreach + Salesforce | Posted on LinkedIn about scaling challenges | Team hitting 10K emails/day"
}

response = requests.post(f"{BASE_URL}/leads", headers=headers, json=lead_data)
lead_id = response.json()["id"]
print(f"\n✓ Lead created")
print(f"  Research: {lead_data['research_notes']}")

# Generate email
print("\n" + "="*70)
print("Generating personalized email...")
print("="*70)

response = requests.post(f"{BASE_URL}/api/generate-email", headers=headers, json={
    "lead_id": lead_id,
    "tone": "professional",
    "goal": "schedule a demo",
    "product_description": "email deliverability monitoring platform that prevents domain reputation issues"
})

if response.status_code == 200:
    email = response.json()
    print(f"\nSUBJECT: {email['subject']}\n")
    print(email['body'])
    print("\n" + "="*70)
    
    # Check if it used research
    body_lower = email['body'].lower()
    used_research = any(x in body_lower for x in ['5', '12', 'hiring', 'series a', 'outreach', 'salesforce', '10k'])
    
    if used_research:
        print("✅ Email references specific research details!")
    else:
        print("⚠️ Email is generic - not using research notes")
else:
    print(f"Error: {response.text}")
