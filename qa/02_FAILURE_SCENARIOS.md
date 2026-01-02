# 🧩 Failure & Edge-Case Test Scenarios

**Category:** Simulated Failures & System Resilience  
**Priority:** P0-P1 (Production Safety)  
**Estimated Time:** 3 hours

---

## 🎯 Testing Philosophy

These tests validate that the system **fails gracefully** under adverse conditions:
- No data corruption
- Clear error messages
- Automatic recovery where possible
- No silent failures

---

## 1️⃣ EMAIL PROVIDER FAILURES

### TC-FAIL-001: SMTP Disconnect Mid-Campaign
**Priority:** P0  
**Severity:** 🔴 Critical if not handled

#### How to Simulate
```bash
# During active campaign:
# 1. Stop SMTP server or block port 587
sudo iptables -A OUTPUT -p tcp --dport 587 -j DROP
# OR disconnect network temporarily
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Campaign sending emails | Initial sends succeed |
| 2 | Disconnect SMTP | Connection lost |
| 3 | Next send attempts | Task fails with connection error |
| 4 | Check Celery retry | Task retries with exponential backoff |
| 5 | Check sending_logs | Status = `failed`, error logged |
| 6 | Restore SMTP | Connection resumes |
| 7 | Retry logic | Failed sends retry and succeed |

**Impact on User:** Temporary delay, emails eventually sent  
**Rollback:** Failed tasks auto-retry, no manual intervention needed

**Failure Indicators:**
- ❌ Tasks stuck in queue forever
- ❌ No retry attempt
- ❌ Silent failure (no error logged)
- ❌ Duplicate sends after reconnect

---

### TC-FAIL-002: Invalid SMTP Credentials
**Priority:** P0  
**Severity:** 🔴 Critical

#### How to Simulate
```python
# In Settings → Email Provider:
# Change SMTP password to wrong value
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Configure wrong SMTP password | Saved |
| 2 | Try to send email | Auth fails |
| 3 | Check error message | "SMTP authentication failed" |
| 4 | User notification | Clear error in UI |
| 5 | Campaign status | Remains active but not sending |
| 6 | Fix credentials | Update settings |
| 7 | Retry | Sends resume |

**Impact on User:** No emails sent until fixed, clear error  
**Rollback:** Update credentials, no data loss

**Failure Indicators:**
- ❌ Silent failure
- ❌ Unclear error message
- ❌ Campaign marked failed permanently

---

### TC-FAIL-003: SendGrid Rate Limit
**Priority:** P1  
**Severity:** 🟠 High

#### How to Simulate
```bash
# Send burst of 100 emails through SendGrid
# If free tier, hits rate limit quickly
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Send many emails quickly | Initial sends succeed |
| 2 | Hit SendGrid rate limit | 429 Too Many Requests |
| 3 | Check response handling | Error caught |
| 4 | Celery retry logic | Waits before retry |
| 5 | Eventually succeeds | All emails sent |

**Impact on User:** Delayed sending, but completes  
**Rollback:** Automatic via retry

**Failure Indicators:**
- ❌ No retry, permanent failure
- ❌ Rate limit not detected
- ❌ Keeps hammering API (bad)

---

### TC-FAIL-004: Provider API Timeout
**Priority:** P1  
**Severity:** 🟡 Medium

#### How to Simulate
```python
# Mock SendGrid API with delayed response
import time
@mock.patch('sendgrid.SendGridAPIClient.send')
def mock_send(*args):
    time.sleep(35)  # Timeout is 30s
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Send email | API call starts |
| 2 | API hangs | Timeout after 30s |
| 3 | Check error | TimeoutError caught |
| 4 | Task retries | Queued for retry |

**Impact on User:** Delayed send  
**Rollback:** Automatic retry

---

## 2️⃣ WORKER (CELERY) FAILURES

### TC-FAIL-005: Celery Worker Restart
**Priority:** P0  
**Severity:** 🔴 Critical

