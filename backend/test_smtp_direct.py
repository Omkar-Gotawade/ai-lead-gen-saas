"""Test SMTP connection directly"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

print("="*60)
print("DIRECT SMTP TEST")
print("="*60)

# Your Gmail credentials
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your-email@gmail.com"
SMTP_PASS = "your-app-password"  # Gmail App Password
FROM_EMAIL = "your-email@gmail.com"
FROM_NAME = "Lead Gen AI"
TO_EMAIL = "recipient@example.com"

try:
    print(f"\n1. Connecting to {SMTP_HOST}:{SMTP_PORT}...")
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    print("   ✓ Connected")
    
    print("\n2. Starting TLS...")
    server.starttls()
    print("   ✓ TLS enabled")
    
    print("\n3. Logging in...")
    server.login(SMTP_USER, SMTP_PASS)
    print("   ✓ Logged in")
    
    print("\n4. Sending test email...")
    msg = MIMEMultipart()
    msg['Subject'] = "Test Email from Lead Gen System"
    msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg['To'] = TO_EMAIL
    
    body = "This is a test email to verify SMTP configuration works!"
    msg.attach(MIMEText(body, 'plain'))
    
    server.sendmail(FROM_EMAIL, [TO_EMAIL], msg.as_string())
    print("   ✓ Email sent!")
    
    server.quit()
    print("\n" + "="*60)
    print("SUCCESS! Check your inbox at:", TO_EMAIL)
    print("="*60)
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    print("\nPossible issues:")
    print("1. App password may be incorrect")
    print("2. 2FA not enabled on Google account")
    print("3. Less secure app access blocked")
    print("="*60)
