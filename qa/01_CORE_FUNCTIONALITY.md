# 🧪 Core Functionality Test Cases

**Category:** Manual QA - Current Features Only  
**Priority:** P0 (Launch Blockers)  
**Estimated Time:** 4 hours

---

## 1️⃣ AUTHENTICATION

### TC-AUTH-001: User Signup
**Priority:** P0  
**Preconditions:** No existing account  

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Navigate to `/signup` | Signup form displays |
| 2 | Enter: email, name, password | Fields accept input |
| 3 | Click "Sign Up" | Account created, redirected to dashboard |
| 4 | Check DB | User record exists in `users` table |

**Failure Indicators:** Error message, no redirect, duplicate account  
**Severity:** 🔴 Critical - blocks all functionality

---

### TC-AUTH-002: User Login
**Priority:** P0  
**Preconditions:** Valid user account exists

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Navigate to `/login` | Login form displays |
| 2 | Enter valid credentials | No error |
| 3 | Click "Login" | JWT token received, redirected to `/` |
| 4 | Check localStorage | `token` stored |
| 5 | Refresh page | Still logged in (token valid) |

**Failure Indicators:** Invalid credentials error, no token, redirect to login  
**Severity:** 🔴 Critical

---

### TC-AUTH-003: User Logout
**Priority:** P0  
**Preconditions:** User logged in

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Click user menu → Logout | Logged out |
| 2 | Check localStorage | Token removed |
| 3 | Navigate to `/leads` | Redirected to `/login` |

**Failure Indicators:** Token persists, can access protected routes  
**Severity:** 🔴 Critical - security risk

---

### TC-AUTH-004: Password Reset Flow
**Priority:** P1  
**Preconditions:** Valid user account

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Click "Forgot Password" | Reset form displays |
| 2 | Enter email | "Check email" message |
| 3 | Check email inbox | Reset link received (if configured) |
| 4 | Click reset link | Password reset form |
| 5 | Enter new password | Password updated |
| 6 | Login with new password | Success |

**Failure Indicators:** No email sent, link expired, password not updated  
**Severity:** 🟡 Medium - workaround exists (admin reset)

---

### TC-AUTH-005: Invalid Login Attempts
**Priority:** P1  
**Preconditions:** Valid account exists

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Enter wrong password | "Invalid credentials" error |
| 2 | Enter non-existent email | "Invalid credentials" error (same message) |
| 3 | Leave fields empty | Validation error |
| 4 | Try 5 wrong passwords | No account lockout (not implemented yet) |

**Failure Indicators:** Different error messages leak user existence, login succeeds  
**Severity:** 🟠 High - security concern

---

### TC-AUTH-006: Token Expiration
**Priority:** P1  
**Preconditions:** User logged in

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Wait for token expiry (24h) | Token expires |
| 2 | Try API request | 401 Unauthorized |
| 3 | Frontend detects 401 | Redirect to login |

**Failure Indicators:** Expired token still works, no redirect  
**Severity:** 🟠 High - security risk

---

### TC-AUTH-007: Protected Route Access
**Priority:** P0  
**Preconditions:** Not logged in

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Navigate to `/leads` | Redirect to `/login` |
| 2 | Navigate to `/campaigns` | Redirect to `/login` |
| 3 | Try `/api/leads` | 401 Unauthorized |

**Failure Indicators:** Can access protected routes without auth  
**Severity:** 🔴 Critical - security breach

---

### TC-AUTH-008: CORS & API Security
**Priority:** P1  
**Preconditions:** Backend running

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Try API from external origin | CORS headers present |
| 2 | Try `/api/health` without auth | 200 OK (public) |
| 3 | Try `/api/leads` without auth | 401 Unauthorized |

**Failure Indicators:** CORS errors in browser, unprotected endpoints  
**Severity:** 🟠 High

---

## 2️⃣ LEADS MANAGEMENT

### TC-LEAD-001: Manual Lead Creation
**Priority:** P0  
**Preconditions:** Logged in

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Navigate to `/leads` | Leads page loads |
| 2 | Click "Add Lead" | Create modal opens |
| 3 | Enter: email, name, company | Fields accept input |
| 4 | Click "Save" | Lead created, modal closes |
| 5 | Check table | New lead appears |
| 6 | Check DB | Lead in `leads` table with correct `org_id` |

**Failure Indicators:** Lead not saved, wrong org_id, duplicate allowed  
**Severity:** 🔴 Critical

---

### TC-LEAD-002: Email Validation
**Priority:** P0  
**Preconditions:** On lead create form

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Enter invalid email: "notanemail" | Validation error |
| 2 | Enter: "test@" | Validation error |
| 3 | Enter: "@example.com" | Validation error |
| 4 | Enter valid: "test@example.com" | No error |
| 5 | Leave email empty | Validation error (required) |