#### How to Simulate
```bash
# During active campaign with queued tasks:
docker-compose restart backend
# OR
docker-compose stop backend && sleep 10 && docker-compose start backend
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Campaign active, 50 tasks queued | Workers processing |
| 2 | Restart worker | Graceful shutdown |
| 3 | Tasks in-progress | Saved to Redis (not lost) |
| 4 | Worker restarts | Reconnects to Redis |
| 5 | Tasks resume | Picks up from queue |
| 6 | Check campaign_leads | No duplicates, correct status |

**Impact on User:** Brief delay, no data loss  
**Rollback:** Automatic

**Failure Indicators:**
- ❌ Tasks lost
- ❌ Duplicate sends
- ❌ Campaign stuck
- ❌ Status corruption

---

### TC-FAIL-006: Redis Connection Lost
**Priority:** P0  
**Severity:** 🔴 Critical

#### How to Simulate
```bash
docker-compose stop redis
# Wait 30 seconds
docker-compose start redis
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Campaign active | Celery connected to Redis |
| 2 | Stop Redis | Connection lost |
| 3 | Worker behavior | Retries connection |
| 4 | Task queue | Persists to disk (Redis RDB) |
| 5 | Restart Redis | Workers reconnect |
| 6 | Tasks resume | No loss |

**Impact on User:** Sending paused during outage  
**Rollback:** Automatic recovery

**Failure Indicators:**
- ❌ Tasks lost
- ❌ Worker crashes
- ❌ No reconnection attempt

---

### TC-FAIL-007: Duplicate Task Prevention
**Priority:** P0  
**Severity:** 🔴 Critical

#### How to Simulate
```python
# Manually queue same task twice:
from app.workers.campaign_worker import send_campaign_email
send_campaign_email.apply_async(args=[lead_id, campaign_id])
send_campaign_email.apply_async(args=[lead_id, campaign_id])  # Duplicate
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Queue duplicate task | Both queued |
| 2 | Worker processes first | Email sent |
| 3 | Worker gets second | Idempotency check |
| 4 | Check sending_logs | Detects already sent |
| 5 | Second task | Skips send |

**Impact on User:** No duplicate emails  
**Rollback:** N/A (prevention)

**Failure Indicators:**
- ❌ Duplicate emails sent
- ❌ No idempotency check

---

### TC-FAIL-008: Task Timeout
**Priority:** P1  
**Severity:** 🟡 Medium

#### How to Simulate
```python
# Celery task with timeout:
@celery.task(time_limit=300)  # 5 minutes
def slow_task():
    time.sleep(400)  # Exceeds limit
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Task runs too long | Timeout triggered |
| 2 | Task killed | SoftTimeLimitExceeded |
| 3 | Check status | Marked failed |
| 4 | Retry logic | May retry or mark permanent fail |

**Impact on User:** Task fails, may need manual retry  
**Rollback:** Manual intervention

---

## 3️⃣ DATABASE FAILURES

### TC-FAIL-009: DB Connection Lost
**Priority:** P0  
**Severity:** 🔴 Critical

#### How to Simulate
```bash
docker-compose stop postgres
sleep 30
docker-compose start postgres
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | DB connection active | API works |
| 2 | Stop postgres | Connection lost |
| 3 | API request | 500 Internal Server Error |
| 4 | SQLAlchemy pool | Retry logic |
| 5 | Start postgres | Connection restored |
| 6 | Next request | Succeeds |

**Impact on User:** API unavailable during outage  
**Rollback:** Automatic

**Failure Indicators:**
- ❌ Permanent failure
- ❌ No reconnection
- ❌ App crash

---

### TC-FAIL-010: Transaction Rollback
**Priority:** P0  
**Severity:** 🔴 Critical

#### How to Simulate
```python
# In campaign creation:
# Cause error after partial insert
db.add(campaign)  # Succeeds
db.flush()
raise Exception("Simulated error")  # Before commit
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Create campaign | Start transaction |
| 2 | Error occurs mid-transaction | Exception raised |
| 3 | SQLAlchemy rollback | Transaction rolled back |
| 4 | Check DB | No partial data |
| 5 | User sees error | Clear message |

**Impact on User:** Operation fails, but clean state  
**Rollback:** Automatic

**Failure Indicators:**
- ❌ Partial data committed
- ❌ Orphan records
- ❌ Data corruption

---

### TC-FAIL-011: Migration Failure
**Priority:** P1  
**Severity:** 🟠 High

