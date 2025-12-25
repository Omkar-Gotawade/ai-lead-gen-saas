"""
Configure SMTP for your current user
Run this after logging into the frontend
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

# Get these from your browser's localStorage after logging in
# 1. Open http://localhost:5173
# 2. Login with your user
# 3. Press F12 -> Console tab
# 4. Run: localStorage.getItem('token')
# 5. Copy the token here
YOUR_TOKEN = "paste-your-token-here"

# Your Gmail credentials
YOUR_GMAIL = os.getenv('SMTP_USER', 'your-email@gmail.com')
YOUR_APP_PASSWORD = os.getenv('SMTP_PASS', 'your-app-password')
YOUR_NAME = "Lead Gen AI"

API_URL = "http://localhost:8000"

def configure_smtp():
    if YOUR_TOKEN == "paste-your-token-here":
        print("❌ Please get your token from the browser first!")
        print("\n📋 Instructions:")
        print("1. Open http://localhost:5173 and login")
        print("2. Press F12 to open Developer Console")
        print("3. Go to Console tab")
        print("4. Type: localStorage.getItem('token')")
        print("5. Copy the token and paste it in this file")
        print("6. Run this script again")
        return
    
    print("📧 Configuring SMTP for your user...")
    
    app_password = YOUR_APP_PASSWORD.replace(" ", "")
    
    response = requests.post(
        f"{API_URL}/api/email-provider/connect",
        headers={
            "Authorization": f"Bearer {YOUR_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "provider_type": "smtp",
            "from_name": YOUR_NAME,
            "from_email": YOUR_GMAIL,
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": YOUR_GMAIL,
            "smtp_password": app_password,
            "use_tls": True,
            "use_ssl": False
        }
    )
    
    if response.status_code == 200:
        print("✅ SMTP configured successfully for your user!")
        print("\n📨 You can now send test emails from the frontend!")
    else:
        print("❌ Configuration failed:")
        print(response.text)

if __name__ == "__main__":
    configure_smtp()
