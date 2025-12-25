#!/usr/bin/env python3
"""
Test SendGrid email sending to trigger webhook events
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv('backend/.env')

# Load SendGrid API key from environment
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

def send_test_email():
    message = Mail(
        from_email='test@example.com',
        to_emails='your-email@example.com',  # Replace with your email
        subject='Test SendGrid Webhook',
        html_content='<strong>Testing webhook events!</strong><br><br>Click this link: <a href="https://example.com">Test Link</a>'
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"✅ Email sent successfully!")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"\n📧 Check your inbox: omkarjotawade05@gmail.com")
        print(f"🔍 Then check webhooks page: http://localhost:5173/webhooks")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    send_test_email()
