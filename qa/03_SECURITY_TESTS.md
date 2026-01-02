# 🔐 Security & Compliance Test Cases

**Category:** Security Validation  
**Priority:** P0 (Launch Blockers)  
**Estimated Time:** 2 hours

---

## 🎯 Security Testing Goals

- Verify authentication cannot be bypassed
- Validate DNC enforcement is absolute
- Check for PII exposure
- Test webhook security
- Validate input sanitization

---

## 1️⃣ AUTHENTICATION SECURITY

### TC-SEC-001: API Access Without Auth Token
**Priority:** P0  
**Severity:** 🔴 Critical

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Remove auth token from localStorage | Token gone |
| 2 | Try GET `/api/leads` | 401 Unauthorized |
| 3 | Try POST `/api/campaigns` | 401 Unauthorized |
| 4 | Try GET `/api/users/me` | 401 Unauthorized |
| 5 | Check error message | Clear "Authentication required" |

**Failure:** If any protected endpoint allows access without token  
**Impact:** 🔴 Complete security breach

---

### TC-SEC-002: Invalid/Malformed JWT Token
**Priority:** P0  
**Severity:** 🔴 Critical

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Set token to "invalid_token_123" | Invalid token |
| 2 | Try API request | 401 Unauthorized |
| 3 | Set token to empty string | 401 Unauthorized |
| 4 | Set malformed JWT (missing signature) | 401 Unauthorized |
| 5 | Check no crash | Server handles gracefully |

**Failure:** Server crashes, accepts invalid token  
**Impact:** 🔴 Critical security flaw

---

### TC-SEC-003: Token Tampering
**Priority:** P0  
**Severity:** 🔴 Critical

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Get valid JWT token | Token obtained |
| 2 | Decode token (jwt.io) | See payload |
| 3 | Modify payload (change user_id) | Modified token |
| 4 | Re-encode without proper signing | Invalid signature |
| 5 | Try API request | 401 Unauthorized |

**Failure:** Modified token accepted  
**Impact:** 🔴 Account takeover risk

---

### TC-SEC-004: SQL Injection in Login
**Priority:** P0  
**Severity:** 🔴 Critical

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Email: `admin' OR '1'='1` | Input accepted |
| 2 | Password: `password` | Submit |
| 3 | Check response | Login fails (invalid credentials) |
| 4 | Check logs | No SQL error |
| 5 | Check DB | No unauthorized access |

**Failure:** SQL injection succeeds, unauthorized access  
**Impact:** 🔴 Critical - database compromise

---

## 2️⃣ DATA ACCESS CONTROL

