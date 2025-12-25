# Setting Up Dynamic Webhook Events

## Current Status
✅ Sent emails are showing dynamically
❌ Replies, bounces, opens, spam reports need webhook setup

## Setup Steps

### Step 1: Start ngrok (Required!)

Open a **new PowerShell terminal** and run:

```powershell
ngrok http 8000
```

**Important**: Keep this terminal open! ngrok must run continuously.

You'll see output like:
```
Forwarding  https://abc-def-ghi.ngrok-free.app -> http://localhost:8000
```

**Copy the HTTPS URL** (something like `https://abc-def-ghi.ngrok-free.app`)

### Step 2: Update Backend Configuration

Replace the ngrok URL in these files with YOUR new URL:

1. **frontend/src/pages/WebhooksDebug.jsx** (lines 90-99)
2. **backend/app/routes/webhooks.py** (if hardcoded anywhere)

Or better yet, use the URL you get from ngrok directly in SendGrid.

### Step 3: Configure SendGrid Webhooks

1. Go to: **https://app.sendgrid.com/settings/mail_settings**

2. Scroll down to **"Event Webhook"**

3. Click **"Settings"** button

4. Enter your webhook URL:
   ```
   https://YOUR-NGROK-URL.ngrok-free.app/api/webhooks/sendgrid
   ```
   Example: `https://abc-def-ghi.ngrok-free.app/api/webhooks/sendgrid`

5. **Enable these event types:**
   - ☑️ Delivered
   - ☑️ Opened
   - ☑️ Clicked  
   - ☑️ Bounced
   - ☑️ Dropped
   - ☑️ Spam Report
   - ☑️ Unsubscribe

6. **IMPORTANT**: Set **"Event Webhook Status"** to **"Enabled"**

7. Click **"Test Your Integration"** - should show "200 OK"

8. Click **"Save"**

### Step 4: Test the Setup

After configuration, send a test email:

```powershell
docker-compose exec backend python send_test_to_me.py
```

Then wait 1-2 minutes and check your webhook page - you should see:
- 📤 Sent (immediate)
- ✅ Delivered (after 10-30 seconds)
- 👁️ Opened (if you open the email)
- 🖱️ Clicked (if you click a link)

### Step 5: Verify Events Are Coming In

Check database for new events:

```powershell
docker-compose exec postgres psql -U postgres -d leadgen_db -c "SELECT event_type, parsed_to, created_at FROM inbound_events ORDER BY created_at DESC LIMIT 5;"
```

You should see recent events with current timestamps.

## Troubleshooting

### Problem: No events showing up

**Check 1: Is ngrok running?**
```powershell
curl https://YOUR-NGROK-URL.ngrok-free.app/health
```
Should return: `{"status":"healthy"}`

**Check 2: Is SendGrid webhook enabled?**
- Go to SendGrid settings
- Event Webhook should show "Enabled" with green checkmark

**Check 3: Check backend logs**
```powershell
docker-compose logs -f backend | Select-String "webhook"
```

### Problem: ngrok URL keeps changing

ngrok free tier gives you a new URL each time you restart. Solutions:

**Option A: Use ngrok paid plan** ($8/month)
- Get a permanent URL
- No need to update configuration

**Option B: Use environment variable**
Add to `.env`:
```
WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok-free.app
```

Update code to read from environment instead of hardcoding.

## What Each Event Type Means

| Event | When It Happens | What It Means |
|-------|----------------|---------------|
| **Sent** | Email leaves your system | You successfully sent it |
| **Delivered** | Email reaches recipient's server | Confirmed delivery |
| **Opened** | Recipient opens the email | Engagement tracking |
| **Clicked** | Recipient clicks a link | High engagement |
| **Bounced** | Email rejected by server | Bad email address |
| **Dropped** | SendGrid blocks sending | Invalid/spam email |
| **Spam Report** | Recipient marks as spam | Remove from list |
| **Unsubscribe** | Recipient unsubscribes | Remove from list |

## Important Notes

1. **Opens/Clicks require HTML emails** - Plain text emails can't track these
2. **Events have ~30 second delay** - Not instant, be patient
3. **Gmail blocks tracking pixels** - Opens may not track for Gmail users
4. **Keep ngrok running** - If it stops, webhooks fail until you restart and reconfigure

## Quick Start (TL;DR)

```powershell
# Terminal 1: Start ngrok
ngrok http 8000

# Copy the HTTPS URL, then go to:
# https://app.sendgrid.com/settings/mail_settings
# Configure Event Webhook with your ngrok URL + /api/webhooks/sendgrid
# Enable all event types, Save

# Test it
docker-compose exec backend python send_test_to_me.py

# Wait 1 minute, then refresh your Webhooks page
# You should see: Sent → Delivered → (Opened if you open it)
```

That's it! 🚀
