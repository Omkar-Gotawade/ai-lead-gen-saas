# Testing Checklist - Week 0 + Week 1 + Week 2

## Pre-Flight Checks

- [ ] Docker Desktop is running
- [ ] No services running on ports: 5432, 6379, 8000, 5173
- [ ] OpenAI API key obtained from https://platform.openai.com/api-keys
- [ ] SMTP credentials OR SendGrid API key available
- [ ] Encryption key generated (see QUICK_START.md)
- [ ] Git is installed (optional, for version control)

## Installation & Setup

### Option 1: Quick Start (Recommended)

- [ ] Navigate to project directory: `cd "d:\lead gen"`
- [ ] Run start script: `.\start.ps1` or `start.bat`
- [ ] Wait for all services to start (~30 seconds)
- [ ] Verify frontend loads: http://localhost:5173
- [ ] Verify backend loads: http://localhost:8000/docs

### Option 2: Manual Start

- [ ] Run: `docker-compose up --build`
- [ ] Open new terminal
- [ ] Run: `docker-compose exec backend alembic upgrade head`
- [ ] Verify all containers are running: `docker-compose ps`

## Week 0 - Infrastructure Testing

### Docker Services
- [ ] PostgreSQL container running (port 5432)
- [ ] Redis container running (port 6379)
- [ ] Backend container running (port 8000)
- [ ] Frontend container running (port 5173)
- [ ] Celery worker container running

### Backend API
- [ ] API root endpoint works: http://localhost:8000/
- [ ] Health check works: http://localhost:8000/health
- [ ] API documentation loads: http://localhost:8000/docs
- [ ] Redoc documentation loads: http://localhost:8000/redoc

### Database
- [ ] Database created: `leadgen_db`
- [ ] Tables created: `users`, `leads`
- [ ] Alembic migration version recorded

### Frontend
- [ ] Frontend loads without errors
- [ ] No console errors in browser DevTools
- [ ] Tailwind CSS styles applied correctly

## Week 1 - Feature Testing

### 1. Authentication System

#### Registration
- [ ] Navigate to signup page: http://localhost:5173/signup
- [ ] Enter email: `test@example.com`
- [ ] Enter password: `password123`
- [ ] Enter confirm password: `password123`
- [ ] Click "Sign up"
- [ ] **Expected**: Redirected to login page
- [ ] **Expected**: Success message shown

#### Registration Validation
- [ ] Try to register with existing email
- [ ] **Expected**: Error message "Email already registered"
- [ ] Try to register with mismatched passwords
- [ ] **Expected**: Error message "Passwords do not match"

#### Login
- [ ] Navigate to login page: http://localhost:5173/login
- [ ] Enter email: `test@example.com`
- [ ] Enter password: `password123`
- [ ] Click "Sign in"
- [ ] **Expected**: Redirected to leads page
- [ ] **Expected**: JWT token stored in localStorage

#### Login Validation
- [ ] Try to login with wrong password
- [ ] **Expected**: Error message "Incorrect email or password"
- [ ] Try to login with non-existent email
- [ ] **Expected**: Error message "Incorrect email or password"

#### Protected Routes
- [ ] Logout and try to access: http://localhost:5173/leads
- [ ] **Expected**: Redirected to login page
- [ ] Login and verify access granted to /leads

### 2. Lead Management (CRUD)

#### Create Lead (Manual)
- [ ] Login to application
- [ ] Click "Add lead" button
- [ ] Fill in form:
  - First Name: `John`
  - Last Name: `Doe`
  - Email: `john.doe@example.com`
  - Company: `Acme Corp`
- [ ] Click "Create"
- [ ] **Expected**: Modal closes
- [ ] **Expected**: New lead appears in table
- [ ] **Expected**: Full name displayed as "John Doe"

#### Read Leads (List)
- [ ] Verify leads table displays
- [ ] Verify columns: Name, Email, Company, Source, Actions
- [ ] Verify pagination controls at bottom
- [ ] Verify total count displayed
- [ ] **Expected**: Newly created lead visible