#### How to Simulate
```bash
# Create breaking migration:
# alembic revision --autogenerate -m "breaking"
# Edit to have syntax error
alembic upgrade head
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Run migration | Error thrown |
| 2 | Check DB state | Migration not applied |
| 3 | Fix migration | Edit file |
| 4 | Re-run | Succeeds |

**Impact on User:** Deployment blocked until fixed  
**Rollback:** Fix migration, re-run

---

## 4️⃣ SAFETY CONTROL FAILURES

### TC-FAIL-012: Lead Imported Twice (Race Condition)
**Priority:** P0  
**Severity:** 🔴 Critical

#### How to Simulate
```python
# Parallel CSV imports with same emails:
import threading
def import_csv_1():
    # Import CSV A with email1@example.com
def import_csv_2():
    # Import CSV B with email1@example.com
threading.Thread(target=import_csv_1).start()
threading.Thread(target=import_csv_2).start()
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Start two imports | Both running |
| 2 | Both try to insert same email | DB unique constraint |
| 3 | One succeeds, one fails | Only one inserted |
| 4 | Error handling | Graceful failure |
| 5 | Check DB | No duplicates |

**Impact on User:** One import may show partial failure  
**Rollback:** Manual dedup if needed

**Failure Indicators:**
- ❌ Duplicate emails in DB
- ❌ Race condition not handled

---

### TC-FAIL-013: Campaign Run on Blocked Lead
**Priority:** P0  
**Severity:** 🔴 Critical

#### How to Simulate
```python
# 1. Add lead to campaign (status=queued)
# 2. Mark lead do_not_contact=True
# 3. Worker tries to send
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Lead in campaign queue | Ready to send |
| 2 | Lead marked DNC | `do_not_contact=true` |
| 3 | Send task runs | Checks DNC status |
| 4 | Send blocked | Task skips lead |
| 5 | Check sending_logs | No entry or status=`blocked` |

**Impact on User:** Email not sent (correct)  
**Rollback:** N/A

**Failure Indicators:**
- ❌ Email sent to DNC lead
- ❌ No DNC check

---

### TC-FAIL-014: Bounce After Reply
**Priority:** P1  
**Severity:** 🟡 Medium

#### How to Simulate
```python
# 1. Send email to lead
# 2. Receive reply webhook
# 3. Receive bounce webhook (delayed)
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Email sent | Success |
| 2 | Reply received | Lead marked replied |
| 3 | Bounce received (delayed) | Both events logged |
| 4 | Check lead status | Replied takes precedence (positive signal) |
| 5 | Lead usable in future | Not marked DNC |

**Impact on User:** Reply status preserved  
**Rollback:** N/A

**Failure Indicators:**
- ❌ Reply overwritten by bounce
- ❌ Lead marked DNC incorrectly

---

### TC-FAIL-015: CSV with Malformed Emails
**Priority:** P1  
**Severity:** 🟡 Medium

#### How to Simulate
```csv
email,name,company
"John Doe",john@example.com,Acme  ← Wrong column order
notanemail,Jane Doe,Beta
test@@example.com,Bob,Gamma
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Upload CSV | Parsing starts |
| 2 | Detect malformed rows | Validation errors |
| 3 | Check result | Valid rows imported, invalid skipped |
| 4 | Error report | Shows which rows failed & why |

**Impact on User:** Partial import, clear feedback  
**Rollback:** N/A

**Failure Indicators:**
- ❌ Invalid data imported
- ❌ Entire import fails
- ❌ No error details

---

## 5️⃣ DELIVERABILITY EDGE CASES

### TC-FAIL-016: No DNS Records
**Priority:** P1  
**Severity:** 🟡 Medium

#### How to Simulate
```bash
# Check domain with no DNS:
# brandnewdomain12345.com (unregistered)
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Run DNS checker | Query starts |
| 2 | No records found | Timeout or NXDOMAIN |
| 3 | Result shown | "No DNS records found" |
| 4 | User guidance | "Domain not configured for email" |

**Impact on User:** Clear error, guidance provided  
**Rollback:** N/A

---

### TC-FAIL-017: Multiple SPF Records
**Priority:** P2  
**Severity:** 🟡 Medium

