#!/usr/bin/env python3
"""Test SendGrid API key decryption and validation"""
from app.database import SessionLocal
from app.models.email_provider import EmailProviderSettings
from app.services.crypto_service import decrypt_value

db = SessionLocal()
providers = db.query(EmailProviderSettings).filter(
    EmailProviderSettings.provider_type == 'sendgrid'
).all()

print(f"\nFound {len(providers)} SendGrid provider(s):\n")

for p in providers:
    print(f"Provider ID: {p.id}")
    print(f"  User ID: {p.user_id}")
    print(f"  From Email: {p.from_email}")
    
    if p.sendgrid_api_key_encrypted:
        try:
            api_key = decrypt_value(p.sendgrid_api_key_encrypted)
            print(f"  Encrypted Key Length: {len(p.sendgrid_api_key_encrypted)}")
            print(f"  Decrypted Key Length: {len(api_key)}")
            print(f"  Key Starts With: {api_key[:3]}...")
            print(f"  Key Format Valid: {api_key.startswith('SG.')}")
            
            if not api_key.startswith('SG.'):
                print(f"  WARNING: SendGrid API keys should start with 'SG.'")
                print(f"  First 20 chars: {api_key[:20]}")
        except Exception as e:
            print(f"  ERROR decrypting: {e}")
    else:
        print(f"  SendGrid API Key: NONE/NULL")
    print()

db.close()
