# 🎨 UI/UX Flow Guide - What Users See

> **Step-by-step visual walkthrough of the user experience for each major flow**

---

## 1. Individual Email Sending - Step by Step

### Step 1: User opens Leads page
```
┌─────────────────────────────────────────────────────────────┐
│  LEADS PAGE                                      [Settings] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Leads                                  [+ Create] [Upload] │
│  42 contacts in your database                               │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Search leads...               Page 1 of 3 [<] [>]      ││
│  ├─────────────────────────────────────────────────────────┤│
│  │ Name          │ Email              │ Company  │ Actions ││
│  ├─────────────────────────────────────────────────────────┤│
│  │ John Smith    │ john@techcorp.com  │ TechCorp │ ⋮ Edit  ││
│  │ Jane Doe      │ jane@acme.com      │ ACME Inc │ ⋮ Send  ││
│  │ Bob Johnson   │ bob@startup.io     │ Startup  │ ⋮ Delete││
│  │ ...           │ ...                │ ...      │ ...     ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: User clicks "Send Email" on John Smith
```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL COMPOSER                                    [×] Close │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Send Email to John Smith @ TechCorp                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐│
│  │ Subject:                                              ││
│  │ ┌────────────────────────────────────────────────────┐││
│  │ │ Let's connect - quick idea                         │││
│  │ └────────────────────────────────────────────────────┘││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌────────────────────────────────────────────────────────┐│
│  │ Message Body:                                         ││
│  │ ┌────────────────────────────────────────────────────┐││
│  │ │ Hi John,                                           │││
│  │ │                                                    │││
│  │ │ Noticed TechCorp is expanding into EMEA...        │││
│  │ │                                                    │││
│  │ │ Teams like yours use our platform to...           │││
│  │ │                                                    │││
│  │ │ Open to a quick 15-minute walkthrough?            │││
│  │ │                                                    │││
│  │ │ Best regards,                                     │││
│  │ │ Alex                                              │││
│  │ └────────────────────────────────────────────────────┘││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  [ Generate with AI ] [ Edit ] [ Cancel ] [ Send ]        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: User clicks "Generate with AI"
```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL COMPOSER                                    [×] Close │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ⟳ Generating email...                                      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐│
│  │ ✓ Step 1: Researching lead...                        ││
│  │ ⟳ Step 2: Analyzing company...                       ││
│  │ ○ Step 3: Generating email...                        ││
│  │ ○ Step 4: Personalizing content...                   ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  [ Cancel ]                                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 4: AI generates email (shows result)
```
┌─────────────────────────────────────────────────────────────┐
│  EMAIL COMPOSER                                    [×] Close │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✓ Email Generated!  📧  87 words | 30 sec read | GPT-4   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐│
│  │ Subject:                                              ││
│  │ ┌────────────────────────────────────────────────────┐││
│  │ │ Quick idea for TechCorp - email deliverability    │││
│  │ └────────────────────────────────────────────────────┘││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌────────────────────────────────────────────────────────┐│
│  │ Message Body:                                         ││
│  │ ┌────────────────────────────────────────────────────┐││
│  │ │ Hi John,                                           │││
│  │ │                                                    │││
│  │ │ I noticed TechCorp recently raised Series B...     │││
│  │ │ That's awesome. With that growth, managing        │││
│  │ │ deliverability becomes crucial...                 │││
│  │ │                                                    │││
│  │ │ Would you be open to a 15-min walkthrough?        │││
│  │ │                                                    │││
│  │ │ Best,                                             │││
│  │ │ Alex                                              │││
│  │ └────────────────────────────────────────────────────┘││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  [ Regenerate ] [ Edit ] [ Cancel ] [ Use This ]          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 5: User clicks "Use This"
```
Email is populated in composer with "Send" button active
User can now click "Send" to queue the email
```

