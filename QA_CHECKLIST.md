# Alpha Release QA Checklist

**Purpose**: Ensure product stability and safety before controlled alpha launch.

**Test Environment**: Local development setup (Docker containers running)

**Test User**: Create fresh account for each test run to simulate new user experience.

---

## ✅ Pre-Launch Smoke Tests

### 1. Authentication & Account Management

- [ ] **Sign Up with Valid Email**
  - Go to http://localhost:3000/signup
  - Enter email: test-alpha-{timestamp}@example.com
  - Enter password (min 8 chars)
  - **Expected**: Account created, redirected to /leads
  - **Pass/Fail**: ___________

- [ ] **Sign Up with Duplicate Email**
  - Try to sign up with same email again
  - **Expected**: Error message "Email already registered"
  - **Pass/Fail**: ___________

- [ ] **Login with Correct Credentials**
  - Go to /login
  - Enter correct email/password
  - **Expected**: Successfully logged in, redirected to /leads
  - **Pass/Fail**: ___________

- [ ] **Login with Wrong Password**
  - Enter correct email, wrong password
  - **Expected**: Error "Invalid credentials"
  - **Pass/Fail**: ___________

- [ ] **Logout and Re-login**
  - Click logout button
  - **Expected**: Redirected to /login
  - Log in again - should work
  - **Pass/Fail**: ___________

---

### 2. Email Provider Setup

- [ ] **Add SendGrid API Key (Valid)**
  - Go to Settings → Email Provider
  - Select "SendGrid"
  - Enter valid API key
  - Click "Test Connection"
  - **Expected**: ✅ "Connection successful"
  - **Pass/Fail**: ___________

- [ ] **Add Invalid API Key**
  - Enter invalid/fake API key
  - Click "Test Connection"
  - **Expected**: ❌ Error message displayed
  - Should NOT crash page
  - **Pass/Fail**: ___________

- [ ] **Update Existing Provider**
  - Change API key
  - Save settings
  - **Expected**: Settings saved, confirmation shown
  - **Pass/Fail**: ___________

- [ ] **Delete Email Provider**
  - Remove provider configuration
  - Try to create campaign
  - **Expected**: Warning "Email provider required"
  - **Pass/Fail**: ___________

---

### 3. Lead Management

- [ ] **Import CSV with Valid Leads**
  - Go to Leads page
  - Click "Import CSV"
  - Upload sample_leads.csv (10 leads)
  - **Expected**: "10 leads imported successfully"
  - Leads appear in table
  - **Pass/Fail**: ___________

- [ ] **Import CSV with Invalid Emails**
  - Create CSV with invalid emails (missing @, no domain, etc.)
  - Import it
  - **Expected**: Error report showing invalid rows
  - Valid leads still imported
  - **Pass/Fail**: ___________

- [ ] **Add Single Lead Manually**
  - Click "Add Lead"
  - Fill form: name, email, company
  - Click "Save"
  - **Expected**: Lead added to list
  - **Pass/Fail**: ___________

- [ ] **Edit Existing Lead**
  - Click edit icon on a lead
  - Change company name
  - Save
  - **Expected**: Changes saved, table updates
  - **Pass/Fail**: ___________

- [ ] **Delete Lead**
  - Click delete icon
  - Confirm deletion
  - **Expected**: Lead removed from list
  - **Pass/Fail**: ___________

- [ ] **Search/Filter Leads**
  - Use search box to filter by name/email
  - **Expected**: Table filters correctly
  - **Pass/Fail**: ___________

---

### 4. Campaign Creation

- [ ] **Block Campaign Creation Without Provider**
  - Remove email provider in settings
  - Go to Campaigns
  - Try to create campaign
  - **Expected**: ❌ "Email provider required" blocker
  - Cannot proceed
  - **Pass/Fail**: ___________

- [ ] **Create Campaign with Valid Settings**
  - Ensure provider connected
  - Click "Create Campaign"
  - Name: "Alpha Test Campaign"
  - Select 5-10 leads
  - **Expected**: Campaign created, redirected to editor
  - **Pass/Fail**: ___________

