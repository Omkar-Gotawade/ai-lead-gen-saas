#!/usr/bin/env python3
"""Check SendGrid API keys in database"""
from app.database import SessionLocal
from app.models.email_provider import EmailProviderSettings

db = SessionLocal()
providers = db.query(EmailProviderSettings).all()

print(f"\nFound {len(providers)} email provider(s):\n")
for p in providers:
    print(f"Provider ID: {p.id}")
    print(f"  User ID: {p.user_id}")
    print(f"  Type: {p.provider_type}")
    print(f"  From Email: {p.from_email}")
    print(f"  From Name: {p.from_name}")
    
    if p.provider_type.value == 'sendgrid':
        if p.sendgrid_api_key_encrypted:
            print(f"  SendGrid API Key: {p.sendgrid_api_key_encrypted[:10]}...{p.sendgrid_api_key_encrypted[-5:]} (length: {len(p.sendgrid_api_key_encrypted)})")
        else:
            print(f"  SendGrid API Key: NONE/NULL")
    else:
        if p.smtp_password_encrypted:
            print(f"  SMTP Password: {p.smtp_password_encrypted[:10]}...{p.smtp_password_encrypted[-5:]} (length: {len(p.smtp_password_encrypted)})")
        else:
            print(f"  SMTP Password: NONE/NULL")
    print()

db.close()
