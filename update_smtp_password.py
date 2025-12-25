"""Direct database update for SMTP password"""
import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, 'backend')
load_dotenv('backend/.env')

from app.database import SessionLocal
from app.models.email_provider import EmailProviderSettings
from app.services.crypto_service import encrypt_value, decrypt_value

# Your Gmail App Password (without spaces!)
APP_PASSWORD = os.getenv('SMTP_PASS', input('Enter your Gmail App Password: '))
USER_EMAIL = os.getenv('SMTP_USER', input('Enter your email address: '))

print("="*60)
print("UPDATING SMTP PASSWORD DIRECTLY IN DATABASE")
print("="*60)

db = SessionLocal()
try:
    # Get SMTP provider for your email
    provider = db.query(EmailProviderSettings).filter_by(
        provider_type='smtp',
        from_email=USER_EMAIL
    ).first()
    
    if not provider:
        print("ERROR: No SMTP provider found!")
        sys.exit(1)
    
    print(f"\nFound provider: {provider.id}")
    print(f"Current email: {provider.from_email}")
    
    # Decrypt current password to show before
    old_password = decrypt_value(provider.smtp_password_encrypted)
    print(f"Old password: [{old_password}] (length: {len(old_password)})")
    
    # Update password
    provider.smtp_password_encrypted = encrypt_value(APP_PASSWORD)
    db.commit()
    
    # Verify
    db.refresh(provider)
    new_password = decrypt_value(provider.smtp_password_encrypted)
    print(f"New password: [{new_password}] (length: {len(new_password)})")
    print(f"Match: {new_password == APP_PASSWORD}")
    
    print("\n" + "="*60)
    print("DONE! Password updated successfully!")
    print("="*60)
    
finally:
    db.close()