- [ ] **Generate AI Email WITH Research Notes**
  - Lead has research_notes populated
  - Click "Generate AI Email"
  - **Expected**: Email generated within 10 seconds
  - Subject and body populated
  - Personalization variables present
  - **Pass/Fail**: ___________

- [ ] **Generate AI Email WITHOUT Research Notes**
  - Lead has no research_notes
  - Click "Generate AI Email"
  - **Expected**: ⚠️ Warning shown "No research notes - quality may be lower"
  - Email still generates (fallback template OK)
  - **Pass/Fail**: ___________

- [ ] **Edit Generated Email**
  - Modify AI-generated email body
  - Change subject line
  - **Expected**: Changes saved in editor
  - **Pass/Fail**: ___________

- [ ] **Save Draft Campaign**
  - Click "Save Draft"
  - Navigate away and back
  - **Expected**: Draft saved, changes persisted
  - **Pass/Fail**: ___________

- [ ] **Activate Campaign**
  - Click "Activate Campaign"
  - **Expected**: Confirmation dialog appears
  - Shows lead count and daily limit warning
  - **Pass/Fail**: ___________

---

### 5. Campaign Sending

- [ ] **Send Test Email to Single Lead**
  - In campaign editor, click "Send Test"
  - Select one lead
  - **Expected**: Email sent successfully
  - Check provider dashboard to verify
  - **Pass/Fail**: ___________

- [ ] **Activate Campaign with 10 Leads**
  - Campaign with 10 leads
  - Click "Activate"
  - Confirm
  - **Expected**: Campaign status → "Active"
  - Sending begins
  - **Pass/Fail**: ___________

- [ ] **Monitor Sending Progress**
  - Stay on Campaigns page
  - Refresh to see progress
  - **Expected**: Sent count increases
  - Status updates visible
  - **Pass/Fail**: ___________

- [ ] **Check Daily Limit Warnings**
  - If on Day 1 (limit 10), try to send 15 emails
  - **Expected**: ⚠️ Warning at 8 emails (80%)
  - ⚠️ Critical alert at 11 emails (exceeded)
  - **Pass/Fail**: ___________

- [ ] **Verify Emails Sent via Provider Dashboard**
  - Log into SendGrid dashboard
  - Check activity feed
  - **Expected**: Emails appear in provider logs
  - **Pass/Fail**: ___________

- [ ] **Check sending_logs Table**
  - Run: `docker exec leadgen_postgres psql -U postgres -d leadgen_db -c "SELECT * FROM sending_logs LIMIT 10"`
  - **Expected**: Rows with status "SENT"
  - Timestamps within last 5 minutes
  - **Pass/Fail**: ___________

---

### 6. Deliverability Monitoring

- [ ] **Check Deliverability Score on Day 1**
  - Go to Deliverability page
  - **Expected**: Health score 70-85 (Day 1 of warmup)
  - Warmup progress shown: "Day 1/21"
  - Daily limit: 10 emails
  - **Pass/Fail**: ___________

- [ ] **View Warmup Progress**
  - Check warmup status card
  - **Expected**: Current day, total days, recommended limit
  - Progress bar shown
  - **Pass/Fail**: ___________

- [ ] **Run Safety Diagnostics**
  - Click "Run Safety Diagnostics"
  - **Expected**: Results shown within 5 seconds
  - Passed checks listed
  - Manual actions listed
  - **Pass/Fail**: ___________

- [ ] **Review Recommendations**
  - Check recommendations card
  - **Expected**: Actionable advice shown
  - Warnings displayed if applicable
  - **Pass/Fail**: ___________

- [ ] **Check Bounce Rate (with test data)**
  - Insert test bounce events (see scripts/insert_test_events.sql)
  - Refresh deliverability page
  - **Expected**: Bounce rate calculated correctly
  - Warning shown if rate > 5%
  - **Pass/Fail**: ___________

- [ ] **Check Spam Rate (with test data)**
  - Test spam events inserted
  - **Expected**: Spam rate shown
  - Critical alert if rate > 0.5%
  - **Pass/Fail**: ___________

---

### 7. Webhook Events

- [ ] **Configure SendGrid Webhook**
  - Follow SENDGRID_WEBHOOK_SETUP.md
  - Use ngrok to expose localhost
  - Add webhook URL to SendGrid
  - **Expected**: Webhook created successfully
  - **Pass/Fail**: ___________