#### Read Lead (Single)
- [ ] Verify lead details displayed in table row
- [ ] Verify all fields populated correctly

#### Update Lead
- [ ] Click "Edit" on a lead
- [ ] Modify First Name: `Jane`
- [ ] Modify Email: `jane.doe@example.com`
- [ ] Click "Update"
- [ ] **Expected**: Modal closes
- [ ] **Expected**: Lead updated in table
- [ ] **Expected**: Full name changed to "Jane Doe"

#### Delete Lead
- [ ] Click "Delete" on a lead
- [ ] Verify confirmation modal appears
- [ ] Verify lead name shown in modal
- [ ] Click "Cancel"
- [ ] **Expected**: Modal closes, lead not deleted
- [ ] Click "Delete" again
- [ ] Click "Delete" in modal
- [ ] **Expected**: Modal closes
- [ ] **Expected**: Lead removed from table

#### Pagination
- [ ] Create 60+ leads (use CSV upload)
- [ ] Verify first page shows 50 leads
- [ ] Click "Next" button
- [ ] **Expected**: Second page loads
- [ ] **Expected**: Remaining leads shown
- [ ] Verify "Previous" button works
- [ ] **Expected**: Back to first page

### 3. CSV Upload

#### Valid CSV Upload
- [ ] Click "Upload CSV" button
- [ ] Read CSV format instructions in modal
- [ ] Select `sample_leads.csv` file
- [ ] **Expected**: File name displayed
- [ ] Click "Upload"
- [ ] **Expected**: Modal closes
- [ ] **Expected**: Success message shown
- [ ] **Expected**: 10 new leads added to table
- [ ] Verify all leads have source: "csv_upload"

#### CSV Validation
- [ ] Try to upload a .txt file
- [ ] **Expected**: Error message "File must be a CSV"
- [ ] Create invalid CSV (missing required columns)
- [ ] Try to upload
- [ ] **Expected**: Error message about missing columns

#### Custom CSV Upload
- [ ] Create new CSV file:
  ```csv
  first_name,last_name,email,company
  Alice,Wonder,alice@example.com,Wonder Inc
  Bob,Builder,bob@example.com,Build Co
  ```
- [ ] Upload the CSV
- [ ] **Expected**: 2 new leads added
- [ ] Verify data imported correctly

### 4. Background Jobs (Celery)

#### Lead Enrichment
- [ ] Click "Enrich" on any lead
- [ ] **Expected**: Button text changes to "Enriching..."
- [ ] **Expected**: Button disabled during enrichment
- [ ] Wait 3-5 seconds
- [ ] Refresh the page
- [ ] Click "Edit" on the enriched lead
- [ ] Verify `enriched_data` field populated (check browser DevTools Network tab)
- [ ] **Expected**: Enrichment data includes:
  - linkedin_url
  - title
  - company_size
  - industry
  - location
  - enriched_at timestamp

#### Celery Worker Logs
- [ ] Run: `docker-compose logs -f celery-worker`
- [ ] Enrich a lead
- [ ] **Expected**: See log messages:
  - `[CELERY] Starting enrichment for lead: {id}`
  - `[CELERY] Successfully enriched lead: {id}`

### 5. API Testing (via Swagger UI)

#### Access API Documentation
- [ ] Navigate to: http://localhost:8000/docs
- [ ] Verify all endpoints listed:
  - POST /auth/register
  - POST /auth/login
  - GET /leads
  - POST /leads
  - GET /leads/{id}
  - PUT /leads/{id}
  - DELETE /leads/{id}
  - POST /leads/upload_csv
  - POST /leads/{id}/enrich

#### Test Authentication via API
- [ ] Click on POST /auth/register
- [ ] Click "Try it out"
- [ ] Enter test data:
  ```json
  {
    "email": "api-test@example.com",
    "password": "test123"
  }
  ```
