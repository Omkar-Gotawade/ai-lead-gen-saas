"""Reconfigure SMTP with correct Gmail App Password"""
import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_URL = "http://localhost:8000"

# Your Gmail credentials
YOUR_GMAIL = os.getenv('SMTP_USER', 'your-email@gmail.com')
YOUR_APP_PASSWORD = os.getenv('SMTP_PASS', 'your-app-password')  # Gmail App Password
YOUR_NAME = "Lead Gen AI"

print("="*60)
print("RECONFIGURING SMTP EMAIL PROVIDER")
print("="*60)

# Login
print("\n1. Logging in...")
resp = requests.post(f"{API_URL}/auth/login", json={
    "email": "test@example.com",
    "password": "testpass123"
})
print(f"   Status: {resp.status_code}")
token = resp.json()["access_token"]

# Reconfigure SMTP
print("\n2. Updating SMTP configuration...")
resp2 = requests.post(
    f"{API_URL}/api/email-provider/connect",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "provider_type": "smtp",
        "from_name": YOUR_NAME,
        "from_email": YOUR_GMAIL,
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_username": YOUR_GMAIL,
        "smtp_password": YOUR_APP_PASSWORD,
        "use_tls": True,
        "use_ssl": False
    }
)
print(f"   Status: {resp2.status_code}")
print(f"   Response: {resp2.json()}")

# Test sending
print("\n3. Sending test email...")
resp3 = requests.post(
    f"{API_URL}/api/email/send-test",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "to_email": YOUR_GMAIL,
        "subject": "SMTP Test After Reconfiguration",
        "body": "If you receive this, SMTP is working correctly!"
    }
)
print(f"   Status: {resp3.status_code}")
print(f"   Response: {resp3.json()}")

print("\n" + "="*60)
print("DONE! Check Celery logs:")
print("docker logs leadgen_celery_worker --tail 20")
print("="*60)
