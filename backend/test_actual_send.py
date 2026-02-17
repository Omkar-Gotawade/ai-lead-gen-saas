#!/usr/bin/env python3
"""Actually test sending email with SendGrid to verify API key permissions"""
from app.database import SessionLocal
from app.models.email_provider import EmailProviderSettings
from app.services.crypto_service import decrypt_value
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

db = SessionLocal()

# Get the provider for user running campaigns
provider = db.query(EmailProviderSettings).filter(
    EmailProviderSettings.user_id == 'c85c7a1a-4ee3-4921-a8fd-366924b9053b'
).first()

if not provider:
    print("ERROR: No provider found")
    db.close()
    exit(1)

print(f"Testing actual SendGrid email send...")
print(f"  From: {provider.from_email}")

try:
    # Decrypt the API key
    api_key = decrypt_value(provider.sendgrid_api_key_encrypted)
    
    # Create SendGrid client
    sg = SendGridAPIClient(api_key)
    
    # Create a real test message
    message = Mail(
        from_email=(provider.from_email, provider.from_name or "AI Cold Email"),
        to_emails=provider.from_email,  # Send to yourself
        subject="SendGrid API Test",
        plain_text_content="This is a test email to verify SendGrid API key is working correctly."
    )
    
    # Actually try to send
    print(f"\n  Attempting to send test email to: {provider.from_email}")
    print(f"  (This will use 1 email from your SendGrid quota)")
    
    response = sg.send(message)
    
    print(f"\n  ✓ SUCCESS!")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response Headers: {dict(response.headers)}")
    
    if response.status_code in [200, 201, 202]:
        print(f"\n  Email sent successfully!")
        print(f"  Check your inbox: {provider.from_email}")
        print(f"\n  Your SendGrid API key is working correctly!")
    else:
        print(f"\n  Warning: Unexpected status code: {response.status_code}")
        
except Exception as e:
    print(f"\n  ✗ FAILED!")
    print(f"  Error: {e}")
    
    error_str = str(e)
    if "401" in error_str or "Unauthorized" in error_str:
        print(f"\n  401 Unauthorized means:")
        print(f"    1. API key is invalid/revoked")
        print(f"    2. API key is from wrong SendGrid account")
        print(f"    3. Go to SendGrid > Settings > API Keys")
        print(f"    4. Create NEW API key with 'Full Access' or 'Mail Send' permission")
        print(f"    5. Copy the NEW key (starts with SG.)")
        print(f"    6. Update in app Settings page")
    elif "403" in error_str or "Forbidden" in error_str:
        print(f"\n  403 Forbidden means:")
        print(f"    1. API key doesn't have 'Mail Send' permission")
        print(f"    2. Create new API key with proper permissions")
    else:
        print(f"\n  Check your SendGrid account at: https://app.sendgrid.com/")

db.close()