**Failure Indicators:** Invalid emails accepted, valid emails rejected  
**Severity:** 🔴 Critical - data corruption

---

### TC-LEAD-003: CSV Import Success
**Priority:** P0  
**Preconditions:** Valid CSV file with 100 leads

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Navigate to `/leads` | Page loads |
| 2 | Click "Import CSV" | File picker opens |
| 3 | Select CSV file | Upload starts |
| 4 | Wait for processing | Progress indicator |
| 5 | Check success message | "100 leads imported" |
| 6 | Check leads table | 100 new leads appear |
| 7 | Check DB count | `SELECT COUNT(*) FROM leads` matches |

**Failure Indicators:** Import fails, partial import, duplicate leads  
**Severity:** 🔴 Critical - main data entry method

---

### TC-LEAD-004: CSV Duplicate Prevention
**Priority:** P0  
**Preconditions:** 50 leads already in DB

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Create CSV with 50 existing + 50 new emails | File ready |
| 2 | Import CSV | Upload completes |
| 3 | Check message | "50 new leads imported, 50 duplicates skipped" |
| 4 | Check DB | Only 50 new records added |
| 5 | Verify no duplicates | `SELECT email, COUNT(*) GROUP BY email` all=1 |

**Failure Indicators:** Duplicates inserted, import fails entirely  
**Severity:** 🔴 Critical - data integrity

---

### TC-LEAD-005: CSV Malformed Data Handling
**Priority:** P0  
**Preconditions:** CSV with errors

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Create CSV with invalid emails | "test@", "notanemail", etc. |
| 2 | Import CSV | Upload completes |
| 3 | Check message | "X valid leads imported, Y skipped (invalid email)" |
| 4 | Check DB | Only valid leads inserted |
| 5 | Download error report | List of skipped rows with reasons |

**Failure Indicators:** Invalid data inserted, entire import fails  
**Severity:** 🟠 High - user experience

---

### TC-LEAD-006: Lead Edit
**Priority:** P1  
**Preconditions:** Lead exists

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Click lead row | Details/edit form |
| 2 | Change name field | Field updates |
| 3 | Click "Save" | Update persists |
| 4 | Refresh page | Changes still there |
| 5 | Check DB | `updated_at` timestamp changed |

**Failure Indicators:** Changes lost, wrong lead updated  
**Severity:** 🟡 Medium

---

### TC-LEAD-007: Lead Delete
**Priority:** P1  
**Preconditions:** Lead exists, not in active campaign

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Select lead | Checkbox checked |
| 2 | Click "Delete" | Confirm dialog |
| 3 | Confirm deletion | Lead removed from UI |
| 4 | Check DB | Lead marked deleted or removed |

**Failure Indicators:** Lead still visible, DB corruption  
**Severity:** 🟡 Medium

---

### TC-LEAD-008: Do-Not-Contact Enforcement
**Priority:** P0  
**Preconditions:** Lead marked `do_not_contact=true`

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Open campaign editor | Load page |
| 2 | Try to add DNC lead to campaign | Error or lead filtered out |
| 3 | Check campaign_leads table | DNC lead NOT added |
| 4 | Try manual send to DNC lead | Blocked with error message |

**Failure Indicators:** DNC lead added to campaign, email sent  
**Severity:** 🔴 Critical - legal/compliance risk

---

### TC-LEAD-009: Bounce Marks DNC
**Priority:** P0  
**Preconditions:** Lead in active campaign

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Send email to lead | Email queued |
| 2 | Simulate bounce webhook | POST to `/api/webhooks/sendgrid` with bounce event |
| 3 | Check lead record | `do_not_contact=true`, `bounced_at` set |
| 4 | Check campaign_lead | Status = `stopped`, `stop_reason='bounced'` |
| 5 | Try adding to new campaign | Blocked |

**Failure Indicators:** DNC not set, can add to campaigns, email sent again  
**Severity:** 🔴 Critical - deliverability risk

---

### TC-LEAD-010: Lead Search/Filter
**Priority:** P1  
**Preconditions:** 100+ leads in DB

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Enter email in search | Filtered results |
| 2 | Filter by company | Only matching leads show |
| 3 | Filter by status (DNC) | Only DNC leads show |
| 4 | Clear filters | All leads visible |

**Failure Indicators:** Search doesn't work, wrong results  
**Severity:** 🟡 Medium - usability issue

---

### TC-LEAD-011: Lead Tags
**Priority:** P2  
**Preconditions:** Lead exists

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Add tag to lead | Tag saved |
| 2 | Filter by tag | Tagged leads show |
| 3 | Remove tag | Tag removed |

