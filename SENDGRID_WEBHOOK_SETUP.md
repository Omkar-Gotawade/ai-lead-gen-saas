# SendGrid Webhook Setup Guide

## Why You're Seeing "No Events Found"

Your webhook page shows no events because **SendGrid hasn't been configured to send events to your app yet**.

### What's Working:
- ✅ Your backend webhook endpoint exists: `POST /api/webhooks/sendgrid`
- ✅ Your database table `inbound_events` exists
- ✅ You can send emails via SendGrid

### What's Missing:
- ❌ SendGrid doesn't know where to send event notifications
- ❌ No webhook URL configured in SendGrid dashboard
- ❌ No events (delivered, bounced, spam, opened, clicked, replied) are being received

---

## Option 1: Configure SendGrid Webhooks (Production)

### Prerequisites:
- SendGrid account (free or paid)
- Public URL for your app (localhost won't work)
- Use ngrok or deploy to a server

### Steps:

#### 1. Expose Your Local App Publicly (Using ngrok)

```powershell
# Install ngrok: https://ngrok.com/download

# Start ngrok to expose port 8000
ngrok http 8000

# You'll get a URL like: https://abc123.ngrok.io
```

#### 2. Configure SendGrid Webhook

1. Go to **SendGrid Dashboard**: https://app.sendgrid.com
2. Navigate to **Settings** → **Mail Settings** → **Event Webhook**
3. Click **Enable Event Webhook**
4. **HTTP Post URL**: `https://YOUR-NGROK-URL.ngrok.io/api/webhooks/sendgrid`
   - Example: `https://abc123.ngrok.io/api/webhooks/sendgrid`
5. **Select Actions to Post**:
   - ☑️ Delivered
   - ☑️ Bounced  
   - ☑️ Spam Report
   - ☑️ Opened (requires open tracking enabled)
   - ☑️ Clicked (requires click tracking enabled)
6. **OAuth** (optional): Leave blank for now
7. Click **Save**

#### 3. Test the Webhook

```powershell
# Send a test email from your app
# Then check SendGrid's Event Webhook page for delivery attempts
```

#### 4. Verify Events Are Received

```powershell
# Check database for events
docker exec -it leadgen_postgres psql -U postgres -d leadgen_db -c "SELECT event_type, COUNT(*) FROM inbound_events GROUP BY event_type;"

# Check backend logs
docker-compose logs backend --tail 50 | Select-String "webhook"
```

---

## Option 2: Generate Test Data (Development)

If you don't want to set up ngrok/webhooks yet, you can populate the page with fake test data:

### Method A: API Endpoint (Easiest)

```powershell
# The backend has a built-in endpoint to create sample events
# Run this from PowerShell:

$headers = @{
    "Authorization" = "Bearer YOUR_JWT_TOKEN"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/webhooks/sample-events" -Method POST -Headers $headers
```

### Method B: Direct Database Insert

```powershell
# Insert test webhook events directly
docker exec -it leadgen_postgres psql -U postgres -d leadgen_db -c "
INSERT INTO inbound_events (event_type, provider, parsed_from, parsed_to, parsed_subject, raw_payload, created_at)
VALUES 
  ('delivered', 'sendgrid', 'you@example.com', 'lead@company.com', 'Test Email 1', '{}', NOW()),
  ('delivered', 'sendgrid', 'you@example.com', 'lead2@company.com', 'Test Email 2', '{}', NOW() - INTERVAL '1 hour'),
  ('bounce', 'sendgrid', 'you@example.com', 'bounced@invalid.com', 'Bounced Email', '{\"reason\":\"invalid\"}', NOW() - INTERVAL '2 hours'),
  ('spam', 'sendgrid', 'you@example.com', 'spam@report.com', 'Spam Report', '{}', NOW() - INTERVAL '3 hours'),
  ('open', 'sendgrid', 'you@example.com', 'lead@company.com', 'Test Email 1', '{}', NOW() - INTERVAL '30 minutes'),
  ('reply', 'gmail', 'lead@company.com', 'you@example.com', 'Re: Test Email 1', '{\"body\":\"Thanks for reaching out\"}', NOW() - INTERVAL '15 minutes');
"
```

### Method C: Python Script

Create `scripts/generate_test_events.py`:

```python
import requests
import sys

# Get JWT token from login
login_response = requests.post('http://localhost:8000/auth/login', json={
    'email': 'test@example.com',
    'password': 'password123'
})

if login_response.status_code != 200:
    print("Login failed!")
    sys.exit(1)

token = login_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Generate sample events
response = requests.post(
    'http://localhost:8000/api/webhooks/sample-events',
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Created {data['created']} sample webhook events!")
    print(f"Event types: {', '.join(data['events_created'])}")
else:
    print(f"❌ Failed: {response.text}")
```

Run it:
```powershell
python scripts/generate_test_events.py
```

---

## Option 3: Webhook Simulation Tool

I can create a webhook simulator that mimics SendGrid sending events:

### Create: `scripts/simulate_sendgrid_webhook.py`

```python
"""
Simulate SendGrid webhook events for testing
"""
import requests
import json
from datetime import datetime

BACKEND_URL = "http://localhost:8000"
WEBHOOK_ENDPOINT = f"{BACKEND_URL}/api/webhooks/sendgrid"

# Sample SendGrid webhook payloads
SAMPLE_EVENTS = [
    {
        "email": "john@example.com",
        "event": "delivered",
        "smtp-id": "<delivered@example.com>",
        "timestamp": int(datetime.now().timestamp()),
        "sg_event_id": "delivered-123",
        "sg_message_id": "msg-123.filter0123.12345.12345.0",
    },
    {
        "email": "jane@example.com",
        "event": "bounce",
        "smtp-id": "<bounced@example.com>",
        "timestamp": int(datetime.now().timestamp()),
        "sg_event_id": "bounce-456",
        "reason": "550 5.1.1 User unknown",
        "type": "bounce",
    },
    {
        "email": "spam@example.com",
        "event": "spamreport",
        "smtp-id": "<spam@example.com>",
        "timestamp": int(datetime.now().timestamp()),
        "sg_event_id": "spam-789",
    },
    {
        "email": "opener@example.com",
        "event": "open",
        "smtp-id": "<opened@example.com>",
        "timestamp": int(datetime.now().timestamp()),
        "sg_event_id": "open-321",
        "useragent": "Mozilla/5.0",
    },
]

def simulate_webhooks():
    """Send sample webhook events to your backend"""
    print("🔄 Simulating SendGrid webhook events...")
    print(f"📍 Target: {WEBHOOK_ENDPOINT}\n")
    
    for event in SAMPLE_EVENTS:
        try:
            response = requests.post(
                WEBHOOK_ENDPOINT,
                json=[event],  # SendGrid sends array of events
                headers={"Content-Type": "application/json"}
            )
            
            event_type = event["event"]
            email = event["email"]
            
            if response.status_code == 200:
                print(f"✅ {event_type.upper()}: {email}")
            else:
                print(f"❌ {event_type.upper()}: {email} - Failed ({response.status_code})")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error sending webhook: {e}")
    
    print(f"\n✅ Webhook simulation complete!")
    print(f"🌐 Check: http://localhost:5173/webhooks")

if __name__ == "__main__":
    simulate_webhooks()
```

Run it:
```powershell
python scripts/simulate_sendgrid_webhook.py
```

---

## Troubleshooting

### 1. Webhook Not Receiving Events

**Check if endpoint is accessible:**
```powershell
# From your machine
Invoke-RestMethod -Uri "http://localhost:8000/api/webhooks/sendgrid" -Method POST -Body "[]" -ContentType "application/json"

# Should return: {"received": 0}
```

**Check backend logs:**
```powershell
docker-compose logs backend -f | Select-String "webhook"
```

### 2. SendGrid Not Sending Events

**Reasons:**
- Webhook URL not reachable (localhost, firewall)
- Wrong URL configured
- Webhook disabled in SendGrid
- Event types not selected

**Solution:**
- Use ngrok for local testing
- Deploy to public server
- Check SendGrid Event Webhook stats

### 3. Events Not Showing in UI

**Check database:**
```powershell
docker exec -it leadgen_postgres psql -U postgres -d leadgen_db -c "SELECT * FROM inbound_events ORDER BY created_at DESC LIMIT 5;"
```

**Check API directly:**
```powershell
# Get JWT token first (login)
$token = "YOUR_JWT_TOKEN_HERE"

$headers = @{
    "Authorization" = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/webhooks/events?limit=10" -Headers $headers
```

**Refresh frontend:**
- Clear browser cache
- Hard reload (Ctrl+Shift+R)
- Check browser console for errors

---

## Quick Start (Recommended for Testing)

**Fastest way to see data in your webhook page:**

```powershell
# 1. Insert test data directly
docker exec -it leadgen_postgres psql -U postgres -d leadgen_db -c "
INSERT INTO inbound_events (event_type, provider, parsed_from, parsed_to, parsed_subject, raw_payload, created_at)
SELECT 
  (ARRAY['delivered', 'bounce', 'spam', 'open', 'reply'])[floor(random() * 5 + 1)],
  'sendgrid',
  'you@example.com',
  'lead' || generate_series || '@company.com',
  'Test Email ' || generate_series,
  '{}',
  NOW() - (random() * INTERVAL '7 days')
FROM generate_series(1, 20);
"

# 2. Refresh the webhook page in browser
# You should now see 20 random events!
```

---

## Production Checklist

Before going live, ensure:

- ☐ Deployed to public server (not localhost)
- ☐ HTTPS enabled (SendGrid requires HTTPS for webhooks)
- ☐ SendGrid webhook URL configured correctly
- ☐ All event types selected (delivered, bounced, spam, opened, clicked)
- ☐ Webhook signature verification enabled (set SENDGRID_SIGNING_KEY in .env)
- ☐ Test email sent and events received
- ☐ Database has events after sending test
- ☐ UI shows events correctly

---

## Summary

Your webhook page is **working correctly** - it's just waiting for events!

**Choose one:**

1. **Quick Testing**: Insert fake data (5 minutes)
   ```powershell
   docker exec -it leadgen_postgres psql -U postgres -d leadgen_db -c "INSERT INTO inbound_events ..."
   ```

2. **Real Webhooks**: Set up ngrok + SendGrid (30 minutes)
   - Expose your app with ngrok
   - Configure SendGrid webhook URL
   - Send test emails

3. **Production**: Deploy to server with HTTPS (2+ hours)
   - Deploy app to Heroku/AWS/DigitalOcean
   - Configure SendGrid webhook with public URL
   - Monitor real email events

**Recommendation**: Start with option 1 (fake data) to verify the UI works, then move to option 2 (ngrok) for real testing.
