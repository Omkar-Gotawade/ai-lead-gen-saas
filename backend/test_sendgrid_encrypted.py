"""Test SendGrid email with properly encrypted API key."""
from app.database import SessionLocal
from app.models.email_provider import EmailProviderSettings
from app.services.email_sender import send_email

def test_sendgrid():
    """Send a test email using SendGrid with encrypted credentials."""
    db = SessionLocal()
    
    try:
        # Get the email provider settings for the active user
        provider = db.query(EmailProviderSettings).filter(
            EmailProviderSettings.user_id == '6fb4105b-8d9e-4189-baa5-132674288ff5'
        ).first()
        
        if not provider:
            print("❌ No email provider settings found!")
            return
        
        print(f"✅ Found provider: {provider.provider_type}")
        print(f"   From: {provider.from_email} ({provider.from_name})")
        print(f"   API key encrypted: {provider.sendgrid_api_key_encrypted[:50]}...")
        
        # Send test email
        print("\n📧 Sending test email...")
        send_email(
            provider_settings=provider,
            to_email="omkargotawade05@gmail.com",  # Send to yourself
            subject="🎉 Test Email - SendGrid Encryption Fixed!",
            body="""
            <html>
            <body>
                <h2>Success!</h2>
                <p>Your SendGrid API key is now properly encrypted and emails are working! 🚀</p>
                <p>This email was sent with AI personalization enabled.</p>
                <p><strong>From:</strong> Lead Gen AI System</p>
            </body>
            </html>
            """
        )
        
        print("✅ Email sent successfully!")
        print("📊 Check SendGrid dashboard: https://app.sendgrid.com/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_sendgrid()
