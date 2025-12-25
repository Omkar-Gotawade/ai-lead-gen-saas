"""Send email to omkargotawade16@gmail.com specifically"""
import requests

API_URL = "http://localhost:8000"

print("="*60)
print("SENDING EMAIL TO: omkargotawade16@gmail.com")
print("="*60)

# Login
resp = requests.post(f"{API_URL}/auth/login", json={
    "email": "test@example.com",
    "password": "testpass123"
})
token = resp.json()["access_token"]

# Send test email to omkargotawade16
print("\n📧 Sending test email...")
resp = requests.post(
    f"{API_URL}/api/email/send-test",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "to_email": "omkargotawade16@gmail.com",
        "subject": "Quick thought for Ai Automation",
        "body": """Hi test 2,

I hope this email finds you well.

I was looking into Ai Automation and the innovative work you're doing in the AI space. It's clear that effectively communicating your unique value is essential for reaching the right clients and driving growth.

My team specializes in helping technology companies like yours translate complex solutions into clear, compelling marketing messages. We focus on strategies that attract genuine interest and expand your reach.

Would you be open to a brief 15-minute call sometime next week to discuss some tailored marketing ideas for Ai Automation?

Best regards,
Lead gen ai"""
    }
)

print(f"✓ Status: {resp.status_code}")
print(f"✓ Response: {resp.json()}")

print("\n⏳ Waiting 5 seconds for Celery to process...")
import time
time.sleep(5)

# Check if it was sent
print("\n📋 Checking send status...")
import subprocess
result = subprocess.run([
    'docker', 'exec', 'leadgen_backend', 'python', '-c',
    "from app.database import SessionLocal; from app.models.sending_log import SendingLog; db=SessionLocal(); log=db.query(SendingLog).filter(SendingLog.to_email=='omkargotawade16@gmail.com').order_by(SendingLog.created_at.desc()).first(); print(f'Status: {log.status.value}'); print(f'Error: {log.error_message or \"None\"}')"
], capture_output=True, text=True)
print(result.stdout)

print("\n" + "="*60)
print("✓ If Status = 'sent', check:")
print("  1. Inbox at omkargotawade16@gmail.com")
print("  2. SPAM/Junk folder")
print("  3. Promotions tab")
print("  4. Wait 1-2 minutes for delivery")
print("\n✗ If Status = 'failed', check error message above")
print("="*60)