**Failure Indicators:** Tags don't save, filter broken  
**Severity:** ⚪ Low - nice-to-have

---

### TC-LEAD-012: Pagination
**Priority:** P1  
**Preconditions:** 500+ leads

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Load leads page | First 50 show |
| 2 | Click "Next" | Next 50 show |
| 3 | Navigate to page 5 | Correct offset |
| 4 | Check URL | Page param present |

**Failure Indicators:** All leads load at once (slow), pagination broken  
**Severity:** 🟡 Medium - performance issue

---

## 3️⃣ LEAD DISCOVERY

### TC-DISC-001: Manual Domain Discovery
**Priority:** P0  
**Preconditions:** Logged in, discovery feature enabled

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Navigate to `/discover` | Discovery page loads |
| 2 | Enter domain: "example.com" | Field accepts input |
| 3 | Click "Discover Leads" | Scan starts |
| 4 | Wait for completion | Progress shows |
| 5 | Check results | Contact emails found |
| 6 | Click "Approve & Add" | Leads added to main list |
| 7 | Check DB | Leads in `leads` table |

**Failure Indicators:** Scan hangs, no results, leads not added  
**Severity:** 🔴 Critical - key feature

---

### TC-DISC-002: SERP Discovery
**Priority:** P0  
**Preconditions:** SERP API key configured

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Enter search query: "SaaS CEO email" | Query accepted |
| 2 | Click "Search" | SERP job starts |
| 3 | Wait for results | Domains/emails found |
| 4 | Results show preview | Can see before importing |
| 5 | Select results to import | Checkbox selection |
| 6 | Click "Add to Leads" | Leads imported |

**Failure Indicators:** SERP fails, no results, import fails  
**Severity:** 🟠 High - major feature

---

### TC-DISC-003: Discovery Duplicate Handling
**Priority:** P0  
**Preconditions:** 10 leads already exist

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Discover domain with existing leads | Scan completes |
| 2 | Check results | Duplicates marked/filtered |
| 3 | Try to import duplicates | Skipped or error |
| 4 | Check DB | No duplicate emails |

**Failure Indicators:** Duplicates imported, data corruption  
**Severity:** 🔴 Critical - data integrity

---

### TC-DISC-004: Invalid Domain Handling
**Priority:** P1  
**Preconditions:** Discovery page

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Enter: "notadomain" | Validation error or graceful failure |
| 2 | Enter: "http://example.com" | Auto-clean to "example.com" |
| 3 | Enter: "example.com:8080" | Handle port correctly |
| 4 | Enter: "localhost" | Error (invalid for discovery) |

**Failure Indicators:** Invalid domains accepted, scan crashes  
**Severity:** 🟡 Medium

---

### TC-DISC-005: Empty Discovery Results
**Priority:** P1  
**Preconditions:** Domain with no contacts

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Discover domain with no emails | Scan completes |
| 2 | Check results | "No contacts found" message |
| 3 | No error thrown | Graceful handling |

**Failure Indicators:** Error thrown, UI breaks  
**Severity:** 🟡 Medium

---

### TC-DISC-006: Discovery Timeout
**Priority:** P1  
**Preconditions:** Slow/unreachable domain

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Discover slow domain | Scan starts |
| 2 | Wait 60 seconds | Timeout triggered |
| 3 | Check status | "Timed out" or partial results |
| 4 | Can retry | Try again works |

**Failure Indicators:** Hangs forever, no timeout, browser crash  
**Severity:** 🟠 High - user experience

---

### TC-DISC-007: Partial Failure (Multi-Domain)
**Priority:** P1  
**Preconditions:** Batch discovery with 5 domains

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Add 5 domains (2 invalid, 3 valid) | All queued |
| 2 | Start batch scan | All attempted |
| 3 | Check results | 3 succeeded, 2 failed with reasons |
| 4 | Import successful results | Only valid leads added |

**Failure Indicators:** Entire batch fails, no error detail  
**Severity:** 🟠 High

---

### TC-DISC-008: Captcha/Blocked Domain
**Priority:** P2  
**Preconditions:** Domain with bot protection

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Discover protected domain | Scan starts |
| 2 | Hit captcha/block | Detected |
| 3 | Check status | "Unable to access - protected" |
| 4 | User notified | Clear error message |

**Failure Indicators:** Crash, infinite retry, unclear error  
**Severity:** 🟡 Medium

---

### TC-DISC-009: 404 Page Crawl
**Priority:** P2  
**Preconditions:** Domain returns 404

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Discover domain that 404s | Scan attempts |
| 2 | Check result | "Page not found" |
| 3 | No crash | Graceful handling |