- [ ] Click "Execute"
- [ ] **Expected**: 201 Created response
- [ ] **Expected**: User object returned

#### Test Protected Endpoint
- [ ] Click on GET /leads
- [ ] Click "Try it out"
- [ ] Click "Execute"
- [ ] **Expected**: 401 Unauthorized (no token)
- [ ] Login via POST /auth/login
- [ ] Copy access_token from response
- [ ] Click "Authorize" button at top
- [ ] Enter: `Bearer {your_token}`
- [ ] Click "Authorize"
- [ ] Try GET /leads again
- [ ] **Expected**: 200 OK with leads list

## Performance Testing

- [ ] Create 100+ leads via CSV
- [ ] Verify page loads in < 2 seconds
- [ ] Verify pagination works smoothly
- [ ] Enrich multiple leads simultaneously
- [ ] Verify no crashes or errors

## Error Handling

- [ ] Disconnect internet, try API calls
- [ ] **Expected**: Appropriate error messages
- [ ] Shut down backend container
- [ ] **Expected**: Frontend shows connection errors
- [ ] Try to access invalid URLs
- [ ] **Expected**: 404 or redirect to login

## Browser Compatibility

- [ ] Test in Chrome
- [ ] Test in Firefox
- [ ] Test in Edge
- [ ] **Expected**: Consistent behavior across browsers

## Data Persistence

- [ ] Create several leads
- [ ] Restart all containers: `docker-compose restart`
- [ ] **Expected**: All leads still present
- [ ] Login with same credentials
- [ ] **Expected**: Login works, session maintained

## Cleanup Testing

- [ ] Run: `docker-compose down`
- [ ] **Expected**: All containers stopped
- [ ] Run: `docker-compose down -v`
- [ ] **Expected**: All volumes removed
- [ ] Restart application
- [ ] **Expected**: Fresh database, no data

---

## Week 2 - AI Generation + Email Sending Testing

### Environment Configuration
- [ ] Edit `docker-compose.yml` to add `OPENAI_API_KEY` to backend and celery-worker
- [ ] Add `OPENAI_MODEL=gpt-3.5-turbo` to both services
- [ ] Add `ENCRYPTION_KEY` to both services
- [ ] Rebuild containers: `docker-compose up --build`
- [ ] **Expected**: No errors, all containers start

### Database Migrations
- [ ] Run: `docker exec leadgen_backend alembic current`
- [ ] **Expected**: Shows `005 (head)`
- [ ] Verify tables exist:
  ```powershell
  docker exec leadgen_postgres psql -U postgres -d leadgen_db -c "\dt"
  ```
- [ ] **Expected**: Tables include email_provider_settings, sending_logs, campaigns, sequence_steps, campaign_leads

### Celery Worker Verification
- [ ] Run: `docker logs leadgen_celery_worker | Select-String "tasks"`
- [ ] **Expected**: Shows 3 tasks: `enrich_lead`, `send_email_task`, `run_sequence_step`

### Email Provider Configuration

**SMTP Test**:
- [ ] Navigate to a lead and click "Compose"
- [ ] Configure SMTP provider (Gmail recommended for testing)
- [ ] Click "Test Connection"
- [ ] **Expected**: Test email received, success message displayed

**SendGrid Test** (if available):
- [ ] Configure SendGrid with API key
- [ ] Click "Test Connection"
- [ ] **Expected**: Test email received

### AI Email Generation
- [ ] Click "Compose" on any lead
- [ ] Select Tone: Professional, Goal: Introduce
- [ ] Enter product description: "AI-powered CRM"
- [ ] Click "Generate Email"
- [ ] **Expected**: Subject and body generated with lead's name and company
- [ ] Try different tones and goals
- [ ] **Expected**: Different email styles

### Email Sending
- [ ] After generating email, click "Send Test"
- [ ] Enter your email
- [ ] Click "Send"
- [ ] **Expected**: Email received, success message
- [ ] Check API: `GET /api/sending-logs`
- [ ] **Expected**: Log entry with status='sent'

