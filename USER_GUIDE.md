# AI Lead Generation & Outreach SaaS - Complete User Guide

## 🚀 Quick Start

### Starting the Application

```powershell
cd "d:\lead gen"
docker-compose up -d
```

**Access the app:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs

---

## 📋 Table of Contents

1. [User Management](#1-user-management)
2. [Lead Management](#2-lead-management)
3. [AI Email Generation](#3-ai-email-generation)
4. [Email Campaigns](#4-email-campaigns)
5. [Email Sequences](#5-email-sequences)
6. [Metrics & Analytics](#6-metrics--analytics)
7. [Settings](#7-settings)
8. [Advanced Features](#8-advanced-features)

---

## 1. User Management

### Register New Account
1. Go to http://localhost:5173
2. Click **"Sign Up"**
3. Enter email and password
4. Click **"Create Account"**

### Login
1. Enter your email: `test@example.com`
2. Enter password: `testpass123`
3. Click **"Login"**

**Current Test Account:**
- Email: `test@example.com`
- Password: `testpass123`

---

## 2. Lead Management

### View All Leads
1. Navigate to **"Leads"** page
2. View list of all leads with:
   - Name, Email, Company
   - Title, Industry
   - Status (Active/Bounced/Unsubscribed)
   - Tags

### Create Single Lead
1. Click **"+ New Lead"** button
2. Fill in details:
   - **First Name**: John
   - **Last Name**: Doe
   - **Email**: john.doe@company.com (required)
   - **Company**: TechCorp Inc
   - **Title**: Marketing Director
   - **Industry**: Technology
   - **Phone**: +1-555-0123
3. Click **"Create Lead"**

### Import Leads from CSV
1. Click **"Import CSV"** button
2. Prepare CSV file with columns:
   ```
   first_name,last_name,email,company,title,industry,phone
   John,Doe,john@example.com,TechCorp,CEO,Technology,555-0123
   Jane,Smith,jane@example.com,MarketCo,CMO,Marketing,555-0124
   ```
3. Upload the CSV file
4. Click **"Import"**
5. System will:
   - Validate emails
   - Skip duplicates
   - Import valid leads

**Sample CSV:** Use `sample_leads.csv` in project root

### Enrich Lead Data (AI)
1. Click on a lead row
2. Click **"Enrich"** button (✨ icon)
3. System uses AI to find:
   - Company information
   - Industry details
   - Social media profiles
   - Additional contact info

### Edit Lead
1. Click lead row
2. Click **"Edit"** button
3. Update information
4. Click **"Save"**

### Delete Lead
1. Click lead row
2. Click **"Delete"** button
3. Confirm deletion

### Tag Leads
1. Select one or more leads (checkbox)
2. Click **"Add Tag"**
3. Enter tag name: `Hot Lead`, `Decision Maker`, `Follow Up`
4. Apply to selected leads
5. Filter leads by tags later

---

## 3. AI Email Generation

### Generate Personalized Email
1. Go to **Leads** page
2. Click on a lead
3. Click **"Send Email"** button
4. In Email Composer:

   **Configure Email:**
   - **Tone**: Choose from
     - Professional (default)
     - Friendly
     - Formal
     - Casual
   - **Goal**: Select objective
     - Schedule a meeting
     - Share product info
     - Follow up
     - Request demo
   - **Product Description**: Describe your offering
     - Example: "AI-powered marketing automation platform"

5. Click **"✨ Generate Email with AI"**
6. Wait 2-3 seconds for AI to generate

**AI generates:**
- Personalized subject line
- Customized email body using:
  - Lead's name
  - Company name
  - Industry context
  - Your product description
  - Selected tone and goal

### Review Generated Email
- **Subject**: Preview and edit if needed
- **Body**: Review personalized content
- Edit directly in text area if changes needed

### Send Test Email
1. After generating email
2. Click **"Send Test"** button
3. Email sent to lead's email address
4. Success message appears
5. Check recipient's inbox (may be in spam initially)

### Save as Draft
1. Click **"Save Draft"** button
2. Email saved for later use
3. Can be accessed from campaign editor

---

## 4. Email Campaigns

### Create Campaign
1. Navigate to **"Campaigns"** page
2. Click **"+ New Campaign"**
3. Fill in details:
   - **Name**: "Product Launch Q1 2025"
   - **Description**: Campaign objectives
4. Click **"Create"**

### View Campaigns
- See all campaigns with:
  - Name and description
  - Number of enrolled leads
  - Emails sent/delivered/opened
  - Replies received
  - Status (Active/Paused/Completed)

### Add Leads to Campaign
1. Go to **Leads** page
2. Select leads (checkboxes)
3. Click **"Add to Campaign"** button
4. Choose campaign from dropdown
5. Click **"Add"**
6. System automatically:
   - Queues emails for sequence
   - Tracks engagement
   - Manages follow-ups

### Pause/Resume Campaign
1. Open campaign details
2. Click **"Pause"** to stop sending
3. Click **"Resume"** to continue
4. Emails in queue will wait

### View Campaign Stats
- **Overview:**
  - Total leads enrolled
  - Emails sent
  - Delivery rate
  - Open rate
  - Reply rate
- **Lead Status:**
  - Active
  - Replied (stops sequence)
  - Bounced
  - Unsubscribed

---

## 5. Email Sequences

### Create Email Sequence
1. Open a campaign
2. Navigate to **"Sequence Steps"** tab
3. Click **"+ Add Step"**

**Configure Each Step:**

**Step 1 - Initial Contact:**
- **Step Number**: 1
- **Delay**: 0 days (sends immediately)
- **Subject Template**: "Quick thought on {goal}"
- **Body Template**: 
  ```
  Hi {first_name},
  
  I was looking into {company} and noticed...
  
  [Your pitch]
  
  Would you be open to a brief chat?
  
  Best,
  {sender_name}
  ```
- **Stop on Reply**: ✓ Yes (stops if lead replies)

**Step 2 - Follow-Up:**
- **Step Number**: 2
- **Delay**: 3 days
- **Subject Template**: "Following up - {company}"
- **Body Template**:
  ```
  Hi {first_name},
  
  I wanted to follow up on my previous email...
  
  [Value proposition]
  
  Let me know if you'd like to discuss.
  
  Best regards,
  {sender_name}
  ```
- **Stop on Reply**: ✓ Yes

**Step 3 - Final Touch:**
- **Step Number**: 3
- **Delay**: 7 days
- **Subject**: "Last follow-up"
- **Body**: Final attempt message
- **Stop on Reply**: ✓ Yes

### Available Variables
Use these in templates:
- `{first_name}` - Lead's first name
- `{last_name}` - Lead's last name
- `{email}` - Lead's email
- `{company}` - Company name
- `{title}` - Job title
- `{industry}` - Industry
- `{sender_name}` - Your name (from email config)

### How Sequences Work
1. Lead enrolled in campaign
2. Step 1 sends immediately
3. System waits for delay period
4. If no reply, sends next step
5. If lead replies, sequence stops
6. System tracks all interactions

### Edit Sequence Step
1. Click on existing step
2. Update content
3. Save changes
4. Affects future sends only

### Delete Sequence Step
1. Click step
2. Click **"Delete"**
3. Confirm removal

---

## 6. Metrics & Analytics

### Access Dashboard
1. Navigate to **"Metrics"** page
2. View comprehensive analytics

### Overview Metrics
- **Total Emails Sent**: All-time count
- **Delivered**: Successfully delivered
- **Opened**: Email opens tracked
- **Clicked**: Link clicks (if tracking enabled)
- **Replied**: Responses received
- **Bounced**: Failed deliveries
- **Unsubscribed**: Opt-outs

### Email Performance Charts
- **Timeline**: Daily/weekly/monthly trends
- **Delivery Rate**: Success percentage
- **Engagement Rate**: Opens + clicks
- **Response Rate**: Reply percentage

### Campaign Analytics
- Compare performance across campaigns
- Identify best-performing sequences
- Track ROI per campaign

### Lead Engagement
- Most engaged leads
- Best time to send
- Subject line performance

### Date Range Filter
- Select time period:
  - Last 7 days
  - Last 30 days
  - Last 90 days
  - Custom range

---

## 7. Settings

### Email Provider Configuration

**Already Configured:**
- Provider: Gmail SMTP
- From Email: omkargotawade05@gmail.com
- From Name: Lead gen ai

**To Update:**
1. Go to **"Settings"** → **"Email Provider"**
2. Update credentials if needed
3. Click **"Save"**
4. Click **"Test Connection"**

**For New Users:**
1. Go to **Settings** → **Email Provider**
2. Choose provider:
   - **Gmail/SMTP** (recommended)
   - **SendGrid**

**Gmail Setup:**
1. Enable 2FA: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Enter in settings:
   - Email: your.email@gmail.com
   - App Password: (16 characters)
   - From Name: Your Name

### Webhook Configuration
1. Go to **Settings** → **Webhooks**
2. Configure for:
   - SendGrid events (bounces, opens, clicks)
   - Gmail inbox monitoring
3. Add webhook URLs:
   - `http://your-domain.com/api/webhooks/sendgrid`
   - `http://your-domain.com/api/webhooks/gmail`

### Deliverability Settings
1. Navigate to **"Deliverability"** page
2. View best practices:
   - Email warmup tips
   - Spam score checker
   - SPF/DKIM setup guide
   - Content recommendations

---

## 8. Advanced Features

### Lead Tagging & Filtering
**Use Cases:**
- Tag hot leads: `Hot Lead`, `Ready to Buy`
- Tag by source: `Webinar`, `LinkedIn`, `Referral`
- Tag by stage: `Contacted`, `Replied`, `Meeting Scheduled`

**Filter by Tag:**
1. Go to Leads page
2. Click **"Filter"** dropdown
3. Select tag(s)
4. View filtered results

### Bounce Management
**System automatically:**
- Detects bounced emails
- Marks leads as `bounced`
- Stops sending to bounced addresses
- Categorizes bounce types:
  - Hard bounce (permanent)
  - Soft bounce (temporary)

**Manual Review:**
1. Go to Leads
2. Filter by status: `Bounced`
3. Review and clean list
4. Remove invalid emails

### Unsubscribe Handling
**Automated:**
- Unsubscribe links in emails
- One-click opt-out
- System marks lead as `unsubscribed`
- No more emails sent

**Manual Unsubscribe:**
1. Open lead details
2. Mark as "Unsubscribed"
3. Lead excluded from campaigns

### Reply Detection
**Automatic:**
- System monitors for replies
- Stops sequence on reply
- Marks lead status as `replied`
- Records reply timestamp

**View Replies:**
1. Go to Leads
2. Filter by status: `Replied`
3. See who responded
4. Follow up manually

### Quota Management
**Daily Limits:**
- Prevents spam complaints
- Protects sender reputation
- Default: 500 emails/day

**View Usage:**
1. Dashboard shows quota
2. Emails sent today
3. Remaining quota
4. Resets daily

### Rate Limiting
**Protection:**
- API rate limits: 60 req/min
- Prevents abuse
- Ensures fair usage

---

## 🎯 Complete Workflow Example

### Scenario: Launch Product to 100 Leads

**Day 1: Setup**

1. **Import Leads:**
   - Prepare CSV with 100 leads
   - Import via CSV upload
   - Verify import success

2. **Enrich Leads:**
   - Select all leads
   - Click "Enrich" 
   - Wait for AI to complete

3. **Create Campaign:**
   - Name: "Product Launch - AI Tool"
   - Description: "Introduce new AI marketing tool"

4. **Build Sequence:**
   - Step 1: Initial intro (0 days)
   - Step 2: Value prop follow-up (3 days)
   - Step 3: Case study share (7 days)
   - Step 4: Final CTA (10 days)

**Day 2: Launch**

5. **Generate Email Template:**
   - Use AI to generate email
   - Tone: Professional
   - Goal: Schedule demo
   - Product: "AI Marketing Automation"

6. **Add to Sequence:**
   - Copy generated email to Step 1
   - Customize with variables
   - Save template

7. **Enroll Leads:**
   - Select all 100 leads
   - Add to campaign
   - Confirm enrollment
   - System starts sending

**Ongoing: Monitor**

8. **Track Performance:**
   - Check Metrics dashboard daily
   - Monitor open rates
   - View replies
   - Track conversions

9. **Handle Responses:**
   - Check replied leads
   - Follow up manually
   - Move to sales pipeline

10. **Optimize:**
    - Test subject lines
    - Adjust timing
    - Refine messaging

---

## 🔧 Troubleshooting

### Emails Not Sending
1. Check Celery worker: `docker ps`
2. View logs: `docker logs leadgen_celery_worker`
3. Verify SMTP config in Settings
4. Test with single email first

### Emails in Spam
- Ask recipients to mark "Not Spam"
- Avoid spam trigger words (FREE, URGENT)
- Personalize content
- Keep sending volume gradual
- Add SPF/DKIM records

### System Not Starting
```powershell
docker-compose down
docker-compose up -d
docker ps  # Check all containers running
```

### Database Issues
```powershell
# Reset database
docker-compose down -v
docker-compose up -d
# Re-run migrations in backend container
```

---

## 📊 Best Practices

### Email Sending
- **Start slow**: 20-50 emails/day initially
- **Warm up**: Gradually increase volume
- **Personalize**: Use AI generation for each lead
- **Test**: Send to yourself first
- **Monitor**: Check bounce/spam rates

### Lead Management
- **Clean data**: Remove invalid emails
- **Segment**: Use tags effectively
- **Enrich**: Update with latest info
- **Track**: Monitor engagement
- **Remove**: Delete bounced/unsubscribed

### Campaign Strategy
- **Clear goal**: Define objective per campaign
- **Right timing**: Send during business hours
- **Follow-up**: 3-4 touches optimal
- **Stop on reply**: Don't over-send
- **A/B test**: Try different approaches

### Compliance
- **Include unsubscribe**: Required by law
- **Honor opt-outs**: Immediately
- **No purchased lists**: Use opt-in leads only
- **CAN-SPAM**: Follow regulations
- **GDPR**: If EU contacts

---

## 🎓 Quick Reference

### Common Commands

**Start System:**
```powershell
cd "d:\lead gen"
docker-compose up -d
```

**Stop System:**
```powershell
docker-compose down
```

**View Logs:**
```powershell
docker logs leadgen_backend --tail 50
docker logs leadgen_celery_worker --tail 50
```

**Check Status:**
```powershell
docker ps
```

**Rebuild Frontend:**
```powershell
docker-compose build frontend
docker-compose up -d frontend
```

---

## 📱 Keyboard Shortcuts

- **Leads Page:**
  - `N` - New lead
  - `I` - Import CSV
  - `F` - Filter leads

- **Email Composer:**
  - `Ctrl+Enter` - Generate email
  - `Ctrl+S` - Save draft

- **Navigation:**
  - `1` - Dashboard
  - `2` - Leads
  - `3` - Campaigns
  - `4` - Metrics

---

## 🚀 Next Steps

1. **Import your real leads** from CSV
2. **Create first campaign** with sequence
3. **Generate AI emails** for personalization
4. **Start with 10-20 test sends** 
5. **Monitor results** in Metrics
6. **Scale up gradually** to full list
7. **Track conversions** and optimize

---

## 💡 Pro Tips

1. **Personalization is key**: Use AI generation for each lead
2. **Timing matters**: Send during business hours (9am-5pm)
3. **Subject lines**: Keep under 50 characters
4. **Follow-up**: 3 touches gets 80% more responses
5. **Stop on reply**: Don't annoy engaged leads
6. **Clean lists**: Remove bounces weekly
7. **Test everything**: Send to yourself first
8. **Monitor reputation**: Check bounce/spam rates
9. **Gradual ramp**: Increase volume slowly
10. **Track what works**: Use metrics to optimize

---

## 📚 Additional Resources

- API Documentation: http://localhost:8000/docs
- Swagger UI: http://localhost:8000/redoc
- Health Check: `python health_check.py`
- Test Suite: `python test_gemini_integration.py`

---

**Support:** Check logs, review error messages, verify configuration
**Version:** 1.0.0 (Week 3 Complete)
**Last Updated:** December 2025