### Step 6: User clicks "Send"
```
┌─────────────────────────────────────────────────────────────┐
│  ✓ Success!                                                 │
│  ├─ Email sent to john@techcorp.com                        │
│  └─ View sending logs: [Link]                              │
│                                                              │
│  [Close]                                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘

[Modal closes]
[Returns to Leads page]
[Toast notification at top: "Email sent successfully ✓"]
```

---

## 2. Campaign Creation & Launch - Step by Step

### Step 1: User opens Campaigns page
```
┌─────────────────────────────────────────────────────────────┐
│  CAMPAIGNS                                     [Settings]   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Campaigns                          Create and manage       │
│                                      multi-step sequences   │
│                                                              │
│  ⚠️ Email provider required                                 │
│     Configure SMTP or SendGrid in Settings before          │
│     creating campaigns. [Go to Settings →]                 │
│                                                              │
│  ℹ️ Warmup in progress — Day 3/21                          │
│     Recommended limit: 20 emails today.                    │
│     View Deliverability →                                  │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ NEW CAMPAIGN                                            ││
│  ├─────────────────────────────────────────────────────────┤│
│  │ Campaign Name:  [________________]                      ││
│  │ Description:    [________________]                      ││
│  │ (optional)                                              ││
│  │                                                         ││
│  │              [ Create Campaign ]                        ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  Existing Campaigns:                                        │
│  (None yet)                                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: User enters campaign name and creates
```
┌─────────────────────────────────────────────────────────────┐
│  CAMPAIGNS                                     [Settings]   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Campaigns                                                  │
│                                                              │
│  Existing Campaigns:                                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Q2 2024 Founder Outreach                             │  │
│  │ Target SaaS founders in US                           │  │
│  │                                                       │  │
│  │ Status: DRAFT  │  0 leads  │  Created: Jan 15       │  │
│  │                                                       │  │
│  │ [ Edit ] [ Launch ] [ Delete ]                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘

[Toast: "Campaign created. ✓"]
```

### Step 3: User clicks "Edit" → Opens Campaign Editor
```
┌─────────────────────────────────────────────────────────────┐
│  CAMPAIGN EDITOR: Q2 2024 Founder Outreach                 │
│                  Status: DRAFT  [Launched] [Delete]        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SEQUENCE STEPS                                             │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐│
│  │ STEP 1: Initial Outreach (Day 0)                      ││
│  ├────────────────────────────────────────────────────────┤│
│  │ Subject: Let's connect                                ││
│  │ ┌──────────────────────────────────────────────────┐  ││
│  │ │ Hi {first_name},                                 │  ││
│  │ │                                                  │  ││
│  │ │ Noticed {company} is in the {industry} space...  │  ││
│  │ │                                                  │  ││
│  │ │ Open to a quick chat?                            │  ││
│  │ │                                                  │  ││
│  │ │ Best,                                            │  ││
│  │ │ Alex                                             │  ││
│  │ └──────────────────────────────────────────────────┘  ││
│  │ Delay: 0 days  [ × Delete ]                            ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌────────────────────────────────────────────────────────┐│
│  │ STEP 2: Follow-up (Day 3)                             ││
│  ├────────────────────────────────────────────────────────┤│
│  │ Subject: Following up                                 ││
│  │ ┌──────────────────────────────────────────────────┐  ││
│  │ │ Hi {first_name},                                 │  ││
│  │ │                                                  │  ││
│  │ │ Didn't hear back, but would still love to...     │  ││
│  │ └──────────────────────────────────────────────────┘  ││
│  │ Delay: 3 days  [ × Delete ]                            ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  [ + Add Step ]  [ Save Campaign ]                         │
│                                                              │
│  CAMPAIGN LEADS                                             │
│  ┌────────────────────────────────────────────────────────┐│
│  │ No leads added yet. [ Add Leads ]                      ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 4: User clicks "Add Leads"
```
┌─────────────────────────────────────────────────────────────┐
│  SELECT LEADS TO ADD                              [×] Close │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Select leads for: Q2 2024 Founder Outreach               │
│                                                              │
│  ┌─ Search: [________________]                             │
│  │                                                         │
│  ├─ [☑] John Smith (john@techcorp.com) - TechCorp        │
│  ├─ [☐] Jane Doe (jane@acme.com) - ACME Inc             │
│  ├─ [☑] Bob Johnson (bob@startup.io) - Startup          │
│  ├─ [☐] Alice Brown (alice@app.com) - App Co            │
│  ├─ [☑] Charlie Davis (charlie@saas.com) - SaaS         │
│  └─ ... (20 more leads)                                  │
│                                                          │
│  Selected: 3 leads                                       │
│                                                          │
│  [ Cancel ] [ Add Selected (3) ]                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Step 5: User clicks "Add Selected"
```
Leads added to campaign