- [ ] **Send Test Email**
  - Send campaign email
  - **Expected**: Email sent
  - **Pass/Fail**: ___________

- [ ] **Verify Delivery Event Appears**
  - Go to Webhooks page
  - Wait 30 seconds
  - **Expected**: Delivery event appears in table
  - Event type: "delivered"
  - **Pass/Fail**: ___________

- [ ] **Check Bounce Event Handling**
  - Send to invalid email
  - **Expected**: Bounce event captured
  - Appears in webhook events
  - **Pass/Fail**: ___________

- [ ] **Verify Spam Complaint Tracking**
  - (Simulate if possible)
  - **Expected**: Spam events tracked
  - Appears in webhook page
  - **Pass/Fail**: ___________

---

### 8. Error Handling

- [ ] **Submit Form with Missing Required Fields**
  - Leave campaign name empty
  - Try to save
  - **Expected**: ❌ Validation error "Campaign name required"
  - Form doesn't submit
  - **Pass/Fail**: ___________

- [ ] **Upload Invalid CSV Format**
  - Upload .txt file or malformed CSV
  - **Expected**: Error "Invalid file format"
  - Page doesn't crash
  - **Pass/Fail**: ___________

- [ ] **Try to Send Campaign at Daily Limit**
  - Reach daily limit (e.g., 10/10 on Day 1)
  - Try to activate new campaign
  - **Expected**: ⚠️ Warning shown (advisory mode)
  - Still allows activation with acknowledgment
  - **Pass/Fail**: ___________

- [ ] **Disconnect Internet During Operation**
  - Start AI email generation
  - Disconnect WiFi/Ethernet
  - **Expected**: Error message "Network error"
  - Doesn't crash
  - Retry button appears
  - **Pass/Fail**: ___________

- [ ] **Invalid API Response from Email Provider**
  - Use invalid API key mid-operation
  - **Expected**: Error message shown
  - User can fix in settings
  - **Pass/Fail**: ___________

---

### 9. Safety Features

- [ ] **Daily Send Limit Warning (80%)**
  - Send 8 of 10 allowed emails
  - **Expected**: ⚠️ "Approaching daily limit (8/10)"
  - **Pass/Fail**: ___________

- [ ] **Daily Limit Exceeded Warning (100%+)**
  - Send 11 of 10 allowed emails
  - **Expected**: 🚨 "Daily limit exceeded (11/10)"
  - Critical alert displayed
  - **Pass/Fail**: ___________

- [ ] **Warmup Guidance Shown to New Users**
  - New account (Day 1)
  - Go to Deliverability
  - **Expected**: "Day 1 of 21 warmup"
  - Guidance: "Send 10 emails today"
  - **Pass/Fail**: ___________

- [ ] **High Bounce Rate Triggers Warning**
  - Insert bounces to create 10% bounce rate
  - **Expected**: 🚨 "HIGH BOUNCE RATE: 10%"
  - Recommendation: "Stop sending immediately"
  - **Pass/Fail**: ___________

- [ ] **High Spam Rate Triggers Critical Alert**
  - Insert spam complaints to create 1% rate
  - **Expected**: 🚨 "CRITICAL: Spam rate 1%"
  - Urgent action recommended
  - **Pass/Fail**: ___________

- [ ] **Missing Email Provider Blocks Sending**
  - Delete email provider
  - Try to activate campaign
  - **Expected**: ❌ Hard blocker
  - "Configure email provider first"
  - **Pass/Fail**: ___________

---

## 🔄 Regression Tests

### Data Integrity

- [ ] **Campaign Leads Persisted Correctly**
  - Create campaign with leads
  - Restart backend: `docker-compose restart backend`
  - **Expected**: Campaign and leads still associated
  - **Pass/Fail**: ___________

- [ ] **Sending Logs Recorded Accurately**
  - Send 5 emails
  - Query database: `SELECT * FROM sending_logs`
  - **Expected**: 5 rows with correct status, timestamps
  - **Pass/Fail**: ___________