**Failure Indicators:** Error thrown, scan hangs  
**Severity:** 🟡 Medium

---

### TC-DISC-010: Discovery Approval Workflow
**Priority:** P0  
**Preconditions:** Discovery results ready

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Complete discovery | Results in "pending" state |
| 2 | Review results | Can see before adding to leads |
| 3 | Uncheck unwanted leads | Selection persists |
| 4 | Click "Approve & Add" | Only selected leads imported |
| 5 | Check leads table | Correct leads added |

**Failure Indicators:** Auto-imported without approval, all leads added  
**Severity:** 🟠 High - user control

---

## 4️⃣ COMPANY ENRICHMENT

### TC-ENRICH-001: AI Enrichment Success
**Priority:** P1  
**Preconditions:** Lead with company name, Gemini API key configured

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Create lead with company name | Lead saved |
| 2 | Trigger enrichment (manual or auto) | Enrichment job starts |
| 3 | Wait for completion | AI populates: industry, title, description |
| 4 | Check lead record | Fields updated |
| 5 | Verify data quality | Reasonable values (not gibberish) |

**Failure Indicators:** Enrichment fails, gibberish data, fields empty  
**Severity:** 🟡 Medium - feature enhancement

---

### TC-ENRICH-002: Enrichment Missing Company
**Priority:** P1  
**Preconditions:** Lead with no company name

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Create lead without company | Lead saved |
| 2 | Trigger enrichment | Skipped or attempted with email domain |
| 3 | Check result | Gracefully handled, no error |

**Failure Indicators:** Error thrown, enrichment crashes  
**Severity:** 🟡 Medium

---

### TC-ENRICH-003: API Key Missing
**Priority:** P1  
**Preconditions:** No Gemini API key configured

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Trigger enrichment | Job fails gracefully |
| 2 | Check error message | "API key not configured" |
| 3 | Lead still exists | No data corruption |

**Failure Indicators:** Silent failure, lead deleted, crash  
**Severity:** 🟡 Medium

---

### TC-ENRICH-004: Rate Limit Handling
**Priority:** P2  
**Preconditions:** Gemini API rate limited

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Trigger many enrichments | Hit rate limit |
| 2 | Check behavior | Retry with backoff |
| 3 | Eventually succeeds | Data updated |

**Failure Indicators:** Permanent failure, no retry  
**Severity:** 🟡 Medium

---

### TC-ENRICH-005: Timeout Handling
**Priority:** P1  
**Preconditions:** Slow API response

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Trigger enrichment | Request sent |
| 2 | API slow to respond | Timeout after 30s |
| 3 | Check status | "Timed out" or retry queued |
| 4 | Lead data intact | No corruption |

**Failure Indicators:** Hangs forever, lead corrupted  
**Severity:** 🟡 Medium

---

### TC-ENRICH-006: Enrichment Doesn't Block Sends
**Priority:** P0  
**Preconditions:** Lead in campaign, enrichment pending

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Add lead to campaign | Lead added |
| 2 | Start campaign | Sends even if enrichment incomplete |
| 3 | Check sending_logs | Email sent |
| 4 | Enrichment completes later | Updates lead asynchronously |

**Failure Indicators:** Send blocked by enrichment, campaign stuck  
**Severity:** 🔴 Critical - sending must not block

---

## 5️⃣ CAMPAIGNS & SEQUENCES

### TC-CAMP-001: Create Campaign
**Priority:** P0  
**Preconditions:** Logged in

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Navigate to `/campaigns` | Page loads |
| 2 | Click "New Campaign" | Editor opens |
| 3 | Enter name, subject line | Fields accept input |
| 4 | Add email body | Rich text works |
| 5 | Click "Save Draft" | Campaign saved |
| 6 | Check DB | Campaign in `campaigns` table, status=`draft` |

**Failure Indicators:** Campaign not saved, fields lost  
**Severity:** 🔴 Critical

---

### TC-CAMP-002: Add Leads to Campaign
**Priority:** P0  
**Preconditions:** Campaign exists (draft), 10 leads exist

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Open campaign editor | Page loads |
| 2 | Click "Add Leads" | Lead selector opens |
| 3 | Select 10 leads | Checkboxes work |
| 4 | Click "Add" | Leads added |
| 5 | Check campaign_leads table | 10 rows created, status=`queued` |

**Failure Indicators:** Leads not added, duplicates, wrong campaign_id  
**Severity:** 🔴 Critical

---

### TC-CAMP-003: Multi-Step Sequence
**Priority:** P0  
**Preconditions:** Campaign editor

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Click "Add Step" | New step created |
| 2 | Set delay: 3 days | Delay saved |
| 3 | Enter step 2 subject/body | Content saved |
| 4 | Click "Add Step" | Step 3 created |
| 5 | Check DB | 3 rows in `sequence_steps` table |
| 6 | Reorder steps (drag/drop) | Order updated |