#### How to Simulate
```bash
# Add two SPF TXT records to domain:
# v=spf1 include:_spf.google.com ~all
# v=spf1 include:spf.sendgrid.net ~all
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | DNS check | Finds both records |
| 2 | Validation | Flags as invalid |
| 3 | User warning | "Multiple SPF records detected (RFC violation)" |
| 4 | Recommendation | "Merge into one record" |

**Impact on User:** Deliverability guidance  
**Rollback:** N/A

---

### TC-FAIL-018: Subdomain vs Root Domain SPF
**Priority:** P2  
**Severity:** 🟡 Medium

#### How to Simulate
```bash
# Send from: sales@mail.example.com
# SPF record exists on example.com but not mail.example.com
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Check mail.example.com | Query subdomain |
| 2 | No SPF found | Check parent domain |
| 3 | Find example.com SPF | Show result |
| 4 | Guidance | "Using parent domain SPF" |

**Impact on User:** Informational  
**Rollback:** N/A

---

## 6️⃣ DISCOVERY FAILURES

### TC-FAIL-019: Captcha'd Domain
**Priority:** P2  
**Severity:** 🟡 Medium

#### How to Simulate
```python
# Try to scrape linkedin.com or similar
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Start discovery | HTTP request |
| 2 | Captcha returned | HTML contains challenge |
| 3 | Detection | Recognized as captcha |
| 4 | User message | "Domain protected by captcha" |
| 5 | Graceful failure | No crash |

**Impact on User:** Discovery fails, clear reason  
**Rollback:** N/A

---

### TC-FAIL-020: Empty Website Content
**Priority:** P2  
**Severity:** 🟡 Medium

#### How to Simulate
```bash
# Scrape domain with no content:
# example.com (default Apache page)
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Scrape website | HTML retrieved |
| 2 | Parse content | No emails found |
| 3 | Result | "No contacts discovered" |
| 4 | No error | Graceful handling |

**Impact on User:** Empty result, expected  
**Rollback:** N/A

---

### TC-FAIL-021: 404 Crawl Pages
**Priority:** P2  
**Severity:** 🟡 Medium

#### How to Simulate
```bash
# Crawl /about, /contact, /team pages
# One of them returns 404
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Crawl multiple pages | Queue pages |
| 2 | One page 404s | Error logged |
| 3 | Other pages succeed | Continue crawling |
| 4 | Results | Show successful pages |

**Impact on User:** Partial results OK  
**Rollback:** N/A

---

### TC-FAIL-022: SERP API Quota Exceeded
**Priority:** P1  
**Severity:** 🟡 Medium

#### How to Simulate
```bash
# Use up SERP API quota
# Next request gets 429 or quota error
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | SERP search | API call |
| 2 | Quota exceeded | Error returned |
| 3 | Error handling | Caught gracefully |
| 4 | User message | "SERP API quota exceeded. Resets in X hours." |

**Impact on User:** Feature temporarily unavailable  
**Rollback:** Wait for quota reset

---

## 7️⃣ NETWORK & INFRASTRUCTURE

### TC-FAIL-023: Slow Network Conditions
**Priority:** P2  
**Severity:** 🟡 Medium

#### How to Simulate
```bash
# Linux network throttling:
sudo tc qdisc add dev eth0 root netem delay 2000ms
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | API requests | Slow responses |
| 2 | Frontend timeout | Loader shows |
| 3 | Request completes | Eventually succeeds |
| 4 | User experience | Loading indicators work |

**Impact on User:** Slow but functional  
**Rollback:** N/A

---

### TC-FAIL-024: Full Disk (Logs)
**Priority:** P1  
**Severity:** 🟠 High

#### How to Simulate
```bash
# Fill disk with large file
dd if=/dev/zero of=/tmp/bigfile bs=1M count=10000
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Disk full | Write fails |
| 2 | Log rotation | Prevents fill |
| 3 | DB writes | Critical ops still work |
| 4 | Alert | Monitoring detects |

**Impact on User:** Potential service degradation  
**Rollback:** Clear logs, add monitoring

---

## 8️⃣ AUTHENTICATION & SECURITY

### TC-FAIL-025: Expired JWT Token
**Priority:** P1  
**Severity:** 🟡 Medium