- [ ] **Inbound Events Stored Properly**
  - Send emails, receive webhooks
  - Query: `SELECT * FROM inbound_events`
  - **Expected**: Events match webhook posts
  - **Pass/Fail**: ___________

- [ ] **User Settings Saved Correctly**
  - Update email provider settings
  - Logout and login
  - **Expected**: Settings persisted
  - **Pass/Fail**: ___________

---

### Performance

- [ ] **Page Loads Complete Within 2 Seconds**
  - Test all main pages: Leads, Campaigns, Metrics, Deliverability
  - **Expected**: Each loads < 2 seconds
  - **Pass/Fail**: ___________

- [ ] **CSV Import of 100 Leads Within 10 Seconds**
  - Upload CSV with 100 leads
  - **Expected**: Import completes < 10 seconds
  - **Pass/Fail**: ___________

- [ ] **AI Email Generation Within 10 Seconds**
  - Generate email for single lead
  - **Expected**: Response < 10 seconds
  - **Pass/Fail**: ___________

- [ ] **Campaign Activation Response Within 3 Seconds**
  - Activate campaign
  - **Expected**: Status updates < 3 seconds
  - **Pass/Fail**: ___________

---

### Browser Compatibility

- [ ] **Chrome (Latest)**
  - Test all features
  - **Expected**: Everything works
  - **Pass/Fail**: ___________

- [ ] **Firefox (Latest)**
  - Test key features
  - **Expected**: Everything works
  - **Pass/Fail**: ___________

- [ ] **Safari (Latest - Mac only)**
  - Test key features
  - **Expected**: Everything works
  - **Pass/Fail**: ___________

- [ ] **Edge (Latest)**
  - Test key features
  - **Expected**: Everything works
  - **Pass/Fail**: ___________

---

## 🎯 Critical Path Tests

### Happy Path: First Campaign (End-to-End)

**Time Estimate**: 10 minutes

1. [ ] Sign up with new account
2. [ ] Configure SendGrid API key in Settings
3. [ ] Import 10 leads from CSV
4. [ ] Create new campaign
5. [ ] Generate AI emails for all leads
6. [ ] Review and edit 1-2 emails
7. [ ] Activate campaign
8. [ ] Monitor sending progress
9. [ ] Check deliverability page for updates
10. [ ] Verify emails in SendGrid dashboard

**Overall Pass/Fail**: ___________

---

### Safety Path: Warmup Compliance

**Time Estimate**: 5 minutes (per day simulation)

1. [ ] New user account (Day 1 of warmup)
2. [ ] Check daily limit (should be 10)
3. [ ] Send 8 emails (within limit)
4. [ ] Verify no warnings
5. [ ] Send 3 more emails (total 11, exceeds limit)
6. [ ] Verify warning appears
7. [ ] Check next day - limit should increase

**Overall Pass/Fail**: ___________

---

### Recovery Path: Fix High Bounce Rate

**Time Estimate**: 5 minutes

1. [ ] Insert test data with 15% bounce rate
2. [ ] Go to Deliverability page
3. [ ] Verify critical alert shown
4. [ ] Stop all campaigns
5. [ ] Review bounced leads
6. [ ] Remove bounced leads from list
7. [ ] Re-check deliverability
8. [ ] Verify recommendations updated

**Overall Pass/Fail**: ___________

---

## 📝 Test Results Summary

**Date**: ___________  
**Tester**: ___________  
**Environment**: Local / Staging / Production

**Total Tests**: ___________  
**Passed**: ___________  
**Failed**: ___________  
**Blocked**: ___________  

**Critical Bugs Found**: ___________  
**Major Bugs Found**: ___________  
**Minor Bugs Found**: ___________  

**Ready for Alpha Launch?**: YES / NO

**Notes**:
```
[Add any additional observations, user experience feedback, or recommendations here]
```

---

## 🚨 Bug Reporting Template

When bugs are found during testing:

```markdown
**Bug ID**: ALPHA-001
**Severity**: Critical / Major / Minor
**Found In**: [Page/Feature]
**Steps to Reproduce**:
1. 
2. 
3. 

**Expected Result**: 
**Actual Result**: 
**Screenshot/Video**: 
**Browser**: 
**Date Found**: 
**Status**: Open / Fixed / Won't Fix
```
