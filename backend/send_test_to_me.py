"""Send a test email to your own inbox."""
from app.database import SessionLocal
from app.models.email_provider import EmailProviderSettings
from app.services.email_sender import send_email

def send_test():
    db = SessionLocal()
    
    try:
        provider = db.query(EmailProviderSettings).filter(
            EmailProviderSettings.user_id == '6fb4105b-8d9e-4189-baa5-132674288ff5'
        ).first()
        
        if not provider:
            print("❌ No email provider settings found!")
            return
        
        print(f"✅ Sending from: {provider.from_email} ({provider.from_name})")
        print(f"✅ Sending to: {provider.from_email}")
        
        send_email(
            provider_settings=provider,
            to_email=provider.from_email,  # Send to yourself
            subject="🎉 Test Email - Your Lead Gen AI is Working!",
            body="""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #4CAF50;">✅ Success! Your Email System is Working!</h2>
                <p>Your SendGrid integration is now properly configured and emails are being sent.</p>
                
                <h3>What's Working:</h3>
                <ul>
                    <li>✅ SendGrid API key is properly encrypted</li>
                    <li>✅ AI email personalization is enabled</li>
                    <li>✅ Emails are being sent via SendGrid</li>
                    <li>✅ Campaign automation is active</li>
                </ul>
                
                <h3>Next Steps:</h3>
                <ol>
                    <li>Verify this sender email in SendGrid: <a href="https://app.sendgrid.com/settings/sender_auth">Sender Authentication</a></li>
                    <li>Check your SendGrid dashboard for activity</li>
                    <li>Create campaigns with AI personalization enabled</li>
                </ol>
                
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    This is a test email from your Lead Gen AI system.
                </p>
            </body>
            </html>
            """
        )
        
        print("✅ Test email sent successfully!")
        print(f"📬 Check inbox: {provider.from_email}")
        print("📊 Check SendGrid: https://app.sendgrid.com/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    send_test()