┌────────────────────────────────────────┐
│ CAMPAIGN LEADS                         │
├────────────────────────────────────────┤
│ 3 leads added                          │
│                                        │
│ ┌────────────────────────────────────┐│
│ │ John Smith (john@techcorp.com)    ││
│ │ Bob Johnson (bob@startup.io)      ││
│ │ Charlie Davis (charlie@saas.com)  ││
│ └────────────────────────────────────┘│
│                                        │
│ [ + Add More Leads ]                   │
│                                        │
└────────────────────────────────────────┘
```

### Step 6: User saves and launches campaign
```
User clicks "Launched" button at top

┌────────────────────────────────────────┐
│ ✓ Campaign Launched!                   │
│                                        │
│ Status: ACTIVE                         │
│ Emails will start sending immediately │
│                                        │
│ [ View Campaign ] [ Back ]             │
│                                        │
└────────────────────────────────────────┘

Campaign Editor updates:
Status: ACTIVE  [Pause]  [Delete]

CAMPAIGN PROGRESS:
└─ Total leads: 3
   ├─ Pending: 0
   ├─ In Progress: 3
   ├─ Completed: 0
   └─ Failed: 0

Step 1 (Day 0): 3/3 sent ✓
Step 2 (Day 3): Waiting...
Step 3 (Day 7): Waiting...
```

### Step 7: Real-time progress updates (polling)
```
After campaign launches, frontend polls for updates every 5 seconds:

2 seconds later:
┌─────────────────────────────────────────────────────┐
│ CAMPAIGN PROGRESS (Real-time)                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Step 1 (Day 0 - Initial): 3/3 sent ✓              │
│ ┌─────────────────────────────────────────────────┐│
│ │ ████████████████████ 100%                       ││
│ └─────────────────────────────────────────────────┘│
│                                                     │
│ Step 2 (Day 3 - Follow-up): Waiting (3/3)...      │
│ ┌─────────────────────────────────────────────────┐│
│ │ ░░░░░░░░░░░░░░░░░░░░ 0%                         ││
│ └─────────────────────────────────────────────────┘│
│                                                     │
│ Step 3 (Day 7 - Final): Waiting (3/3)...          │
│ ┌─────────────────────────────────────────────────┐│
│ │ ░░░░░░░░░░░░░░░░░░░░ 0%                         ││
│ └─────────────────────────────────────────────────┘│
│                                                     │
│ Last update: Just now ⟳                            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 3. Lead Discovery - Step by Step

### Step 1: User opens Discover Leads page
```
┌─────────────────────────────────────────────────────────────┐
│  DISCOVER LEADS                                 [Settings]  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Find new leads using AI                                    │
│                                                              │
│  SEARCH PARAMETERS                                          │
│  ┌────────────────────────────────────────────────────────┐│
│  │ Keywords:     [SaaS founders________________]          ││
│  │ Location:     [United States____________]             ││
│  │ Industry:     [B2B Software ▼]                        ││
│  │                                                        ││
│  │ Advanced ▼                                             ││
│  │ ├─ Job Title: [Founder, CEO________]                  ││
│  │ ├─ Seniority: [C-Suite ▼]                             ││
│  │ └─ Max Results: [50 leads ◀───●─▶]                   ││
│  │                                                        ││
│  │              [ Start Discovery ]                       ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  RECENT JOBS                                                │
│  (None yet)                                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: User clicks "Start Discovery"
```
Discovery job created and queued
Frontend begins polling for status

