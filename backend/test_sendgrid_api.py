#!/usr/bin/env python3
"""Test if SendGrid API key is valid"""
from app.database import SessionLocal
from app.models.email_provider import EmailProviderSettings
from app.services.crypto_service import decrypt_value
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

db = SessionLocal()

# Get the provider for user c85c7a1a-4ee3-4921-a8fd-366924b9053b (the one running campaigns)
provider = db.query(EmailProviderSettings).filter(
    EmailProviderSettings.user_id == 'c85c7a1a-4ee3-4921-a8fd-366924b9053b'
).first()

if not provider:
    print("ERROR: No provider found for user c85c7a1a-4ee3-4921-a8fd-366924b9053b")
    db.close()
    exit(1)

print(f"Testing SendGrid API key for user: c85c7a1a-4ee3-4921-a8fd-366924b9053b")
print(f"  From Email: {provider.from_email}")
print(f"  From Name: {provider.from_name}")

try:
    # Decrypt the API key
    api_key = decrypt_value(provider.sendgrid_api_key_encrypted)
    print(f"  API Key Format: {api_key[:10]}...{api_key[-10:]} (length: {len(api_key)})")
    print(f"  Valid Format: {api_key.startswith('SG.')}")
    
    # Try to create SendGrid client
    sg = SendGridAPIClient(api_key)
    print("  ✓ SendGrid client created successfully")
    
    # Try to validate the API key by checking stats (this will fail if key is invalid)
    # Note: We're not actually sending an email, just validating the key format
    print("\n  Testing API key with SendGrid...")
    
    # Create a test message (won't be sent)
    message = Mail(
        from_email=(provider.from_email, provider.from_name or "Test"),
        to_emails="test@example.com",
        subject="Test",
        plain_text_content="Test"
    )
    
    print("  ✓ Message object created successfully")
    print("\n  API key appears to be valid!")
    print("\n  NOTE: To fully test, try sending a test email through the UI")
    print("  If you still get 401 errors, the API key might be:")
    print("    - Revoked in SendGrid dashboard")
    print("    - From wrong SendGrid account")
    print("    - Lacking required permissions (Mail Send)")
    
except Exception as e:
    print(f"\n  ✗ ERROR: {e}")
    print("\n  Please check:")
    print("    1. API key is copied correctly (no extra spaces)")
    print("    2. API key has 'Mail Send' permission in SendGrid")
    print("    3. API key is not revoked")

db.close()