#### How to Simulate
```python
# Set JWT expiry to 1 minute
# Wait 2 minutes
# Try API call
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Login | Token issued |
| 2 | Wait for expiry | Token expires |
| 3 | API call with expired token | 401 Unauthorized |
| 4 | Frontend intercepts | Redirects to login |

**Impact on User:** Must re-login  
**Rollback:** N/A

---

### TC-FAIL-026: Concurrent Session Handling
**Priority:** P2  
**Severity:** 🟡 Medium

#### How to Simulate
```bash
# Login from two browsers
# Logout from one
# Try request from other
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Login browser A | Token A |
| 2 | Login browser B | Token B |
| 3 | Both tokens valid | Both work |
| 4 | Logout browser A | Token A invalid |
| 5 | Browser B still works | Independent sessions |

**Impact on User:** Multiple sessions allowed (expected)  
**Rollback:** N/A

---

## 9️⃣ DATA INTEGRITY CHECKS

### TC-FAIL-027: Orphan Campaign Leads
**Priority:** P1  
**Severity:** 🟡 Medium

#### How to Simulate
```sql
-- Manually create orphan:
INSERT INTO campaign_leads (campaign_id, lead_id) VALUES (99999, 1);
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Run orphan detector | Script scans DB |
| 2 | Find orphan | campaign_id=99999 doesn't exist |
| 3 | Report | Lists orphan records |
| 4 | Cleanup option | Can delete orphans |

**Impact on User:** Data cleanup  
**Rollback:** Delete orphans

---

### TC-FAIL-028: Missing Foreign Keys
**Priority:** P0  
**Severity:** 🔴 Critical (prevention)

#### How to Simulate
```python
# Try to create campaign_lead with invalid lead_id:
cl = CampaignLead(campaign_id=1, lead_id=99999)
db.add(cl)
db.commit()
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Insert invalid FK | DB constraint violation |
| 2 | Error raised | IntegrityError |
| 3 | Transaction rolled back | No partial data |

**Impact on User:** Operation fails cleanly  
**Rollback:** Automatic

---

## 🔟 WEBHOOK RELIABILITY

### TC-FAIL-029: Webhook Replay Attack
**Priority:** P1  
**Severity:** 🟠 High

#### How to Simulate
```bash
# Capture webhook payload
# Resend same payload twice
curl -X POST http://localhost:8000/api/webhooks/sendgrid \
  -d @webhook_payload.json
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Webhook received | Processed |
| 2 | Same webhook resent | Detected as duplicate |
| 3 | Idempotency check | Skipped processing |
| 4 | Check DB | Event not duplicated |

**Impact on User:** No duplicate processing  
**Rollback:** N/A

---

### TC-FAIL-030: Webhook Signature Verification Fail
**Priority:** P0  
**Severity:** 🔴 Critical

#### How to Simulate
```bash
# Send webhook with wrong signature:
curl -X POST http://localhost:8000/api/webhooks/sendgrid \
  -H "X-Twilio-Email-Event-Webhook-Signature: fake_sig" \
  -d @payload.json
```

#### Steps
| Step | Action | Expected Behavior |
|------|--------|-------------------|
| 1 | Webhook with bad sig | Received |
| 2 | Signature verification | Fails |
| 3 | Response | 401 Unauthorized |
| 4 | Event NOT processed | No DB entry |

**Impact on User:** Security maintained  
**Rollback:** N/A

**Failure Indicators:**
- ❌ Accepts unsigned webhooks
- ❌ Wrong signature accepted

---

## ✅ FAILURE TEST COMPLETION CRITERIA

### Critical (Must Pass)
- ✅ Worker restart doesn't lose tasks
- ✅ Redis outage recovers gracefully
- ✅ DB transaction rollbacks work
- ✅ No duplicate sends
- ✅ DNC enforcement can't be bypassed
- ✅ Webhook signature verified

### High Priority
- ✅ SMTP failures retry correctly
- ✅ Provider rate limits handled
- ✅ CSV malformed data handled
- ✅ Orphan detection works

### Medium Priority
- ✅ Discovery edge cases handled
- ✅ DNS checker edge cases
- ✅ Token expiry handled

---

**Next:** [Security Tests →](./03_SECURITY_TESTS.md)