┌─────────────────────────────────────────────────────────────┐
│  DISCOVERING LEADS...                                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Progress                                                   │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ ⟳ Step 1: Searching domains...                        ││
│  │ ○ Step 2: Crawling websites...                        ││
│  │ ○ Step 3: Extracting emails...                        ││
│  │ ○ Step 4: Enriching data...                           ││
│  │                                                        ││
│  │ Found: 0/50 leads                                      ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  [ Cancel ]                                                 │
│                                                              │
│                                                              │
│  RESULTS (Will appear as discovered)                        │
│  (Empty - waiting for results)                             │
│                                                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Results start appearing (polling updates)
```
2 seconds later:
┌─────────────────────────────────────────────────────────────┐
│  DISCOVERING LEADS...                                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Progress                                                   │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ ✓ Step 1: Searching domains (12 found)                ││
│  │ ⟳ Step 2: Crawling websites (2 done)...              ││
│  │ ○ Step 3: Extracting emails...                        ││
│  │ ○ Step 4: Enriching data...                           ││
│  │                                                        ││
│  │ Found: 2/50 leads                                      ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  RESULTS                                                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ 👤 John Smith                                          ││
│  │    CEO at TechCorp                                     ││
│  │    📧 john@techcorp.com                                ││
│  │    🔗 LinkedIn   [ + Add to Leads ]                    ││
│  │                                                        ││
│  │ 👤 Jane Doe                                           ││
│  │    VP Sales at TechCorp                                ││
│  │    📧 jane@techcorp.com                                ││
│  │    🔗 LinkedIn   [ + Add to Leads ]                    ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│ [ Add All 2 to Leads ] or select individual [ + Add ]      │
│                                                              │
└─────────────────────────────────────────────────────────────┘

4 seconds later (continuing to poll):
Found: 8/50 leads

RESULTS section continues to grow as backend processes:
├─ 👤 John Smith @ TechCorp
├─ 👤 Jane Doe @ TechCorp
├─ 👤 Bob Brown @ StartupXYZ
├─ 👤 Alice Green @ AppCorp
├─ 👤 Charlie Wilson @ SaaSOps
├─ 👤 Diana Prince @ TechVentures
├─ 👤 Edward Norton @ CloudSoft
└─ 👤 Fiona Scott @ DigitalCo
```

### Step 4: Discovery completes
```
┌─────────────────────────────────────────────────────────────┐
│  DISCOVER LEADS - COMPLETED                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Progress                                                   │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ ✓ Step 1: Searching domains (25 found)                ││
│  │ ✓ Step 2: Crawling websites (25 done)                 ││
│  │ ✓ Step 3: Extracting emails (18 found)                ││
│  │ ✓ Step 4: Enriching data (complete)                   ││
│  │                                                        ││
│  │ COMPLETED: Found 18/50 leads                           ││
│  │ Duration: 2m 34s                                       ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  RESULTS (18 LEADS)                                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Select: [☐] All                                        ││
│  │                                                        ││
│  │ [☑] 👤 John Smith - john@techcorp.com                 ││
│  │ [☑] 👤 Jane Doe - jane@techcorp.com                   ││
│  │ [☑] 👤 Bob Brown - bob@startupxyz.com                 ││
│  │ ... (15 more)                                         ││
│  │                                                        ││
│  │ Selected: 18                                           ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  [ Cancel ] [ Add Selected (18) to Leads ]                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 5: User clicks "Add Selected"
```
┌────────────────────────────────────┐
│ ✓ Added 18 new leads               │
│                                    │
│ [ View in Leads Page ]             │
│ [ Start New Discovery ]            │
│                                    │
└────────────────────────────────────┘