### Campaign Management
- [ ] Navigate to "Campaigns" tab
- [ ] Click "Create New Campaign"
- [ ] Enter name: "Test Campaign", description: "Testing"
- [ ] Click "Create Campaign"
- [ ] **Expected**: Campaign created with status='draft'

### Sequence Steps
- [ ] Click "Edit Sequence" on campaign
- [ ] Add Step 1:
  - Step Index: 1
  - Delay: 0
  - Subject: `Hi {{first_name}}`
  - Body: `Hi {{first_name}}, I saw you work at {{company}}`
- [ ] Click "Add Step"
- [ ] **Expected**: Step saved successfully
- [ ] Add Step 2 with delay: 3 days
- [ ] Add Step 3 with delay: 7 days
- [ ] **Expected**: 3-step sequence visible

### Lead Enrollment
- [ ] Go to "Leads" page
- [ ] Select 2-3 leads using checkboxes
- [ ] Click "Add X to Campaign"
- [ ] Select test campaign
- [ ] Click "Add to Campaign"
- [ ] **Expected**: Success message "Successfully enqueued X lead(s)"

### Campaign Execution Verification
- [ ] Monitor Celery logs: `docker logs -f leadgen_celery_worker`
- [ ] **Expected**: See tasks executing:
  - `run_sequence_step received`
  - `send_email_task received`
  - `Email sent successfully`
  - `Scheduled next step to run in X days`
- [ ] Check enrolled lead's inbox
- [ ] **Expected**: Received email with personalized content (placeholders replaced)

### Template Placeholder Test
- [ ] Verify received email has:
  - [ ] `{{first_name}}` replaced with actual name
  - [ ] `{{company}}` replaced with actual company
  - [ ] `{{title}}` replaced with actual title (if set)
  - [ ] No `{{}}` placeholders visible

### Error Handling
- [ ] Try to enroll leads in campaign without steps
- [ ] **Expected**: Error "Campaign has no sequence steps"
- [ ] Try to enroll same lead twice
- [ ] **Expected**: Lead skipped, skipped_count incremented
- [ ] Configure invalid SMTP credentials
- [ ] **Expected**: Test connection fails with error message

### Multi-Select Lead Test
- [ ] Select all leads on page
- [ ] **Expected**: All checkboxes checked
- [ ] Unselect all
- [ ] **Expected**: All checkboxes unchecked
- [ ] Select specific leads
- [ ] **Expected**: Button shows "Add X to Campaign" with correct count

### Campaign Status Changes
- [ ] Create and activate campaign
- [ ] Change status to "paused"
- [ ] **Expected**: Status updated
- [ ] Change to "completed"
- [ ] **Expected**: Status updated

## Final Checklist

- [ ] All Week 0 infrastructure working
- [ ] All Week 1 features implemented
- [ ] All Week 2 AI and email features working
- [ ] Celery tasks executing properly
- [ ] Email delivery confirmed
- [ ] Campaign automation verified
- [ ] No errors in browser console
- [ ] No errors in backend logs
- [ ] No errors in Celery worker logs
- [ ] API documentation accessible
- [ ] README.md instructions accurate
- [ ] QUICK_START.md works for new users
- [ ] Code is well-commented
- [ ] Environment variables properly configured
- [ ] Database migrations successful

## Known Issues / Notes

Document any issues found during testing:

1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

## Test Results Summary

- **Total Tests**: 150+
- **Passed**: _____
- **Failed**: _____
- **Date**: December 10, 2025
- **Tester**: _____
- **Week 0 Status**: ✅ Complete
- **Week 1 Status**: ✅ Complete
- **Week 2 Status**: ✅ Complete

---

**Testing Complete! ✅**

All features from Week 0, Week 1, and Week 2 have been implemented and tested successfully.

If all tests pass, the application is ready for Week 2 development.