**Failure Indicators:** Steps not saved, wrong order, delays lost  
**Severity:** 🔴 Critical - core feature

---

### TC-CAMP-004: Schedule Campaign
**Priority:** P1  
**Preconditions:** Campaign with leads

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Open campaign | Loaded |
| 2 | Click "Schedule" | Schedule modal opens |
| 3 | Set start time: tomorrow 9 AM | Time accepted |
| 4 | Set daily limit: 50 | Limit saved |
| 5 | Click "Confirm" | Campaign status → `scheduled` |
| 6 | Check at scheduled time | Sends start |

**Failure Indicators:** Sends immediately, time ignored, wrong timezone  
**Severity:** 🟠 High

---

### TC-CAMP-005: Activate Campaign
**Priority:** P0  
**Preconditions:** Campaign with leads (draft)

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Open campaign | Loaded |
| 2 | Click "Activate" | Confirmation dialog |
| 3 | Confirm | Campaign status → `active` |
| 4 | Check Celery queue | Send tasks queued |
| 5 | Wait 30 seconds | Emails start sending |
| 6 | Check sending_logs | Entries created |

**Failure Indicators:** Campaign not activated, tasks not queued, no sends  
**Severity:** 🔴 Critical

---

### TC-CAMP-006: Pause Campaign
**Priority:** P0  
**Preconditions:** Active campaign

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Click "Pause" | Campaign status → `paused` |
| 2 | Check Celery | No new sends queued |
| 3 | Check campaign_leads | In-progress leads stay in queue |
| 4 | Resume campaign | Sends continue from pause point |

**Failure Indicators:** Can't pause, sends continue, resume fails  
**Severity:** 🟠 High

---

### TC-CAMP-007: Stop Campaign
**Priority:** P1  
**Preconditions:** Active campaign

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Click "Stop" | Confirmation required |
| 2 | Confirm | Campaign status → `stopped` |
| 3 | Check Celery | All queued tasks cancelled |
| 4 | Check campaign_leads | Remaining leads → `stopped` |
| 5 | Try to resume | Cannot resume (permanent stop) |

**Failure Indicators:** Sends continue, can't stop, tasks not cancelled  
**Severity:** 🟠 High

---

### TC-CAMP-008: Campaign Statistics
**Priority:** P1  
**Preconditions:** Campaign with sent emails

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | View campaign details | Stats display |
| 2 | Check sent count | Matches sending_logs |
| 3 | Check delivered count | Matches webhook events |
| 4 | Check reply count | Matches reply webhooks |
| 5 | Check bounce count | Matches bounce webhooks |

**Failure Indicators:** Wrong counts, stats don't update  
**Severity:** 🟡 Medium - user visibility

---

### TC-CAMP-009: Duplicate Campaign
**Priority:** P2  
**Preconditions:** Campaign exists

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Click "Duplicate" | Copy created |
| 2 | Check new campaign | Name = "Copy of [Original]", status=`draft` |
| 3 | Sequence steps copied | Same steps exist |
| 4 | Leads NOT copied | campaign_leads empty |

**Failure Indicators:** Duplication fails, leads included  
**Severity:** ⚪ Low - convenience feature

---

### TC-CAMP-010: Delete Draft Campaign
**Priority:** P1  
**Preconditions:** Draft campaign exists

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Click "Delete" | Confirmation required |
| 2 | Confirm | Campaign deleted |
| 3 | Check DB | Campaign removed or soft-deleted |
| 4 | Check campaign_leads | Related rows cleaned up |

**Failure Indicators:** Can't delete, orphan records  
**Severity:** 🟡 Medium

---

### TC-CAMP-011: Cannot Delete Active Campaign
**Priority:** P1  
**Preconditions:** Active campaign

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Try to delete | Error: "Must stop first" |
| 2 | Stop campaign | Status → `stopped` |
| 3 | Now try delete | Success |

**Failure Indicators:** Can delete active campaign, data loss  
**Severity:** 🟠 High - safety control

---

### TC-CAMP-012: Sequence Step Timing
**Priority:** P0  
**Preconditions:** 2-step sequence with 2-day delay

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Activate campaign | Step 1 sends immediately |
| 2 | Check campaign_leads | `current_step=1`, `next_step_at` = now + 2 days |
| 3 | Wait 2 days | Step 2 queued |
| 4 | Check sending_logs | Step 2 sent |
| 5 | Check timestamps | 2-day gap between steps |

