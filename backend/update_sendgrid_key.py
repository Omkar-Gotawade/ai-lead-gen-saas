#!/usr/bin/env python3
"""Update SendGrid API key for a user"""
import sys
from app.database import SessionLocal
from app.models.email_provider import EmailProviderSettings
from app.services.crypto_service import encrypt_value

# Get the new API key from command line argument
if len(sys.argv) < 2:
    print("Usage: python update_sendgrid_key.py <NEW_API_KEY>")
    print("\nExample: python update_sendgrid_key.py SG.abc123...")
    sys.exit(1)

new_api_key = sys.argv[1].strip()

# Validate API key format
if not new_api_key.startswith('SG.'):
    print("ERROR: SendGrid API keys should start with 'SG.'")
    print(f"Your key starts with: {new_api_key[:5]}")
    sys.exit(1)

if len(new_api_key) < 50:
    print("WARNING: SendGrid API keys are usually 60-70+ characters long")
    print(f"Your key is only {len(new_api_key)} characters")
    response = input("Continue anyway? (yes/no): ")
    if response.lower() != 'yes':
        sys.exit(1)

# Update the database
db = SessionLocal()

try:
    # Get the provider for omkargotawade05@gmail.com
    provider = db.query(EmailProviderSettings).filter(
        EmailProviderSettings.user_id == 'c85c7a1a-4ee3-4921-a8fd-366924b9053b'
    ).first()
    
    if not provider:
        print("ERROR: No provider found for omkargotawade05@gmail.com")
        db.close()
        sys.exit(1)
    
    print(f"\nUpdating API key for: {provider.from_email}")
    print(f"  Old key: {new_api_key[:10]}...{new_api_key[-10:]}")
    
    # Encrypt and save the new API key
    encrypted_key = encrypt_value(new_api_key)
    provider.sendgrid_api_key_encrypted = encrypted_key
    
    db.commit()
    
    print(f"  ✓ API key updated successfully!")
    print(f"\nNext steps:")
    print(f"  1. Restart Celery: docker-compose restart celery-worker celery-beat")
    print(f"  2. Test by sending a campaign email")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    db.rollback()
finally:
    db.close()
