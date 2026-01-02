# 🚀 Production Readiness QA Plan - Lead Gen SaaS

**Version:** 1.0  
**Target Launch:** Week 4  
**Test Scope:** Single-user mode, current features only  
**Status:** Pre-launch validation

---

## 📋 Test Execution Summary

| Category | Test Cases | Priority | Status |
|----------|-----------|----------|--------|
| Authentication | 8 | P0 | ⏳ Pending |
| Leads Management | 12 | P0 | ⏳ Pending |
| Lead Discovery | 10 | P0 | ⏳ Pending |
| Company Enrichment | 6 | P1 | ⏳ Pending |
| Campaigns & Sequences | 15 | P0 | ⏳ Pending |
| Sending Flow | 18 | P0 | ⏳ Pending |
| Deliverability Tools | 8 | P1 | ⏳ Pending |
| Worker Reliability | 10 | P0 | ⏳ Pending |
| Security | 12 | P0 | ⏳ Pending |

**Total Test Cases:** 99  
**Estimated Test Time:** 12-16 hours

---

## 🎯 Testing Philosophy

### What We Test
✅ Real user workflows  
✅ Data integrity  
✅ Safety controls  
✅ Worker reliability  
✅ Email delivery correctness  
✅ Security boundaries

### What We DON'T Test (Not Implemented)
❌ Team organizations  
❌ Role-based access  
❌ A/B testing  
❌ Multi-tenant features

---

## 📁 QA Directory Structure

```
/qa/
├── QA_MASTER_PLAN.md           # This file
├── 01_CORE_FUNCTIONALITY.md    # Manual test cases
├── 02_FAILURE_SCENARIOS.md     # Edge cases & failure tests
├── 03_SECURITY_TESTS.md        # Security validation
├── 04_LOAD_STABILITY.md        # Performance tests
├── 05_GAP_REPORT.md            # Risk analysis & recommendations
├── smoke/                       # Quick sanity checks
│   ├── health_check.py
│   ├── celery_check.py
│   ├── redis_check.py
│   └── db_migration_check.py
└── tools/                       # Data integrity validators
    ├── detect_duplicates.py
    ├── detect_orphans.py
    ├── failed_task_scanner.py
    └── webhook_replayer.py
```

---

## ⚡ Quick Start

### Pre-Test Setup
```bash
# 1. Ensure all services running
docker-compose ps

# 2. Run smoke tests
python qa/smoke/health_check.py
python qa/smoke/celery_check.py
python qa/smoke/redis_check.py
python qa/smoke/db_migration_check.py

# 3. Check data integrity
python qa/tools/detect_duplicates.py
python qa/tools/detect_orphans.py
```

### Test Execution Order
1. **Smoke Tests** (5 min) - Automated
2. **Core Functionality** (4 hours) - Manual
3. **Failure Scenarios** (3 hours) - Manual + Simulated
4. **Security Tests** (2 hours) - Manual
5. **Load Tests** (2 hours) - Automated
6. **Gap Analysis** (1 hour) - Review

---

## 🔥 Critical Path (Must Pass Before Launch)

### P0 - Launch Blockers
- [ ] User can sign up and log in
- [ ] CSV import works without corruption
- [ ] Campaigns send emails successfully
- [ ] Bounce → do-not-contact enforcement
- [ ] Reply detection stops campaigns
- [ ] Warm-up limits enforced
- [ ] Quota limits enforced
- [ ] Worker tasks execute reliably
- [ ] No PII in logs
- [ ] No authentication bypass

### P1 - High Priority (Fix Before Beta)
- [ ] Discovery handles failures gracefully
- [ ] Enrichment doesn't block sends
- [ ] DNS checker handles edge cases
- [ ] Webhook replay works
- [ ] Duplicate detection prevents corruption

### P2 - Medium Priority (Acceptable Post-Launch)
- [ ] UI polish items
- [ ] Non-critical error messages
- [ ] Performance optimizations

---

## 📊 Test Metrics & Success Criteria

### Functional Requirements
- ✅ 100% of P0 tests passing
- ✅ 95%+ of P1 tests passing
- ✅ Zero data corruption scenarios
- ✅ Zero authentication bypasses

### Performance Requirements
- ✅ 5000 lead CSV import < 30 seconds
- ✅ Campaign activation < 3 seconds
- ✅ Email send latency < 5 seconds
- ✅ Discovery scan (10 domains) < 60 seconds

### Reliability Requirements
- ✅ Worker restart recovers cleanly
- ✅ Redis outage doesn't corrupt state
- ✅ DB connection retry works
- ✅ No duplicate sends after retry

---

## 🚨 Test Environment Requirements

### Required Test Data
- 10 test leads with valid emails
- 5 test domains for discovery
- 1 active SMTP account
- 1 active SendGrid account
- Test webhook endpoint (ngrok/local)

### Test Accounts
- Admin user (primary test account)
- Test email recipients (Gmail/Outlook)
- Bounce simulation email
- Reply simulation email

### External Dependencies
- SERP API test key
- Gemini API test key
- SendGrid test API key
- Public DNS server access

---

## 📝 Test Reporting

### Bug Report Template
```markdown
## Bug Title
**Severity:** P0 / P1 / P2  
**Component:** Auth / Leads / Campaigns / Workers / etc.  
**Test Case:** [Reference test case ID]

### Steps to Reproduce
1. 
2. 
3. 

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happened]

### Impact
[User impact / data risk]

### Logs/Screenshots
[Attach relevant evidence]
```

### Test Sign-Off Checklist
- [ ] All P0 tests executed
- [ ] All P0 bugs fixed
- [ ] All smoke tests passing
- [ ] Data integrity validated
- [ ] Security tests passed
- [ ] Load tests completed
- [ ] Gap report reviewed
- [ ] Rollback plan documented

---

## 🔗 Related Documents
- [Core Functionality Tests](./01_CORE_FUNCTIONALITY.md)
- [Failure Scenarios](./02_FAILURE_SCENARIOS.md)
- [Security Tests](./03_SECURITY_TESTS.md)
- [Load & Stability](./04_LOAD_STABILITY.md)
- [Gap Report](./05_GAP_REPORT.md)

---

**Next Step:** Review [Core Functionality Tests](./01_CORE_FUNCTIONALITY.md)