**Failure Indicators:** Step 2 sends immediately, timing wrong  
**Severity:** 🔴 Critical - sequence logic

---

### TC-CAMP-013: Reply Stops Sequence
**Priority:** P0  
**Preconditions:** Lead in 3-step sequence, step 1 sent

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Simulate reply webhook | POST reply event |
| 2 | Check campaign_lead | Status → `stopped`, `stop_reason='reply_received'` |
| 3 | Wait for step 2 timing | Step 2 NOT sent |
| 4 | Check sending_logs | Only step 1 sent |

**Failure Indicators:** Sequence continues, step 2 sent after reply  
**Severity:** 🔴 Critical - user expectation, best practice

---

### TC-CAMP-014: Bounce Stops Sequence
**Priority:** P0  
**Preconditions:** Lead in sequence, step 1 bounced

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Simulate bounce webhook | POST bounce event |
| 2 | Check lead | `do_not_contact=true` |
| 3 | Check campaign_lead | Status → `stopped`, `stop_reason='bounced'` |
| 4 | Remaining steps | NOT sent |

**Failure Indicators:** Sequence continues, step 2 sent  
**Severity:** 🔴 Critical - deliverability protection

---

### TC-CAMP-015: Campaign Lead Status Transitions
**Priority:** P1  
**Preconditions:** Campaign with leads

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Add lead to campaign | Status = `queued` |
| 2 | Send starts | Status = `in_progress` |
| 3 | Email sent | Status = `completed` (if 1-step) or stays `in_progress` |
| 4 | If multi-step | Status = `in_progress` until last step |
| 5 | Last step sent | Status = `completed` |

**Failure Indicators:** Wrong status, stuck in `queued`  
**Severity:** 🟡 Medium - status tracking

---

## 6️⃣ SENDING FLOW

### TC-SEND-001: Basic Email Send (SMTP)
**Priority:** P0  
**Preconditions:** SMTP configured, campaign active

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Activate campaign with 1 lead | Send task queued |
| 2 | Celery worker processes | Email sent via SMTP |
| 3 | Check sending_logs | Status = `sent` |
| 4 | Check recipient inbox | Email received |

**Failure Indicators:** Send fails, status stuck, email not received  
**Severity:** 🔴 Critical - core functionality

---

### TC-SEND-002: Basic Email Send (SendGrid)
**Priority:** P0  
**Preconditions:** SendGrid configured

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Activate campaign | Send via SendGrid API |
| 2 | Check response | 202 Accepted |
| 3 | Check sending_logs | `message_id` from SendGrid |
| 4 | Check SendGrid dashboard | Email sent |

**Failure Indicators:** API error, no message_id, email not sent  
**Severity:** 🔴 Critical

---

### TC-SEND-003: Warm-up Limit Enforcement
**Priority:** P0  
**Preconditions:** User has warm-up limit = 10/day

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Campaign with 50 leads | Campaign activated |
| 2 | Check sends | Only 10 sent on day 1 |
| 3 | Check quota table | 10/10 used |
| 4 | Try to send more | Blocked until tomorrow |
| 5 | Next day | 10 more sent |

**Failure Indicators:** All 50 sent immediately, limit ignored  
**Severity:** 🔴 Critical - deliverability safety

---

### TC-SEND-004: Daily Quota Enforcement
**Priority:** P0  
**Preconditions:** Quota = 100/day

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Send 100 emails | All sent |
| 2 | Check quota | 100/100 |
| 3 | Try to send 101st | Blocked |
| 4 | Check sending_logs | Status = `failed`, reason = `quota_exceeded` |
| 5 | Midnight UTC passes | Quota resets to 0/100 |
| 6 | Can send again | Success |

**Failure Indicators:** Over-limit sends, quota not reset  
**Severity:** 🔴 Critical - account safety

---

### TC-SEND-005: DNC Lead Send Blocked
**Priority:** P0  
**Preconditions:** Lead with `do_not_contact=true`

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Try to add to campaign | Prevented at UI |
| 2 | Try via API | 400 Bad Request |
| 3 | Manually insert into campaign_leads | Send task skips lead |
| 4 | Check sending_logs | No entry for DNC lead |

**Failure Indicators:** Email sent to DNC lead  
**Severity:** 🔴 Critical - compliance/reputation

---

### TC-SEND-006: Personalization Tokens
**Priority:** P1  
**Preconditions:** Campaign with {{first_name}} token

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Email body: "Hi {{first_name}}" | Template saved |
| 2 | Send to lead with first_name="John" | Email sent |
| 3 | Check received email | Body = "Hi John" |
| 4 | Send to lead with no first_name | Graceful fallback (empty or default) |

**Failure Indicators:** Token not replaced, literal {{first_name}} in email  
**Severity:** 🟠 High - user experience

