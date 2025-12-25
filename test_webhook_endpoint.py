"""Test SendGrid webhook reception."""
import requests
import json
from datetime import datetime

# Your ngrok URL
WEBHOOK_URL = "https://disgustfully-mowburnt-pearlie.ngrok-free.dev/api/webhooks/sendgrid"

# Sample SendGrid webhook event (delivered)
sample_event = {
    "email": "test@example.com",
    "timestamp": int(datetime.now().timestamp()),
    "event": "delivered",
    "smtp-id": "<test@sendgrid.net>",
    "sg_event_id": "test-event-123",
    "sg_message_id": "test-msg-456",
    "response": "250 OK",
    "attempt": "1"
}

print("🧪 Testing SendGrid webhook endpoint...")
print(f"URL: {WEBHOOK_URL}")
print(f"Event: {json.dumps(sample_event, indent=2)}")

try:
    # SendGrid sends events as JSON array
    response = requests.post(
        WEBHOOK_URL,
        json=[sample_event],
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n✅ Response Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n🎉 Webhook endpoint is working!")
        print("Now configure it in SendGrid dashboard")
    else:
        print("\n❌ Webhook endpoint returned error")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure:")
    print("1. Backend is running (docker-compose up)")
    print("2. ngrok is running and URL is correct")
