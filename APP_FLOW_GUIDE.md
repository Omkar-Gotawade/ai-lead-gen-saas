# 📊 Complete App Flow Guide

> **This document explains the complete flow of the Lead Generation + Outreach SaaS application, from user interactions to backend processing.**

---

## 🎯 Quick Navigation

- [System Architecture](#system-architecture)
- [Flow 1: Individual Email Sending](#flow-1-send-email-to-individual-lead)
- [Flow 2: Campaign Bulk Email Sending](#flow-2-campaign-bulk-email-sending)
- [Flow 3: Email Generation with AI](#flow-3-ai-email-generation)
- [Flow 4: Lead Discovery](#flow-4-lead-discovery)
- [Page-by-Page Guide](#page-by-page-guide)
- [Database Schema](#database-schema)

---

## 🏗️ System Architecture

```
USER BROWSER
    ↓ (HTTP REST API)
┌─────────────────────────────────────┐
│   FRONTEND (React + Vite)           │
│   - Pages: Leads, Campaigns, etc.   │
│   - Components & State Management   │
│   - Axios API Client                │
└─────────────────────────────────────┘
    ↓ (REST API Calls)
┌─────────────────────────────────────┐
│   BACKEND (FastAPI)                 │
│   - Routes & Controllers            │
│   - Services (Business Logic)       │
│   - Models & Schemas                │
└─────────────────────────────────────┘
    ↓         ↓           ↓
  PostgreSQL Redis     Celery Worker
  (Database) (Cache)   (Background Jobs)
            (Queue)
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React + Vite | UI Components, State Management |
| **Backend** | FastAPI | REST API, Business Logic |
| **Database** | PostgreSQL | Persistent Data Storage |
| **Queue** | Redis + Celery | Background Job Processing |
| **AI** | OpenRouter API | Email Generation |
| **Email** | SMTP / SendGrid | Email Delivery |

---

## Flow 1: Send Email to Individual Lead

### 📍 Location: **Leads Page**

### User Flow (Step by Step)

```
1. User opens "Leads" page
   ↓
2. User clicks on a lead row → Opens lead details
   ↓
3. User clicks "Send Email" button
   ↓
4. Email Composer Modal opens
   ├─ Populated with lead name/company
   ├─ Template suggestion option
   └─ User can edit subject & body
   ↓
5. User clicks "Send" button
   ↓
6. API Request: POST /email/send
   └─ Payload: {lead_id, subject, body}
   ↓
7. Backend processes request
   ↓
8. Email is queued & sent
   ↓
9. User sees success notification
```

### Backend Flow (Detailed)

#### **Step 1-2: Frontend Preparation**
```
File: src/pages/Leads.jsx
File: src/components/EmailComposer.jsx

When user clicks "Send Email":
- EmailComposer component opens
- Pre-fills with lead data
- User edits subject/body
- User clicks "Send"
```

#### **Step 3-4: API Request**
```
File: src/api/index.js

POST /email/send
{
  "lead_id": "uuid",
  "subject": "Let's connect",
  "body": "Hi John, I found your profile..."
}
```

#### **Step 5: Backend Controller**
```
File: backend/app/routes/email_send.py

@router.post("/email/send")
async def send_email_endpoint(request, current_user, db):
    1. Validate request
    2. Fetch lead from database
       - Check: Lead belongs to user
       - Check: Lead email exists
    3. Enforce rate limit
       - Check: User hasn't exceeded daily limit
    4. Enqueue email task
       - send_email_task.delay(
           user_id, to_email, subject, body, lead_id
         )
    5. Return: {queued: true, message: "..."}
```

#### **Step 6: Background Processing (Celery Worker)**
```
File: backend/app/workers/email_worker.py

send_email_task.delay():
1. Fetch user's email provider settings
   └─ Get: SMTP or SendGrid credentials (encrypted)
2. Decrypt email credentials
3. Fetch lead details from database
4. Generate email headers
5. Send email via provider
   ├─ If SMTP:
   │  └─ smtplib.SMTP → server.sendmail()
   └─ If SendGrid:
      └─ SendGridAPIClient → sg.send()
6. Log sending result
   ├─ Success: Save to SendingLog table
   ├─ Failure: Retry with backoff
   └─ Final failure: Mark as failed
7. Update SendingLog with:
   - Status (sent/failed)
   - Provider (SMTP/SendGrid)
   - Timestamp
```

#### **Step 7-8: Email Delivery**
```
SMTP Flow:
┌─────────────────────────────────────┐
│ Celery Worker                       │
│  1. Connect to SMTP server          │
│  2. Authenticate with credentials   │
│  3. Send email                      │
│  4. Close connection                │
└──────────────────┬──────────────────┘
                   │
        ┌──────────▼──────────┐
        │   Email Provider    │
        │   - Gmail SMTP      │
        │   - AWS SES         │
        │   - Custom SMTP     │
        └─────────┬───────────┘
                  │
        ┌─────────▼─────────┐
        │ Recipient Inbox   │
        │ (Lead receives    │
        │  email)           │
        └───────────────────┘

SendGrid Flow:
┌─────────────────────────────────────┐
│ Celery Worker                       │
│  1. Call SendGrid API               │
│  2. POST /v3/mail/send              │
│  3. Include headers for tracking    │
└──────────────────┬──────────────────┘
                   │
        ┌──────────▼──────────┐
        │   SendGrid Service  │
        │   - Queue email     │
        │   - Track opens     │
        │   - Track clicks    │
        │   - Track bounces   │
        └─────────┬───────────┘
                  │
        ┌─────────▼─────────┐
        │ Recipient Inbox   │
        │ (Lead receives    │
        │  email with       │
        │  tracking pixels) │
        └───────────────────┘
```

#### **Step 9: Frontend Update**
```
File: src/pages/Leads.jsx

After sending:
1. API returns success response
2. Toast notification appears
   └─ "Email sent successfully"
3. Email composer modal closes
4. Leads page refreshes (optional)
```

### Database Changes
```
SendingLog Table (New Entry Created):
├─ id: UUID
├─ user_id: UUID (linked to current user)
├─ lead_id: UUID (linked to lead)
├─ to_email: String
├─ subject: String
├─ status: "sent" / "failed" / "pending"
├─ provider: "smtp" / "sendgrid"
├─ created_at: Timestamp
├─ sent_at: Timestamp
└─ error_message: String (if failed)
```

### Error Handling
```
Possible Errors:
├─ Lead not found (404)
├─ Email provider not configured (400)
├─ Rate limit exceeded (429)
├─ SMTP connection failed (500)
├─ SendGrid API error (500)
└─ Invalid email address (400)

Retry Logic:
├─ Failed sends: Retry up to 3 times
├─ Exponential backoff: 1s → 2s → 4s
└─ Final failure: Log error and notify user
```

---

## Flow 2: Campaign Bulk Email Sending

### 📍 Location: **Campaigns Page & Campaign Editor**

### User Flow (Step by Step)

```
1. User opens "Campaigns" page
   ↓
2. User clicks "New Campaign" button
   ↓
3. Campaign Creation Modal opens
   ├─ Enter campaign name
   ├─ Enter description (optional)
   └─ Click "Create"
   ↓
4. Campaign is created (Status: DRAFT)
   ↓
5. User clicks on campaign → Opens Campaign Editor
   ↓
6. In Campaign Editor:
   ├─ Set up email sequence steps
   │  ├─ Step 1 (Day 0): Initial email
   │  ├─ Step 2 (Day 3): Follow-up 1
   │  └─ Step 3 (Day 7): Follow-up 2
   ├─ Configure each step with:
   │  ├─ Subject
   │  ├─ Body
   │  └─ Delay before sending (days)
   └─ Click "Save Campaign"
   ↓
7. User clicks "Add Leads" button
   ├─ Select leads to add to campaign
   └─ Click "Add Selected"
   ↓
8. Leads are enqueued to campaign
   ↓
9. User clicks "Launch Campaign" button
   ↓
10. Campaign status changes to ACTIVE
    ↓
11. Celery worker processes:
    ├─ For each lead in campaign:
    │  ├─ Wait for step 1 delay (0 days)
    │  ├─ Send step 1 email
    │  ├─ Wait for step 2 delay (3 days)
    │  ├─ Send step 2 email
    │  ├─ Wait for step 3 delay (7 days)
    │  └─ Send step 3 email
    └─ Mark campaign lead as completed
```

### Backend Flow (Detailed)

#### **Step 1-3: Campaign Creation**
```
File: backend/app/routes/campaigns.py

POST /campaigns
{
  "name": "Q2 2024 Outreach",
  "description": "Target SaaS founders"
}

Process:
1. Validate user is authenticated
2. Create Campaign object:
   ├─ id: UUID
   ├─ user_id: current_user.id
   ├─ name: "Q2 2024 Outreach"
   ├─ status: CampaignStatus.DRAFT
   └─ created_at: now()
3. Save to database
4. Return campaign object
```

#### **Step 4-6: Add Sequence Steps**
```
File: backend/app/routes/campaigns.py

POST /campaigns/{campaign_id}/steps
{
  "subject": "Let's connect",
  "body": "Hi {first_name}...",
  "delay_days": 0,
  "step_order": 1
}

Process (for each step):
1. Validate campaign exists & user owns it
2. Create SequenceStep object:
   ├─ id: UUID
   ├─ campaign_id: campaign_id
   ├─ subject: "Let's connect"
   ├─ body: "Hi {first_name}..."
   ├─ delay_days: 0
   ├─ step_order: 1
   └─ created_at: now()
3. Save to database
4. Return sequence step
```

#### **Step 7-9: Add Leads & Launch Campaign**
```
File: backend/app/routes/campaigns.py

POST /campaigns/{campaign_id}/add-leads
{
  "lead_ids": ["uuid1", "uuid2", "uuid3"]
}

Process:
1. Validate campaign exists & user owns it
2. For each lead_id:
   ├─ Validate lead exists & user owns it
   ├─ Create CampaignLead object:
   │  ├─ id: UUID
   │  ├─ campaign_id: campaign_id
   │  ├─ lead_id: lead_id
   │  ├─ status: CampaignLeadStatus.PENDING
   │  ├─ current_step: 1
   │  └─ created_at: now()
   └─ Save to database
3. Return confirmation

PUT /campaigns/{campaign_id}/launch

Process:
1. Validate campaign exists & user owns it
2. Update campaign:
   ├─ status: CampaignStatus.ACTIVE
   ├─ started_at: now()
   └─ updated_at: now()
3. Enqueue campaign processing task:
   └─ process_campaign_task.delay(campaign_id)
4. Return campaign object
```

#### **Step 10-11: Background Processing (Celery Worker)**
```
File: backend/app/workers/campaign_worker.py

process_campaign_task(campaign_id):

1. Fetch campaign from database
2. Validate campaign is ACTIVE
3. Fetch all campaign leads with status PENDING/IN_PROGRESS:
   └─ Get: id, lead_id, current_step, created_at

4. For each campaign lead:
   ├─ Calculate which step should be sent now:
   │  ├─ Get sequence steps in order
   │  ├─ For each step:
   │  │  ├─ Calculate: when to send = lead_added_time + delay_days
   │  │  └─ If when_to_send <= now:
   │  │     └─ This step is ready to send
   │  └─ If no steps ready: Skip to next lead
   │
   ├─ For each step ready to send:
   │  ├─ Fetch lead details
   │  ├─ Fetch user's email provider
   │  ├─ Personalize email:
   │  │  ├─ Replace {{first_name}} with lead.first_name
   │  │  ├─ Replace {{last_name}} with lead.last_name
   │  │  ├─ Replace {{company}} with lead.company
   │  │  └─ Replace other variables (template placeholders use double-curly syntax)
   │  ├─ Enqueue email send:
   │  │  └─ send_email_task.delay(
   │  │      user_id, to_email, subject, body,
   │  │      lead_id, campaign_id, step_id
   │  │    )
   │  ├─ Update CampaignLead:
   │  │  ├─ current_step: next_step_number
   │  │  ├─ last_step_sent_at: now()
   │  │  └─ status: IN_PROGRESS / COMPLETED
   │  └─ Save to database
   │
   └─ If all steps completed:
      └─ Update CampaignLead.status = COMPLETED

5. Scheduling and dispatch details:
   └─ A Celery Beat task `check_pending_campaigns` runs frequently (every minute) and:
      1. Queries `CampaignLead` rows where `status` is `PENDING` or `IN_PROGRESS` and `next_run_at <= now()`.
      2. Reserves candidates atomically by updating the row to `status=QUEUED` and extending `next_run_at` to a short reservation window.
      3. Dispatches `run_sequence_step` tasks for reserved rows (one task per campaign-lead step).
      4. `run_sequence_step` executes the step:
         - If the step requires AI generation, the worker first performs fresh lead research (calls `research_lead_with_status`) to populate or refresh `lead.research_notes` so the AI prompt has up-to-date personalization context.
         - After research (or immediately for template steps), the worker generates or renders the email, performs spam/quality checks, calls `send_email_task.delay(...)` and, if another step exists, schedules the next step with an `eta` computed from the next step's `delay_days`.
```

### Database Schema
```
Campaigns Table:
├─ id: UUID (Primary Key)
├─ user_id: UUID (Foreign Key → Users)
├─ name: String
├─ description: String (Nullable)
├─ status: Enum (draft, active, paused, completed)
├─ created_at: DateTime
└─ updated_at: DateTime

SequenceSteps Table:
├─ id: UUID (Primary Key)
├─ campaign_id: UUID (Foreign Key → Campaigns)
├─ step_order: Integer
├─ subject: String
├─ body: String (with {variable} placeholders)
├─ delay_days: Integer
├─ created_at: DateTime
└─ updated_at: DateTime

CampaignLeads Table:
├─ id: UUID (Primary Key)
├─ campaign_id: UUID (Foreign Key → Campaigns)
├─ lead_id: UUID (Foreign Key → Leads)
├─ status: Enum (pending, in_progress, completed, failed)
├─ current_step: Integer
├─ last_step_sent_at: DateTime (Nullable)
├─ created_at: DateTime
└─ updated_at: DateTime

SendingLogs Table:
├─ id: UUID (Primary Key)
├─ user_id: UUID (Foreign Key → Users)
├─ lead_id: UUID (Foreign Key → Leads)
├─ campaign_id: UUID (Foreign Key → Campaigns, Nullable)
├─ to_email: String
├─ subject: String
├─ body: String
├─ status: Enum (pending, sent, failed, bounced)
├─ provider: String (smtp, sendgrid)
├─ created_at: DateTime
├─ sent_at: DateTime (Nullable)
└─ error_message: String (Nullable)
```

### Progress Tracking (Real-time)

```
Frontend polls for campaign status:

File: src/pages/CampaignEditor.jsx

const pollCampaignStatus = () => {
  setInterval(async () => {
    const response = await api.get(`/campaigns/${campaignId}`)
    setCampaignData(response.data)
    // Update UI with:
    // - Total leads
    // - Leads sent
    // - Leads pending
    // - Current step
  }, 5000)  // Poll every 5 seconds
}

Response includes:
{
  "id": "uuid",
  "name": "Q2 Outreach",
  "status": "active",
  "leads_count": 100,
  "leads_sent": 45,
  "leads_pending": 55,
  "current_step": 1,
  "last_check_at": "2024-01-15T10:30:00Z"
}
```

---

## Flow 3: AI Email Generation

### 📍 Location: **Leads Page (Individual) or Campaign Editor (Bulk)**

### User Flow (Step by Step)

```
1. User opens email composer modal
   ↓
2. User clicks "Generate with AI" button
   ├─ Lead details are shown:
   │  ├─ Name
   │  ├─ Company
   │  ├─ Title
   │  └─ Research notes
   └─ Click "Generate"
   ↓
3. Frontend shows progress:
   ├─ "Step 1: Researching lead..."
   ├─ "Step 2: Analyzing company..."
   ├─ "Step 3: Generating email..."
   └─ "Step 4: Personalizing content..."
   ↓
4. AI generates email
   ↓
5. Email appears in composer
   ├─ Subject
   ├─ Body
   └─ "Edit" / "Regenerate" / "Use" buttons
   ↓
6. User clicks "Use" or edits and sends
```

### Backend Flow (Detailed)

#### **Step 1-3: API Request**
```
File: src/api/index.js

POST /generate-email
{
  "lead_id": "uuid",
  "tone": "professional",  // or "friendly", "casual"
  "goal": "introduce",      // or "follow_up", "meeting_request"
  "custom_prompt": null     // Optional override
}

Request reaches:
File: backend/app/routes/email_ai.py

@router.post("/generate-email")
async def generate_email_endpoint(request, current_user, db):
    # Validate request
    # Fetch lead
    # Call AI service
```

#### **Step 4-7: AI Generation Process**

```
File: backend/app/services/ai_email_service.py

def generate_email(lead, tone, goal):
    
    1. Build research context:
       ├─ Fetch lead data:
       │  ├─ First name
       │  ├─ Last name
       │  ├─ Company
       │  ├─ Title
       │  ├─ Website (if available)
       │  ├─ Research notes
       │  └─ Enriched data (LinkedIn, etc.)
       │
       └─ Build context string:
          └─ "Name: John Smith, Company: TechCorp, Role: VP Sales,
              Context: They are expanding into EMEA..."
    
    2. Build AI prompt:
       ├─ System prompt:
       │  └─ "You are an expert B2B sales email copywriter..."
       ├─ Instructions:
       │  ├─ Keep emails under 100 words
       │  ├─ Make it personalized and specific
       │  ├─ Use {first_name} variable
       │  ├─ Match tone: professional/friendly/casual
       │  └─ Goal: introduce/follow_up/meeting_request
       └─ Lead context
    
    3. Call OpenRouter API:
       ├─ Model: gpt-4 or claude-3
       ├─ Temperature: 0.7 (creativity)
       ├─ Max tokens: 500
       └─ Timeout: 30 seconds
    
    4. Parse AI response:
       ├─ Extract subject line
       ├─ Extract email body
       ├─ Validate email mentions lead/company
       ├─ Remove postscripts
       └─ Clean formatting
    
    5. Return EmailGenerateResponse:
       {
         "subject": "Let's connect - quick idea",
         "body": "Hi John,\n\nNoticed TechCorp is expanding..."
       }
```

#### **Step 8-10: Frontend Display**

```
File: src/components/EmailComposer.jsx

When generation completes:
1. Show generated email in preview
2. Display stats:
   ├─ Word count: 87
   ├─ Reading time: 30 seconds
   └─ Generated with: GPT-4
3. Show action buttons:
   ├─ Edit in text field
   ├─ Regenerate (call API again)
   ├─ Use (populate into form)
   └─ Discard
```

### Step-by-Step Progress Tracking

```
Frontend Implementation:
File: src/components/EmailComposer.jsx

const generateEmail = async () => {
  setLoading(true)
  
  // Step 1: Start request
  setProgress("Step 1: Researching lead...")
  
  // Step 2: Fetch lead data
  setProgress("Step 2: Analyzing company...")
  
  // Step 3: Call API
  setProgress("Step 3: Generating email...")
  const response = await api.post('/generate-email', {
    lead_id, tone, goal
  })
  
  // Step 4: Display result
  setProgress("Step 4: Personalizing content...")
  setGeneratedEmail(response.data)
  setLoading(false)
}

UI shows:
┌─────────────────────────────────┐
│ Generating Email...             │
├─────────────────────────────────┤
│ ✓ Step 1: Researching lead      │
│ ✓ Step 2: Analyzing company     │
│ ⟳ Step 3: Generating email      │
│ ○ Step 4: Personalizing content │
│                                 │
│ [Cancel]                        │
└─────────────────────────────────┘
```

### Error Handling & Fallbacks

```
Possible Errors:
├─ OpenRouter quota exceeded (429)
│  └─ Fallback: Use rule-based template
├─ Lead missing required fields
│  └─ Fallback: Use generic template
├─ API timeout (>30s)
│  └─ Fallback: Show error + retry button
└─ Invalid response from AI
   └─ Fallback: Show error + try again

Rule-Based Fallback Email:
{
  "subject": f"Quick idea for {company}",
  "body": f"Hi {first_name},\n\n"
          f"Noticed you're in {title} at {company}.\n\n"
          f"Our product helps teams like yours..."
}
```

---

## Flow 4: Lead Discovery

### 📍 Location: **Discover Leads Page**

### User Flow (Step by Step)

```
1. User opens "Discover Leads" page
   ↓
2. User enters search criteria:
   ├─ Keywords: "SaaS founders"
   ├─ Location: "US"
   ├─ Industry: "B2B Software"
   ├─ Job Title: "Founder, CEO"
   ├─ Seniority: "C-Suite"
   └─ Max Results: 50
   ↓
3. User clicks "Start Discovery"
   ↓
4. Discovery job is created & queued
   ↓
5. Progress indicator appears:
   ├─ "Step 1: Searching domains..."
   ├─ "Step 2: Crawling websites..."
   ├─ "Step 3: Extracting emails..."
   ├─ "Step 4: Enriching data..."
   └─ Progress: 15/50 leads found
   ↓
6. Frontend polls for status updates
   ├─ Every 2 seconds
   └─ Updates progress display
   ↓
7. Results appear as they're discovered:
   ├─ Person name
   ├─ Company
   ├─ Title
   ├─ Email (if found)
   ├─ LinkedIn profile
   └─ "Add to Leads" button
   ↓
8. User can:
   ├─ Click "Add to Leads" to import individual lead
   ├─ Select multiple leads
   └─ Click "Add All to Leads"
   ↓
9. Leads are saved to database
```

### Backend Flow (Detailed)

#### **Step 1-3: Discovery Job Creation**
```
File: backend/app/routes/lead_discovery.py

POST /api/lead-discovery/start
{
  "keywords": "SaaS founders",
  "location": "US",
  "industry": "B2B Software",
  "job_title": "Founder, CEO",
  "seniority": "c_suite",
  "max_results": 50
}

Process:
1. Validate request
2. Create LeadDiscoveryJob object:
   ├─ id: UUID
   ├─ user_id: current_user.id
   ├─ org_id: current_user.id
   ├─ keywords: "SaaS founders"
   ├─ location: "US"
   ├─ industry: "B2B Software"
   ├─ job_title: "Founder, CEO"
   ├─ seniority: "c_suite"
   ├─ status: "pending"
   ├─ domains_found: 0
   ├─ domains_crawled: 0
   ├─ leads_created: 0
   └─ created_at: now()
3. Save to database
4. Enqueue background task:
   └─ run_lead_discovery.delay(job_id, max_results=50)
5. Return job object with status: "pending"
```

#### **Step 4-7: Discovery Processing (Celery Worker)**

```
File: backend/app/workers/lead_discovery_worker.py

run_lead_discovery(job_id, max_results):

Phase 1: SEARCH FOR DOMAINS
──────────────────────────────
1. Update job status: "searching"
2. Use multiple search strategies (in priority order):
   
   Strategy 1: SerpAPI (Google Search)
   ├─ Query: "{keywords} {location} {industry}"
   ├─ Extract URLs from search results
   ├─ Example: techcrunch.com, medium.com, linkedin.com
   └─ Store in DiscoveredDomain table
   
   Strategy 2: ZenRows (Website Scraper)
   ├─ Use SerpAPI results
   ├─ Scrape each domain for email addresses
   ├─ Extract from footer, about page, contact page
   └─ Pattern matching for emails
   
   Strategy 3: Hunter.io API
   ├─ Domain verification
   ├─ Fetch emails for domain
   ├─ Return structured data
   └─ Cache results
   
   Strategy 4: Apollo.io API
   ├─ Advanced peopling search
   ├─ Filter by job title, seniority
   ├─ Return person records
   └─ Structure: first_name, last_name, email, company, title
   
   Strategy 5: Snov.io API
   ├─ Similar to Apollo
   ├─ Alternative coverage
   ├─ Different pricing tier
   └─ Used as fallback

3. For each domain found:
   ├─ Create DiscoveredDomain object:
   │  ├─ id: UUID
   │  ├─ job_id: job_id
   │  ├─ domain: "techcorp.com"
   │  ├─ source: "serpapi" / "hunter" / "apollo" / "snov"
   │  ├─ emails_found: ["john@techcorp.com", "jane@techcorp.com"]
   │  ├─ person: {first_name, last_name, title, company, email}
   │  ├─ company_description: JSON with metadata
   │  ├─ status: "found"
   │  └─ created_at: now()
   └─ Save to database
   
4. Update job:
   ├─ domains_found: count
   └─ Update: LeadDiscoveryJob.domains_found

Phase 2: CRAWL WEBSITES & EXTRACT EMAILS
────────────────────────────────────────────
1. Update job status: "crawling"
2. For each DiscoveredDomain:
   ├─ If email already found: Skip
   ├─ Otherwise:
   │  ├─ Crawl domain website (ZenRows / Selenium)
   │  ├─ Extract text from pages:
   │  │  ├─ /about
   │  │  ├─ /team
   │  │  ├─ /contact
   │  │  └─ /careers
   │  ├─ Pattern match for emails
   │  ├─ Pattern match for person names
   │  └─ Update DiscoveredDomain with findings
   │
   └─ Save to database

3. Update job:
   ├─ domains_crawled: count
   └─ Update: LeadDiscoveryJob.domains_crawled

Phase 3: ENRICH DATA & CREATE LEADS
──────────────────────────────────────
1. Update job status: "enriching"
2. For each DiscoveredDomain with email:
   ├─ Extract person data:
   │  ├─ first_name
   │  ├─ last_name
   │  ├─ title
   │  ├─ company
   │  ├─ email
   │  └─ source
   │
   ├─ Create Lead object:
   │  ├─ id: UUID
   │  ├─ user_id: current_user.id
   │  ├─ org_id: current_user.id
   │  ├─ first_name
   │  ├─ last_name
   │  ├─ full_name
   │  ├─ email (UNIQUE per user)
   │  ├─ company
   │  ├─ title
   │  ├─ source: "lead_discovery"
   │  ├─ source_url: domain
   │  ├─ enriched_data: {
   │  │   "seniority": "c_suite",
   │  │   "location": "US",
   │  │   "industry": "B2B Software",
   │  │   "discovered_via": "apollo",
   │  │   "confidence": 0.95
   │  │ }
   │  └─ created_at: now()
   │
   └─ Save to database (skip if email already exists)

3. Update job:
   ├─ leads_created: count
   ├─ status: "completed"
   └─ completed_at: now()
```

#### **Step 8-9: Frontend Status Polling & Result Display**

```
File: frontend/src/pages/DiscoverLeadsPage.jsx

Poll for updates every 2 seconds:

const pollStatus = setInterval(async () => {
  const response = await api.get(`/api/lead-discovery/${jobId}`)
  
  // Response:
  {
    "id": "job-uuid",
    "status": "crawling",
    "domains_found": 12,
    "domains_crawled": 5,
    "leads_created": 8,
    "discovered_domains": [
      {
        "id": "domain-uuid",
        "domain": "techcorp.com",
        "source": "apollo",
        "emails_found": "john@techcorp.com",
        "person": {
          "first_name": "John",
          "last_name": "Smith",
          "title": "CEO",
          "company": "TechCorp",
          "email": "john@techcorp.com",
          "seniority": "c_suite"
        },
        "status": "found"
      },
      // ... more domains
    ],
    "error_message": null,
    "created_at": "2024-01-15T10:00:00Z"
  }
  
  // Update UI:
  setJob(response.data)
  setProgress(`${response.data.leads_created}/${maxResults} leads`)
  setDiscoveredResults(response.data.discovered_domains)
  
}, 2000)

UI Display:
┌────────────────────────────────────────────┐
│ Discovering Leads...                       │
├────────────────────────────────────────────┤
│ ✓ Search domains: 12 found                 │
│ ⟳ Crawl websites: 5/12 completed          │
│ ○ Extract emails: 8 found                  │
│ ○ Enrich data                              │
│                                            │
│ Progress: 8/50 leads                       │
│ [Cancel]                                   │
└────────────────────────────────────────────┘

Results Section:
┌────────────────────────────────────────────┐
│ Found Leads (8 of 50)                      │
├────────────────────────────────────────────┤
│                                            │
│ 👤 John Smith                              │
│   CEO at TechCorp                          │
│   📧 john@techcorp.com                     │
│   🔗 LinkedIn  [+ Add to Leads]           │
│                                            │
│ 👤 Jane Doe                                │
│   VP Sales at TechCorp                     │
│   📧 jane@techcorp.com                     │
│   🔗 LinkedIn  [+ Add to Leads]           │
│                                            │
└────────────────────────────────────────────┘
```

#### **Step 10-11: Importing Leads**

```
File: frontend/src/pages/DiscoverLeadsPage.jsx

When user clicks "+ Add to Leads":

1. POST /leads (Create lead directly)
   {
     "first_name": "John",
     "last_name": "Smith",
     "email": "john@techcorp.com",
     "company": "TechCorp",
     "title": "CEO",
     "source": "lead_discovery",
     "enriched_data": {
       "seniority": "c_suite",
       "discovered_via": "apollo"
     }
   }

2. Backend creates Lead:
   ├─ Validate email is unique
   ├─ Create Lead object
   ├─ Save to database
   └─ Return lead object

3. Frontend shows confirmation:
   └─ Toast: "Lead added to your database"

When user clicks "Add All to Leads":

1. Get all discovered_domains
2. For each domain:
   ├─ Skip if email already exists
   ├─ POST /leads with domain data
   └─ Create Lead
3. Show batch result:
   └─ Toast: "Added 8 new leads"
```

### Database Schema
```
LeadDiscoveryJob Table:
├─ id: UUID (Primary Key)
├─ user_id: UUID (Foreign Key → Users)
├─ org_id: UUID (Foreign Key → Users)
├─ keywords: String
├─ location: String (Nullable)
├─ industry: String (Nullable)
├─ job_title: String (Nullable)
├─ seniority: String (Nullable)
├─ max_results: Integer
├─ status: String (pending, searching, crawling, enriching, completed, failed)
├─ domains_found: Integer
├─ domains_crawled: Integer
├─ leads_created: Integer
├─ error_message: String (Nullable)
├─ created_at: DateTime
├─ completed_at: DateTime (Nullable)
└─ updated_at: DateTime

DiscoveredDomain Table:
├─ id: UUID (Primary Key)
├─ job_id: UUID (Foreign Key → LeadDiscoveryJob)
├─ domain: String
├─ source: String (serpapi, hunter, apollo, snov, zenrows)
├─ emails_found: Array of Strings
├─ person: JSON {first_name, last_name, title, company, email, seniority}
├─ company_description: JSON (metadata)
├─ source_url: String (Nullable)
├─ status: String (found, crawled, enriched)
├─ created_at: DateTime
└─ updated_at: DateTime
```

---

## Page-by-Page Guide

### 1️⃣ **Login Page** (`/login`)
```
Purpose: User authentication

Flow:
1. User enters email & password
2. Frontend: POST /auth/login
3. Backend: Verify credentials → Return JWT token
4. Frontend: Store JWT in localStorage
5. Redirect to /leads

Frontend Components:
└─ src/pages/Login.jsx
   └─ Email input
   └─ Password input
   └─ Login button
   └─ Sign up link

Backend Endpoint:
└─ POST /auth/login
   ├─ Validates email exists
   ├─ Validates password hash
   ├─ Returns JWT token
   └─ Token includes: user_id, email, exp

Database:
└─ Users table
   ├─ id
   ├─ email
   └─ hashed_password (bcrypt)
```

### 2️⃣ **Signup Page** (`/signup`)
```
Purpose: User registration

Flow:
1. User enters email, password, confirm password
2. Frontend: Validate passwords match
3. Frontend: POST /auth/register
4. Backend: Hash password → Create user → Return success
5. Frontend: Redirect to /login

Frontend Components:
└─ src/pages/Signup.jsx
   └─ Email input
   └─ Password input
   └─ Confirm password input
   └─ Signup button
   └─ Login link

Backend Endpoint:
└─ POST /auth/register
   ├─ Validates email unique
   ├─ Validates password strength
   ├─ Hashes password (bcrypt)
   ├─ Creates User object
   ├─ Saves to database
   └─ Returns success message

Database:
└─ Users table (new row)
   ├─ id: UUID
   ├─ email: String (unique)
   ├─ hashed_password: String
   └─ created_at: DateTime
```

### 3️⃣ **Leads Page** (`/leads`)
```
Purpose: Manage individual leads

Features:
├─ View all leads in paginated table
├─ Search leads by name/email/company
├─ Create new lead (modal)
├─ Edit lead (modal)
├─ Delete lead (confirmation)
├─ Upload CSV (modal)
├─ Enrich lead with LinkedIn data
├─ Send individual email
├─ Add leads to campaign
└─ Select multiple leads

Frontend Components:
└─ src/pages/Leads.jsx
   ├─ Lead table
   ├─ Search bar
   ├─ Pagination controls
   ├─ CreateLeadModal.jsx
   ├─ EditLeadModal.jsx
   ├─ DeleteLeadModal.jsx
   ├─ CSVUploadModal.jsx
   ├─ EmailComposer.jsx
   └─ AddToCampaignModal.jsx

Backend Endpoints:
├─ GET /leads (List leads, paginated)
├─ POST /leads (Create lead)
├─ GET /leads/{id} (Get single lead)
├─ PUT /leads/{id} (Update lead)
├─ DELETE /leads/{id} (Delete lead)
├─ POST /leads/upload_csv (Bulk import)
└─ POST /leads/{id}/enrich (Enrich with LinkedIn)

Database:
└─ Leads table
   ├─ id
   ├─ user_id
   ├─ first_name, last_name, full_name
   ├─ email (unique per user)
   ├─ company
   ├─ title
   ├─ source (manual, csv, lead_discovery)
   ├─ enriched_data (JSONB)
   ├─ created_at
   └─ updated_at
```

### 4️⃣ **Campaigns Page** (`/campaigns`)
```
Purpose: View and manage email campaigns

Features:
├─ List all campaigns (with status, date)
├─ Create new campaign (name, description)
├─ Launch campaign (DRAFT → ACTIVE)
├─ Pause campaign (ACTIVE → PAUSED)
├─ Resume campaign (PAUSED → ACTIVE)
├─ Delete campaign
├─ View warmup status
├─ View sending limits

Frontend Components:
└─ src/pages/Campaigns.jsx
   ├─ Campaign cards
   ├─ Create campaign form
   ├─ Status badge (draft, active, paused)
   ├─ Launch button
   ├─ Pause button
   ├─ Delete button (with confirmation)
   └─ Warmup status alert

Backend Endpoints:
├─ GET /campaigns (List campaigns)
├─ POST /campaigns (Create campaign)
├─ GET /campaigns/{id} (Get campaign with steps)
├─ PUT /campaigns/{id} (Update campaign)
├─ DELETE /campaigns/{id} (Delete campaign)
├─ PUT /campaigns/{id}/launch (Activate campaign)
├─ PUT /campaigns/{id}/pause (Pause campaign)
├─ POST /campaigns/{id}/add-leads (Add leads)
└─ POST /campaigns/{id}/steps (Add sequence step)

Database:
└─ Campaigns table
   ├─ id
   ├─ user_id
   ├─ name
   ├─ description
   ├─ status
   ├─ created_at
   └─ updated_at
```

### 5️⃣ **Campaign Editor** (`/campaigns/{id}/edit`)
```
Purpose: Configure campaign sequence steps and leads

Features:
├─ View campaign details
├─ Add/edit/delete sequence steps
├─ Define email content for each step
├─ Set delay between steps (days)
├─ Add leads to campaign
├─ View campaign progress
├─ Remove leads from campaign
├─ View sending logs

Frontend Components:
└─ src/pages/CampaignEditor.jsx
   ├─ Campaign header (name, status)
   ├─ Sequence builder
   │  ├─ Step cards (draggable?)
   │  ├─ Subject input
   │  ├─ Body editor
   │  ├─ Delay input
   │  ├─ Add step button
   │  └─ Delete step button
   ├─ Leads section
   │  ├─ Lead list
   │  ├─ Add leads button (modal)
   │  └─ Remove lead option
   ├─ Progress stats
   │  ├─ Total leads
   │  ├─ Leads sent
   │  ├─ Leads pending
   │  └─ Campaign status
   └─ Launch button

Backend Endpoints:
├─ GET /campaigns/{id} (Get campaign + steps)
├─ POST /campaigns/{id}/steps (Create step)
├─ PUT /campaigns/{id}/steps/{step_id} (Update step)
├─ DELETE /campaigns/{id}/steps/{step_id} (Delete step)
├─ POST /campaigns/{id}/add-leads (Add leads)
├─ DELETE /campaigns/{id}/leads/{lead_id} (Remove lead)
└─ GET /campaigns/{id}/progress (Campaign status)

Database:
├─ Campaigns table
├─ SequenceSteps table
├─ CampaignLeads table
└─ SendingLogs table
```

### 6️⃣ **Discover Leads Page** (`/discover`)
```
Purpose: Find and import new leads using AI

Features:
├─ Search by keywords, location, industry
├─ Configure search parameters
├─ View real-time discovery progress
├─ See results as they're found
├─ Add individual leads to database
├─ Add all results at once
├─ View previous discovery jobs

Frontend Components:
└─ src/pages/DiscoverLeadsPage.jsx
   ├─ Search form
   │  ├─ Keywords input
   │  ├─ Location input
   │  ├─ Industry dropdown
   │  ├─ Job title input
   │  ├─ Seniority dropdown
   │  ├─ Max results slider
   │  └─ Start discovery button
   ├─ Progress indicator
   │  ├─ Status steps
   │  ├─ Progress bar
   │  └─ Count display
   ├─ Results section
   │  ├─ Person cards
   │  ├─ Email addresses
   │  ├─ LinkedIn links
   │  └─ Add to leads buttons
   └─ Recent jobs history

Backend Endpoints:
├─ POST /api/lead-discovery/start (Create job)
├─ GET /api/lead-discovery/{id} (Get job status)
├─ GET /api/lead-discovery (List recent jobs)
└─ POST /leads (Import found lead)

Workers:
└─ Celery: run_lead_discovery
   ├─ Phase 1: Search for domains
   ├─ Phase 2: Crawl websites
   ├─ Phase 3: Enrich data
   └─ Phase 4: Create leads

Database:
├─ LeadDiscoveryJob table
├─ DiscoveredDomain table
└─ Leads table (created during import)
```

### 7️⃣ **Settings Page** (`/settings`)
```
Purpose: Configure email provider and API keys

Features:
├─ Email provider selection (SMTP / SendGrid)
├─ SMTP settings
│  ├─ SMTP host
│  ├─ SMTP port
│  ├─ Username
│  ├─ Password (encrypted)
│  ├─ Use SSL/TLS
│  └─ From email & name
├─ SendGrid settings
│  ├─ API key (encrypted)
│  └─ From email & name
├─ Test email button
├─ API key management
├─ Webhook configuration
└─ Safety settings

Frontend Components:
└─ src/pages/Settings.jsx
   ├─ Email provider tabs
   ├─ SMTP form
   ├─ SendGrid form
   ├─ Test email section
   ├─ Webhook URL display
   ├─ Save settings button
   └─ Delete provider option

Backend Endpoints:
├─ GET /settings (Get current settings)
├─ POST /settings/smtp (Update SMTP)
├─ POST /settings/sendgrid (Update SendGrid)
├─ POST /email/send-test (Send test email)
├─ PUT /settings/webhook (Configure webhook)
└─ DELETE /settings/{provider} (Remove provider)

Database:
└─ EmailProviderSettings table
   ├─ id
   ├─ user_id
   ├─ provider (smtp / sendgrid)
   ├─ from_email
   ├─ from_name
   ├─ smtp_host (encrypted)
   ├─ smtp_port (encrypted)
   ├─ smtp_username (encrypted)
   ├─ smtp_password_encrypted
   ├─ sendgrid_api_key_encrypted
   ├─ use_ssl
   ├─ use_tls
   ├─ created_at
   └─ updated_at
```

### 8️⃣ **Deliverability Page** (`/deliverability`)
```
Purpose: Monitor email delivery and sender reputation

Features:
├─ View delivery metrics
│  ├─ Total sent
│  ├─ Delivered
│  ├─ Bounced
│  ├─ Spam/Complaints
│  └─ Delivery rate %
├─ Warmup status (21-day schedule)
├─ Daily sending limits
├─ Warning alerts
├─ Webhook setup guide
└─ SendGrid integration status

Frontend Components:
└─ src/pages/Deliverability.jsx
   ├─ Metrics dashboard
   ├─ Warmup day counter
   ├─ Daily limit progress
   ├─ Charts (delivery rate over time)
   ├─ Alerts section
   └─ Webhook configuration

Backend Endpoints:
├─ GET /metrics (Get delivery metrics)
├─ GET /warmup-status (Get warmup progress)
├─ GET /daily-limits (Get sending limits)
├─ POST /webhooks/sendgrid (Receive webhook)
└─ GET /sending-logs (Get email logs)

Database:
├─ SendingLogs table (for metrics)
├─ InboundEvents table (webhook data)
└─ OrgQuota table (daily limits)
```

### 9️⃣ **Metrics Dashboard** (`/metrics`)
```
Purpose: Analytics and performance tracking

Features:
├─ Campaign performance
├─ Lead conversion funnel
├─ Email open rates
├─ Click-through rates
├─ Response tracking
├─ Lead source attribution
└─ Time-based trends

Frontend Components:
└─ src/pages/MetricsDashboard.jsx
   ├─ KPI cards
   ├─ Charts & graphs
   ├─ Filtering options
   └─ Export data

Backend Endpoints:
├─ GET /metrics/campaigns (Campaign stats)
├─ GET /metrics/leads (Lead stats)
├─ GET /metrics/emails (Email stats)
└─ GET /metrics/export (Download data)

Database:
└─ SendingLogs table (derived analytics)
```

---

## Database Schema Summary

### Core Tables

```
Users
├─ id (UUID, PK)
├─ email (String, unique)
├─ hashed_password (String)
├─ created_at (DateTime)
└─ updated_at (DateTime)

Leads
├─ id (UUID, PK)
├─ user_id (UUID, FK → Users)
├─ first_name (String)
├─ last_name (String)
├─ full_name (String)
├─ email (String)
├─ company (String)
├─ title (String)
├─ source (String: manual, csv, lead_discovery)
├─ enriched_data (JSONB)
├─ created_at (DateTime)
└─ updated_at (DateTime)

Campaigns
├─ id (UUID, PK)
├─ user_id (UUID, FK → Users)
├─ name (String)
├─ description (String)
├─ status (Enum: draft, active, paused, completed)
├─ started_at (DateTime)
├─ created_at (DateTime)
└─ updated_at (DateTime)

SequenceSteps
├─ id (UUID, PK)
├─ campaign_id (UUID, FK → Campaigns)
├─ step_order (Integer)
├─ subject (String)
├─ body (String)
├─ delay_days (Integer)
├─ created_at (DateTime)
└─ updated_at (DateTime)

CampaignLeads
├─ id (UUID, PK)
├─ campaign_id (UUID, FK → Campaigns)
├─ lead_id (UUID, FK → Leads)
├─ status (Enum: pending, in_progress, completed, failed)
├─ current_step (Integer)
├─ last_step_sent_at (DateTime)
├─ created_at (DateTime)
└─ updated_at (DateTime)

SendingLogs
├─ id (UUID, PK)
├─ user_id (UUID, FK → Users)
├─ lead_id (UUID, FK → Leads)
├─ campaign_id (UUID, FK → Campaigns, nullable)
├─ to_email (String)
├─ subject (String)
├─ body (String)
├─ status (Enum: pending, sent, failed, bounced)
├─ provider (String: smtp, sendgrid)
├─ created_at (DateTime)
├─ sent_at (DateTime)
└─ error_message (String)

EmailProviderSettings
├─ id (UUID, PK)
├─ user_id (UUID, FK → Users)
├─ provider (String: smtp, sendgrid)
├─ from_email (String)
├─ from_name (String)
├─ smtp_host_encrypted (String)
├─ smtp_port_encrypted (String)
├─ smtp_username_encrypted (String)
├─ smtp_password_encrypted (String)
├─ sendgrid_api_key_encrypted (String)
├─ use_ssl (Boolean)
├─ use_tls (Boolean)
├─ created_at (DateTime)
└─ updated_at (DateTime)

LeadDiscoveryJob
├─ id (UUID, PK)
├─ user_id (UUID, FK → Users)
├─ org_id (UUID, FK → Users)
├─ keywords (String)
├─ location (String)
├─ industry (String)
├─ job_title (String)
├─ seniority (String)
├─ max_results (Integer)
├─ status (String: pending, searching, crawling, enriching, completed, failed)
├─ domains_found (Integer)
├─ domains_crawled (Integer)
├─ leads_created (Integer)
├─ error_message (String)
├─ created_at (DateTime)
├─ completed_at (DateTime)
└─ updated_at (DateTime)

DiscoveredDomain
├─ id (UUID, PK)
├─ job_id (UUID, FK → LeadDiscoveryJob)
├─ domain (String)
├─ source (String: serpapi, hunter, apollo, snov)
├─ emails_found (Array)
├─ person (JSONB)
├─ company_description (JSONB)
├─ source_url (String)
├─ status (String: found, crawled, enriched)
├─ created_at (DateTime)
└─ updated_at (DateTime)

InboundEvents (Webhooks)
├─ id (UUID, PK)
├─ user_id (UUID, FK → Users)
├─ sendgrid_event_id (String)
├─ event_type (String: bounce, open, click, unsubscribe)
├─ email (String)
├─ sending_log_id (UUID, FK → SendingLogs)
├─ payload (JSONB)
├─ created_at (DateTime)
└─ processed_at (DateTime)

OrgQuota
├─ id (UUID, PK)
├─ user_id (UUID, FK → Users)
├─ daily_limit (Integer)
├─ used_today (Integer)
├─ warmup_day (Integer: 1-21)
├─ reset_at (DateTime)
├─ created_at (DateTime)
└─ updated_at (DateTime)
```

---

## API Request/Response Examples

### Example 1: Send Individual Email

**Request:**
```bash
POST http://localhost:8000/email/send
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "lead_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "subject": "Let's connect - quick idea",
  "body": "Hi John,\n\nNoticed TechCorp is expanding into EMEA..."
}
```

**Response:**
```json
{
  "queued": true,
  "message": "Email queued for sending"
}
```

### Example 2: Create Campaign

**Request:**
```bash
POST http://localhost:8000/campaigns
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "Q2 2024 Founder Outreach",
  "description": "Target SaaS founders in US"
}
```

**Response:**
```json
{
  "id": "c4d5e6f7-a8b9-0123-cdef-4567890abcde",
  "user_id": "user-uuid",
  "name": "Q2 2024 Founder Outreach",
  "description": "Target SaaS founders in US",
  "status": "draft",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Example 3: Generate Email with AI

**Request:**
```bash
POST http://localhost:8000/generate-email
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "lead_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "tone": "professional",
  "goal": "introduce"
}
```

**Response:**
```json
{
  "subject": "Quick idea for TechCorp - email deliverability",
  "body": "Hi John,\n\nI noticed TechCorp recently raised Series B funding and is expanding their go-to-market operations.\n\nTeams like yours use our platform to monitor email deliverability in real-time and prevent getting stuck in spam folders.\n\nWould you be open to a brief 15-minute walkthrough?\n\nBest regards,\nAlex"
}
```

### Example 4: Start Lead Discovery

**Request:**
```bash
POST http://localhost:8000/api/lead-discovery/start
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "keywords": "SaaS founders",
  "location": "US",
  "industry": "B2B Software",
  "job_title": "Founder, CEO",
  "seniority": "c_suite",
  "max_results": 50
}
```

**Response:**
```json
{
  "id": "job-uuid-here",
  "user_id": "user-uuid",
  "status": "pending",
  "keywords": "SaaS founders",
  "location": "US",
  "industry": "B2B Software",
  "domains_found": 0,
  "domains_crawled": 0,
  "leads_created": 0,
  "created_at": "2024-01-15T10:35:00Z"
}
```

---

## Key Features & Implementation Details

### 🔒 Security
- **Password Hashing**: bcrypt with 12 rounds
- **JWT Tokens**: HS256 algorithm, 7-day expiration
- **Credential Encryption**: AES-256 for SMTP/SendGrid credentials
- **Rate Limiting**: Per-user, per-endpoint limits
- **CORS**: Configured for frontend origin only

### 🚀 Performance
- **Database Indexing**: On user_id, email, created_at
- **Pagination**: Default 20 items per page
- **Redis Caching**: Job status, quota tracking
- **Connection Pooling**: PostgreSQL connection pool (5-20 connections)
- **Async Processing**: All email sends via Celery workers

### 📊 Monitoring & Logging
- **Audit Logs**: All email sends logged
- **Error Tracking**: Failed sends with retry attempts
- **Webhook Events**: SendGrid bounce/open/click tracking
- **Performance Metrics**: Response time monitoring
- **Usage Analytics**: Campaign performance, delivery rates

### ⚠️ Safety Guardrails
- **Daily Limits**: Configurable per user (starts 10/day)
- **Warmup Schedule**: 21-day gradual increase
- **Bounce Monitoring**: Alert if >5% bounce rate
- **Spam Check**: Detect likely spam/complaint issues
- **Unsubscribe Tracking**: Automatic removal from future sends

---

## Common Workflows

### Workflow A: Quick Email to Single Lead
```
1. User: Navigate to Leads page
2. User: Click lead row
3. User: Click "Send Email"
4. User: Type subject & body (or use AI)
5. User: Click "Send"
6. System: Queue email via Celery
7. System: Send via SMTP/SendGrid
8. User: See success notification
⏱️ Total time: 1-2 minutes
```

### Workflow B: Create & Launch Campaign
```
1. User: Navigate to Campaigns
2. User: Click "New Campaign"
3. User: Enter name & description
4. User: Click "Create"
5. User: Click campaign to edit
6. User: Add sequence steps (3+ emails)
7. User: Save campaign
8. User: Click "Add Leads"
9. User: Select leads to add
10. User: Click "Add Selected"
11. User: Click "Launch Campaign"
12. System: Start processing campaign
13. System: Send first emails immediately
14. System: Schedule follow-ups
15. User: See campaign progress in real-time
⏱️ Total time: 5-10 minutes
```

### Workflow C: Discover & Import Leads
```
1. User: Navigate to Discover Leads
2. User: Enter search criteria (keywords, location, etc)
3. User: Click "Start Discovery"
4. System: Begin searching domains
5. System: Crawl websites
6. System: Extract emails
7. System: Enrich data
8. User: See results appear in real-time
9. User: Click "+ Add to Leads" for interesting leads
10. System: Add leads to database
11. User: Go to Leads page and verify
12. User: Add leads to campaign
⏱️ Total time: 5-15 minutes (+ discovery time 2-5 min)
```

---

This guide provides a complete picture of your app's architecture and user flows!