Frontend redirects to Leads page showing the 18 new leads
```

---

## 4. Settings - Email Provider Configuration

### Step 1: User opens Settings
```
┌─────────────────────────────────────────────────────────────┐
│  SETTINGS                                                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Email Provider Configuration                               │
│                                                              │
│  ┌─ [ SMTP ]  [ SendGrid ]                                 │
│  │                                                         │
│  ├─ Current Provider: Not configured                       │
│  │                                                         │
│  ├─ SMTP Configuration                                     │
│  │ ├─ SMTP Host: [smtp.gmail.com________]               │
│  │ ├─ Port:      [587]                                   │
│  │ ├─ Username:  [your-email@gmail.com_____]            │
│  │ ├─ Password:  [••••••••••••••] (encrypted)           │
│  │ ├─ Use SSL:   [☑]                                     │
│  │ ├─ Use TLS:   [☐]                                     │
│  │ ├─ From Name: [Alex Wilson__]                         │
│  │ └─ From Email:[sender@gmail.com_____]                │
│  │                                                         │
│  │ [ Test Email ] [ Save Settings ]                       │
│  └─                                                         │
│                                                              │
│  SendGrid Configuration                                     │
│  ├─ API Key: [SG.xxxxxxxxxxxx] (encrypted)                │
│  ├─ From Name: [Alex Wilson__]                            │
│  ├─ From Email: [sender@domain.com_____]                 │
│  │                                                         │
│  │ [ Test Email ] [ Save Settings ]                       │
│  └─                                                         │
│                                                              │
│  Webhook Configuration                                      │
│  ├─ Webhook URL: https://yourapp.com/webhooks/sendgrid   │
│  └─ [ Copy ] [ Setup Guide ]                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: User configures SMTP and tests
```
User fills in SMTP settings and clicks "Test Email"

┌──────────────────────────────────────┐
│ Testing email send...                │
│                                      │
│ Sending test email to:               │
│ alex@example.com                     │
│                                      │
│ Status: Connecting to SMTP server... │
│         ⟳                            │
│                                      │
└──────────────────────────────────────┘

After 2 seconds:
┌──────────────────────────────────────┐
│ ✓ Test email sent successfully!      │
│                                      │
│ Check your inbox for the test email. │
│                                      │
│ [ OK ] [ Try Again ]                 │
│                                      │
└──────────────────────────────────────┘

User clicks "OK" and then "Save Settings"

Toast appears:
┌──────────────────────────────────────┐
│ ✓ Settings saved                     │
│   Email provider configured          │
│                                      │
└──────────────────────────────────────┘
```

---

## 5. Real-time Status Indicators

### Email Delivery Status (Deliverability Page)
```
┌─────────────────────────────────────────────────────────────┐
│  DELIVERABILITY                                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  WARMUP STATUS (Day 3/21)                                   │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ ░░░●○○○○○○○○○○○○○○○ Day 3/21                          ││
│  │                                                         ││
│  │ Daily Limit: 20 emails                                 ││
│  │ Sent Today: 12 emails                                  ││
│  │ ████████░░ 60%                                          ││
│  │                                                         ││
│  │ ⚠️  Approaching limit. Consider pausing sends.         ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  DELIVERY METRICS (Last 7 days)                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Total Sent:      142                                   ││
│  │ ├─ Delivered:    136 (95.8%)  ✓                        ││
│  │ ├─ Bounced:      4 (2.8%)     ⚠️                       ││
│  │ └─ Spam/Other:   2 (1.4%)     ⚠️                       ││
│  │                                                         ││
│  │ Opens:           68 (47.9%)                             ││
│  │ Clicks:          12 (8.5%)                              ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  CHARTS                                                     │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Delivery Rate Over Time                               ││
│  │  100% │     ╱‾‾‾╲                                     ││
│  │   95% │ ___╱     ╲___                                  ││
│  │   90% │                                                 ││
│  │       └─┴─┴─┴─┴─┴─┴─┴─ (Last 7 days)                  ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Loading States & Feedback

### Email Generation Loading
```
Initial state:
┌────────────────────────────┐
│ [ Generate with AI ]       │
└────────────────────────────┘

Clicked:
┌────────────────────────────┐
│ ⟳ Generating...            │
│ (button disabled)          │
└────────────────────────────┘