### TC-SEC-005: Cross-User Data Access
**Priority:** P0  
**Severity:** 🔴 Critical

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Login as User A | Token A |
| 2 | Create lead (ID=100) | Lead created |
| 3 | Login as User B (different account) | Token B |
| 4 | Try GET `/api/leads/100` (User A's lead) | 403 Forbidden or 404 Not Found |
| 5 | Try PUT `/api/leads/100` | 403 Forbidden |
| 6 | Check User B cannot see User A's leads | ✓ Isolated |

**Failure:** User B can access User A's data  
**Impact:** 🔴 Critical - data breach

---

### TC-SEC-006: Direct Campaign ID Manipulation
**Priority:** P0  
**Severity:** 🔴 Critical

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | User A creates campaign (ID=10) | Created |
| 2 | Login as User B | New session |
| 3 | Try GET `/api/campaigns/10` | 403 or 404 |
| 4 | Try PUT `/api/campaigns/10` | 403 |
| 5 | Try DELETE `/api/campaigns/10` | 403 |

**Failure:** User B can access/modify User A's campaign  
**Impact:** 🔴 Critical

---

## 3️⃣ DO-NOT-CONTACT ENFORCEMENT

### TC-SEC-007: Bypassing DNC via API
**Priority:** P0  
**Severity:** 🔴 Critical

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Mark lead as `do_not_contact=true` | DNC set |
| 2 | Try POST `/api/campaigns/{id}/leads` with DNC lead | 400 Bad Request |
| 3 | Try direct SQL insert into campaign_leads | FK constraint or app-level check |
| 4 | Worker tries to send | Blocked at send time |
| 5 | Check sending_logs | No entry or status=`blocked` |

**Failure:** Email sent to DNC lead  
**Impact:** 🔴 Legal/compliance violation

---

### TC-SEC-008: DNC Field Direct Modification
**Priority:** P0  
**Severity:** 🔴 Critical

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Lead has `do_not_contact=true` | DNC set |
| 2 | Try PUT `/api/leads/{id}` with `do_not_contact=false` | Should require special permission or audit |
| 3 | If allowed, check audit log | Change logged |
| 4 | Try adding to campaign immediately | Still blocked (cached/validated) |

**Failure:** DNC removed without audit, email sent  
**Impact:** 🔴 Compliance risk

---

## 4️⃣ INPUT VALIDATION

### TC-SEC-009: XSS in Lead Name
**Priority:** P1  
**Severity:** 🟠 High

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Create lead with name: `<script>alert('XSS')</script>` | Accepted |
| 2 | View lead in UI | Script NOT executed |
| 3 | Check HTML source | Script escaped: `&lt;script&gt;` |
| 4 | Send email with {{name}} | Script escaped in email |

**Failure:** Script executes in browser  
**Impact:** 🟠 High - XSS vulnerability

---

### TC-SEC-010: SQL Injection in Lead Search
**Priority:** P0  
**Severity:** 🔴 Critical

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Search leads: `' OR 1=1--` | Query executes |
| 2 | Check results | No SQL error, normal results |
| 3 | Check logs | No SQL error logged |
| 4 | Search: `'; DROP TABLE leads;--` | No DB modification |

**Failure:** SQL injection succeeds  
**Impact:** 🔴 Database compromise

---

### TC-SEC-011: Email Header Injection
**Priority:** P1  
**Severity:** 🟠 High

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Lead email: `test@example.com\nBcc:attacker@evil.com` | Input |
| 2 | Send email | Email send attempted |
| 3 | Check email headers | No Bcc to attacker |
| 4 | Validation rejects | Email validation fails |

**Failure:** Email sent to attacker via header injection  
**Impact:** 🟠 Spam/abuse risk

---

### TC-SEC-012: Path Traversal in File Upload
**Priority:** P1  
**Severity:** 🟠 High

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Upload CSV with filename: `../../etc/passwd` | Upload attempted |
| 2 | Check file saved | Sanitized filename used |
| 3 | File not outside upload dir | ✓ Contained |

**Failure:** File saved outside allowed directory  
**Impact:** 🟠 Server compromise

---

## 5️⃣ PII & DATA EXPOSURE

### TC-SEC-013: PII in Logs
**Priority:** P0  
**Severity:** 🔴 Critical

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Create lead with email | Lead created |
| 2 | Check backend logs | Email NOT logged in plain text |
| 3 | Check error logs | No passwords or tokens |
| 4 | API error response | No internal DB details exposed |

**Failure:** Emails, passwords, tokens in logs  
**Impact:** 🔴 Privacy violation

---

### TC-SEC-014: Sensitive Data in API Responses
**Priority:** P0  
**Severity:** 🔴 Critical

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | GET `/api/users/me` | User data returned |
| 2 | Check response | No password hash |
| 3 | Check for API keys | Not exposed |
| 4 | Check for encrypted fields | Not exposed in plain text |

**Failure:** Sensitive fields leaked  
**Impact:** 🔴 Credential exposure

---

### TC-SEC-015: Error Messages Leak Info
**Priority:** P1  
**Severity:** 🟡 Medium

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Login with non-existent email | Error |
| 2 | Check message | Generic: "Invalid credentials" |
| 3 | Login with existing email, wrong password | Same error message |
| 4 | No user enumeration | Cannot determine if user exists |

**Failure:** Different errors reveal user existence  
**Impact:** 🟡 User enumeration attack

---

## 6️⃣ WEBHOOK SECURITY

### TC-SEC-016: Webhook Signature Bypass
**Priority:** P0  
**Severity:** 🔴 Critical

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Send webhook without signature | POST to `/api/webhooks/sendgrid` |
| 2 | Check response | 401 Unauthorized (if signature required) |
| 3 | Send with wrong signature | 401 Unauthorized |
| 4 | Send with valid signature | 200 OK, event processed |

**Failure:** Accepts unsigned webhooks  
**Impact:** 🔴 Fake webhook injection

---

### TC-SEC-017: Webhook Replay Attack
**Priority:** P1  
**Severity:** 🟠 High

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Receive legitimate webhook | Processed |
| 2 | Resend exact same webhook | Received again |
| 3 | Idempotency check | Detects duplicate |
| 4 | Not processed twice | Event skipped |

**Failure:** Webhook processed multiple times  
**Impact:** 🟠 Data corruption, duplicate actions

---

## 7️⃣ RATE LIMITING & ABUSE

### TC-SEC-018: Brute Force Login Protection
**Priority:** P1  
**Severity:** 🟠 High

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Try 10 wrong passwords rapidly | All fail |
| 2 | Check rate limiting | Slows down or blocks |
| 3 | Wait cooldown period | Can try again |

**Note:** Not implemented yet, but recommended  
**Failure:** Unlimited login attempts  
**Impact:** 🟠 Brute force vulnerability

---

### TC-SEC-019: API Rate Limiting
**Priority:** P2  
**Severity:** 🟡 Medium

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Make 100 API requests rapidly | First N succeed |
| 2 | Check rate limit | 429 Too Many Requests |
| 3 | Wait cooldown | Requests allowed again |

**Note:** Nice to have  
**Failure:** Unlimited API calls  
**Impact:** 🟡 DoS risk

---

## 8️⃣ ENCRYPTION & CREDENTIALS

### TC-SEC-020: Credentials Stored Encrypted
**Priority:** P0  
**Severity:** 🔴 Critical

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Save SMTP password in settings | Password saved |
| 2 | Check DB directly | `password_encrypted` field is encrypted blob |
| 3 | Not plain text | Cannot read password |
| 4 | Check SendGrid API key | Also encrypted |

**Failure:** Credentials in plain text  
**Impact:** 🔴 Credential theft

---

### TC-SEC-021: Password Reset Token Security
**Priority:** P1  
**Severity:** 🟠 High

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Request password reset | Token generated |
| 2 | Check token | Long, random, unique |
| 3 | Token expires | After 1 hour |
| 4 | Used token invalid | Cannot reuse |

**Failure:** Predictable tokens, no expiry  
**Impact:** 🟠 Account takeover

---

## 9️⃣ UNSAFE OPERATIONS

### TC-SEC-022: Test Email Safety
**Priority:** P0  
**Severity:** 🔴 Critical

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Try to send test email to production list | Blocked |
| 2 | Environment check | Prod mode requires confirmation |
| 3 | Test mode enabled | Sends to whitelist only |

**Note:** Implement test mode if not present  
**Failure:** Accidentally emails real users  
**Impact:** 🔴 Reputation damage

---

### TC-SEC-023: Bulk Delete Safety
**Priority:** P1  
**Severity:** 🟠 High

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Select all leads (1000+) | Selected |
| 2 | Click delete | Confirmation required |
| 3 | Large delete warning | "Are you sure? This will delete 1000 leads" |
| 4 | Confirm | Delete proceeds |

**Failure:** No confirmation, accidental bulk delete  
**Impact:** 🟠 Data loss

---

## 🔟 GDPR & COMPLIANCE

### TC-SEC-024: Data Export (Right to Access)
**Priority:** P2  
**Severity:** 🟡 Medium

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Request data export | Feature exists (or manual) |
| 2 | Download all user data | JSON/CSV export |
| 3 | Includes all PII | Leads, campaigns, logs |

**Note:** GDPR requirement  
**Failure:** Cannot export data  
**Impact:** 🟡 Compliance issue

---

### TC-SEC-025: Data Deletion (Right to be Forgotten)
**Priority:** P2  
**Severity:** 🟡 Medium

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Request lead deletion | Delete lead |
| 2 | Check DB | Lead removed |
| 3 | Check related data | campaign_leads, sending_logs handled |
| 4 | Verify complete removal | All PII gone |

**Note:** GDPR requirement  
**Failure:** Data persists after deletion  
**Impact:** 🟡 Compliance issue

---

## ✅ SECURITY TEST COMPLETION CRITERIA

### Must Pass (P0)
- ✅ 100% of authentication tests pass
- ✅ No data access bypasses
- ✅ DNC enforcement absolute
- ✅ No SQL injection vulnerabilities
- ✅ No PII in logs
- ✅ Credentials encrypted
- ✅ Webhook signature verification

### Should Pass (P1)
- ✅ XSS prevention
- ✅ No sensitive data in API responses
- ✅ Webhook replay protection
- ✅ Input validation on all endpoints

### Nice to Have (P2)
- ✅ Rate limiting
- ✅ GDPR compliance features

---

**Next:** [Load & Stability Tests →](./04_LOAD_STABILITY.md)