---

### TC-SEND-007: From Name & Email
**Priority:** P1  
**Preconditions:** Email provider configured

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Set from: "Sales Team <sales@example.com>" | Saved |
| 2 | Send email | Email sent |
| 3 | Check received email | From = "Sales Team <sales@example.com>" |

**Failure Indicators:** Wrong from address, defaults used  
**Severity:** 🟡 Medium

---

### TC-SEND-008: Reply-To Header
**Priority:** P1  
**Preconditions:** Reply-to configured

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Set reply-to: "replies@example.com" | Saved |
| 2 | Send email | Header included |
| 3 | Recipient clicks reply | Goes to replies@example.com |

**Failure Indicators:** Reply goes to from address instead  
**Severity:** 🟡 Medium

---

### TC-SEND-009: HTML Email Rendering
**Priority:** P1  
**Preconditions:** Campaign with HTML content

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Compose email with bold, links, etc. | HTML saved |
| 2 | Send email | HTML email sent |
| 3 | Check received email | Formatting preserved |
| 4 | Check plain-text fallback | Plain version exists |

**Failure Indicators:** HTML broken, no plain-text  
**Severity:** 🟡 Medium

---

### TC-SEND-010: Retry Failed Sends
**Priority:** P1  
**Preconditions:** SMTP temporarily down

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Send email | Fails |
| 2 | Check sending_logs | Status = `failed` |
| 3 | Celery retry logic | Retries after delay |
| 4 | SMTP back up | Send succeeds |
| 5 | Check status | Updated to `sent` |

**Failure Indicators:** No retry, permanent failure  
**Severity:** 🟠 High - reliability

---

### TC-SEND-011: SMTP Connection Reuse
**Priority:** P2  
**Preconditions:** Many emails queued

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Send 100 emails | Batch processing |
| 2 | Check SMTP logs | Connection pooled (not 100 connections) |
| 3 | Performance | Fast (< 30 seconds) |

**Failure Indicators:** New connection per email, very slow  
**Severity:** 🟡 Medium - performance

---

### TC-SEND-012: Send Task Idempotency
**Priority:** P0  
**Preconditions:** Campaign active

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Send task queued | Task ID generated |
| 2 | Duplicate task queued (same lead) | Detected |
| 3 | Check behavior | Only sent once |
| 4 | Check sending_logs | Single entry |

**Failure Indicators:** Duplicate emails sent  
**Severity:** 🔴 Critical - user experience, reputation

---

### TC-SEND-013: Tracking Pixels (Opens)
**Priority:** P1  
**Preconditions:** SendGrid or tracking enabled

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Send email | Tracking pixel included |
| 2 | Recipient opens email | Pixel loaded |
| 3 | Webhook received | `open` event |
| 4 | Check campaign stats | Open count incremented |

**Failure Indicators:** Opens not tracked, webhook missing  
**Severity:** 🟡 Medium - analytics

---

### TC-SEND-014: Link Tracking (Clicks)
**Priority:** P1  
**Preconditions:** SendGrid click tracking enabled

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Email with link | Link rewritten for tracking |
| 2 | Recipient clicks | Redirect tracked |
| 3 | Webhook received | `click` event |
| 4 | Check stats | Click count incremented |

**Failure Indicators:** Clicks not tracked, link broken  
**Severity:** 🟡 Medium

---

### TC-SEND-015: Unsubscribe Link
**Priority:** P1  
**Preconditions:** Email includes unsubscribe link

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Send email | Unsubscribe link included |
| 2 | Recipient clicks link | Opens unsubscribe page |
| 3 | Confirm unsubscribe | Lead marked `do_not_contact=true` |
| 4 | Check DB | DNC set |
| 5 | Try to send again | Blocked |

**Failure Indicators:** Unsubscribe doesn't work, can send after unsubscribe  
**Severity:** 🔴 Critical - compliance (CAN-SPAM)

---

### TC-SEND-016: Bounce Handling
**Priority:** P0  
**Preconditions:** Email to invalid address

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Send to "invalid@nonexistentdomain.xyz" | Send attempted |
| 2 | Bounce received | Webhook or SMTP error |
| 3 | Check lead | `do_not_contact=true`, `bounced_at` set |
| 4 | Check campaign_lead | Stopped |

**Failure Indicators:** Bounce ignored, lead not marked DNC  
**Severity:** 🔴 Critical - deliverability

---

### TC-SEND-017: Reply Detection
**Priority:** P0  
**Preconditions:** Email sent, recipient replies

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Recipient replies | Reply email sent |
| 2 | Webhook received | `reply` or `inbound` event |
| 3 | Check campaign_lead | Status → `stopped`, `reply_received` |
| 4 | Check lead | `replied_at` timestamp set |
| 5 | Sequence stops | No more emails sent |