Complete:
┌────────────────────────────┐
│ ✓ Use This                  │
│ [ Regenerate ] [ Edit ]     │
└────────────────────────────┘
```

### Campaign Sending Progress
```
Before sending:
┌─────────────────────────────────────┐
│ Step 1 (Day 0):  ○ Pending (0/3)   │
│ Step 2 (Day 3):  ○ Pending (0/3)   │
│ Step 3 (Day 7):  ○ Pending (0/3)   │
└─────────────────────────────────────┘

During sending (real-time update):
┌─────────────────────────────────────┐
│ Step 1 (Day 0):  ⟳ Sending (2/3)   │
│ Step 2 (Day 3):  ○ Waiting (0/3)   │
│ Step 3 (Day 7):  ○ Waiting (0/3)   │
└─────────────────────────────────────┘

After complete:
┌─────────────────────────────────────┐
│ Step 1 (Day 0):  ✓ Sent (3/3)       │
│ Step 2 (Day 3):  ○ Waiting (0/3)   │
│ Step 3 (Day 7):  ○ Waiting (0/3)   │
└─────────────────────────────────────┘
```

### Lead Discovery Progress (Polling)
```
Update cycle: every 2 seconds

Update 1:
Domains: 0  |  Leads: 0  |  Time: 2s
Status: Searching...

Update 2:
Domains: 8  |  Leads: 0  |  Time: 4s
Status: Crawling websites...

Update 3:
Domains: 12  |  Leads: 3  |  Time: 6s
Status: Extracting emails...

Update 4:
Domains: 12  |  Leads: 5  |  Time: 8s
Status: Enriching data...

Update 5:
Domains: 12  |  Leads: 12  |  Time: 10s
Status: Completed! ✓
```

---

## 7. Error States

### Email Send Failed
```
┌──────────────────────────────────────┐
│ ✗ Error: Email Send Failed           │
│                                      │
│ SMTP Connection Failed               │
│ "Authentication failed"              │
│                                      │
│ Please check:                        │
│ 1. Email provider credentials        │
│ 2. SMTP host & port settings        │
│ 3. Internet connection               │
│                                      │
│ [ Go to Settings ] [ Try Again ]     │
│                                      │
└──────────────────────────────────────┘
```

### Campaign Creation Failed
```
┌──────────────────────────────────────┐
│ ✗ Error                              │
│                                      │
│ Email provider not configured        │
│                                      │
│ You must configure your email        │
│ provider before creating campaigns.  │
│                                      │
│ [ Go to Settings ]                   │
│                                      │
└──────────────────────────────────────┘
```

### Lead Discovery Timeout
```
┌──────────────────────────────────────┐
│ ⚠️  Discovery took longer than       │
│    expected                          │
│                                      │
│ Current progress:                    │
│ • Domains found: 15                  │
│ • Leads discovered: 8                │
│                                      │
│ Discovery is still running in the    │
│ background. Check back in a moment.  │
│                                      │
│ [ View Results ] [ Cancel ]          │
│                                      │
└──────────────────────────────────────┘
```

---

## 8. Success Toasts & Notifications

```
Email Sent:
┌─────────────────────────────────┐
│ ✓ Email sent successfully        │
│   to john@example.com            │
│   [View Logs]          [×]       │
└─────────────────────────────────┘

Campaign Launched:
┌─────────────────────────────────┐
│ ✓ Campaign activated            │
│   Sending will begin shortly    │
│   [View Campaign]      [×]       │
└─────────────────────────────────┘

Leads Added:
┌─────────────────────────────────┐
│ ✓ Added 18 new leads            │
│   to your database              │
│   [View Leads]         [×]       │
└─────────────────────────────────┘

Settings Saved:
┌─────────────────────────────────┐
│ ✓ Settings saved                │
│   Email provider configured     │
│   [×]                           │
└─────────────────────────────────┘
```

---

This UI/UX guide shows exactly what users see throughout their journey using the application!
