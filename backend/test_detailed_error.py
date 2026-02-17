#!/usr/bin/env python3
"""Check detailed SendGrid error response"""
from app.database import SessionLocal
from app.models.email_provider import EmailProviderSettings
from app.services.crypto_service import decrypt_value
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import json

db = SessionLocal()

provider = db.query(EmailProviderSettings).filter(
    EmailProviderSettings.user_id == 'c85c7a1a-4ee3-4921-a8fd-366924b9053b'
).first()

if not provider:
    print("ERROR: No provider found")
    db.close()
    exit(1)

print(f"Testing SendGrid with detailed error info...")
print(f"  From: {provider.from_email}")

try:
    api_key = decrypt_value(provider.sendgrid_api_key_encrypted)
    print(f"  API Key: {api_key[:15]}...{api_key[-15:]} (length: {len(api_key)})")
    
    sg = SendGridAPIClient(api_key)
    
    message = Mail(
        from_email=(provider.from_email, provider.from_name or "AI Cold Email"),
        to_emails=provider.from_email,
        subject="SendGrid Test",
        plain_text_content="This is a test."
    )
    
    print(f"\n  Sending test email...")
    response = sg.send(message)
    
    print(f"\n  ✓ SUCCESS!")
    print(f"  Status: {response.status_code}")
    print(f"  Check your inbox: {provider.from_email}")
    
except Exception as e:
    print(f"\n  ✗ FAILED: {e}")
    
    # Try to get more details
    error_str = str(e)
    
    if hasattr(e, 'body'):
        print(f"\n  Error Body: {e.body}")
    if hasattr(e, 'to_dict'):
        print(f"\n  Error Details: {json.dumps(e.to_dict, indent=2)}")
    
    print(f"\n  Common causes of 401 Unauthorized:")
    print(f"    1. ❌ Sender email '{provider.from_email}' is NOT VERIFIED in SendGrid")
    print(f"       → Go to: https://app.sendgrid.com/settings/sender_auth/senders")
    print(f"       → Add and verify '{provider.from_email}' as a sender")
    print(f"")
    print(f"    2. ❌ API key lacks 'Mail Send' permission")
    print(f"       → Go to: https://app.sendgrid.com/settings/api_keys")
    print(f"       → Check the key has 'Mail Send' or 'Full Access'")
    print(f"")
    print(f"    3. ❌ API key is from wrong SendGrid account")
    print(f"       → Verify the account owns '{provider.from_email}'")

db.close()