**Failure Indicators:** Reply not detected, sequence continues  
**Severity:** 🔴 Critical - user expectation

---

### TC-SEND-018: Provider Failover (If Multiple)
**Priority:** P2  
**Preconditions:** SMTP + SendGrid configured

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Primary provider fails | Send fails |
| 2 | Retry logic | Switches to secondary |
| 3 | Send succeeds | Email delivered |
| 4 | Check sending_logs | Provider used logged |

**Failure Indicators:** No failover, permanent failure  
**Severity:** 🟡 Medium - reliability (if multi-provider)

---

## 7️⃣ DELIVERABILITY TOOLS

### TC-DELIV-001: DNS Checker - Valid Records
**Priority:** P1  
**Preconditions:** Domain with SPF, DKIM, DMARC

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Navigate to Deliverability | Page loads |
| 2 | Enter domain: "example.com" | Domain accepted |
| 3 | Click "Check DNS" | Scan starts |
| 4 | Check SPF | ✅ Valid SPF record found |
| 5 | Check DKIM | ✅ Valid DKIM record found |
| 6 | Check DMARC | ✅ Valid DMARC record found |

**Failure Indicators:** False negatives, records not detected  
**Severity:** 🟡 Medium - guidance tool

---

### TC-DELIV-002: DNS Checker - Missing Records
**Priority:** P1  
**Preconditions:** Domain without DNS records

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Check domain without SPF | ⚠️ "No SPF record" |
| 2 | Check recommendations | Shows how to add SPF |

**Failure Indicators:** False positive, unclear guidance  
**Severity:** 🟡 Medium

---

### TC-DELIV-003: DNS Checker - Multiple SPF
**Priority:** P2  
**Preconditions:** Domain with 2 SPF records

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Check domain | Scan completes |
| 2 | Check SPF | ⚠️ "Multiple SPF records (invalid)" |
| 3 | Guidance shown | Merge into one record |

**Failure Indicators:** Not detected, shown as valid  
**Severity:** 🟡 Medium

---

### TC-DELIV-004: DNS Checker - Subdomain
**Priority:** P2  
**Preconditions:** Sending from subdomain

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Check "mail.example.com" | Scan starts |
| 2 | Check SPF | Checks subdomain first, then root |
| 3 | Result accurate | Subdomain vs root handled correctly |

**Failure Indicators:** Wrong domain checked  
**Severity:** 🟡 Medium

---

### TC-DELIV-005: Warm-up Schedule Display
**Priority:** P1  
**Preconditions:** Warm-up schedule configured

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Navigate to Deliverability | Page loads |
| 2 | Check warm-up section | Schedule displayed (Day 1: 10, Day 2: 15, etc.) |
| 3 | Current day highlighted | Shows progress |

**Failure Indicators:** Schedule not shown, wrong day  
**Severity:** 🟡 Medium - user guidance

---

### TC-DELIV-006: Quota Display
**Priority:** P1  
**Preconditions:** User sent emails today

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | View Deliverability | Quota widget shows |
| 2 | Check count | "45/100 sent today" |
| 3 | Progress bar | Visual indicator |
| 4 | Reset time shown | "Resets in 8 hours" |

**Failure Indicators:** Wrong count, no reset time  
**Severity:** 🟡 Medium

---

### TC-DELIV-007: Bounce Rate Warning
**Priority:** P1  
**Preconditions:** High bounce rate (>5%)

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | View Deliverability | Warning displayed |
| 2 | Check message | "High bounce rate detected (8%)" |
| 3 | Recommendations | Suggests cleaning list |

**Failure Indicators:** No warning, threshold wrong  
**Severity:** 🟡 Medium

---

### TC-DELIV-008: Spam Complaint Alert
**Priority:** P1  
**Preconditions:** Spam complaints received

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | View Deliverability | Alert shown |
| 2 | Check details | "3 spam complaints in last 7 days" |
| 3 | Leads listed | Shows which leads complained |

**Failure Indicators:** Not detected, no alert  
**Severity:** 🟠 High - reputation risk

---

## ✅ TEST COMPLETION CRITERIA

### Must Pass (P0)
- 100% of P0 tests passing
- No data corruption scenarios
- No authentication bypasses
- No duplicate sends
- DNC enforcement 100% effective

### Should Pass (P1)
- 95%+ of P1 tests passing
- Known issues documented
- Workarounds available

### Nice to Pass (P2)
- Best effort
- Can defer to post-launch

---

**Next:** [Failure Scenarios →](./02_FAILURE_SCENARIOS.md)
