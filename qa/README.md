# 🚀 QA Testing - Quick Start Guide

This directory contains all QA testing materials for the Lead Gen SaaS application.

## 📁 Directory Structure

```
qa/
├── QA_MASTER_PLAN.md              # Overview & test execution plan
├── 01_CORE_FUNCTIONALITY.md       # 77 manual test cases
├── 02_FAILURE_SCENARIOS.md        # 30 failure simulation tests
├── 03_SECURITY_TESTS.md           # 25 security validation tests
├── 05_GAP_REPORT.md               # Risk analysis & launch readiness
├── 06_DELIVERABILITY_PAGE_TESTS.md # Deliverability safety tests
├── run_all_smoke_tests.py         # Run all automated checks
├── smoke/                          # Quick health checks (5 min)
│   ├── health_check.py
│   ├── celery_check.py
│   ├── redis_check.py
│   └── db_migration_check.py
├── deliverability/                 # Deliverability safety validation
│   ├── dns_validator.py
│   ├── warmup_limit_test.py
│   ├── throttle_test.py
│   └── README.md
└── tools/                          # Data integrity validators
    ├── detect_duplicates.py
    ├── detect_orphans.py
    ├── failed_task_scanner.py
    └── webhook_replayer.py
```

## ⚡ Quick Start

### 1. Run Smoke Tests (5 minutes)
```bash
cd qa
python run_all_smoke_tests.py
```

This runs:
- API health check
- Redis connectivity
- Database migration status
- Celery worker health

**Exit Code:** 0 = healthy, 1 = issues found

### 2. Check Data Integrity (2 minutes)
```bash
python tools/detect_duplicates.py
python tools/detect_orphans.py
```

### 3. Test Deliverability Safety Controls (5 minutes)
```bash
cd deliverability

# DNS validation
python dns_validator.py --domain yourdomain.com

# Quota enforcement
python warmup_limit_test.py

# Rate limiting
python throttle_test.py
```

### 4. Manual Testing
Follow test cases in order:
1. [Core Functionality](./01_CORE_FUNCTIONALITY.md) - 4 hours
2. [Deliverability Page](./06_DELIVERABILITY_PAGE_TESTS.md) - 3 hours
3. [Failure Scenarios](./02_FAILURE_SCENARIOS.md) - 3 hours
4. [Security Tests](./03_SECURITY_TESTS.md) - 2 hours

## 🎯 Priority Test Areas

### P0 - Must Pass Before Beta (BLOCKING)
- [ ] Authentication (TC-AUTH-001 to TC-AUTH-008)
- [ ] SPF Warning Before Send (TC-DELIV-101, TC-DELIV-201)
- [ ] Warm-Up Limit Enforcement (TC-DELIV-301)
- [ ] DNC Enforcement (TC-SEND-005, TC-DELIV-302)
- [ ] Duplicate Send Prevention (TC-SEND-012, TC-FAIL-007)
- [ ] Over-Aggressive SDR Protection (TC-DELIV-303)
- [ ] Risk Indicators Accuracy (TC-DELIV-108)

### P1 - Fix Before Public Launch
- [ ] DNS Record Detection (TC-DELIV-102, TC-DELIV-103)
- [ ] Email Provider Failures (TC-FAIL-001 to TC-FAIL-004)
- [ ] Discovery Edge Cases (TC-DISC-004 to TC-DISC-010)
- [ ] Webhook Security (TC-SEC-016, TC-SEC-017)
- [ ] Capacity Planning (TC-DELIV-202)

## 🔧 Individual Test Scripts

### Smoke Tests (Quick Health Checks)
```bash
# API Health
python smoke/health_check.py

# Redis Health
python smoke/redis_check.py

# Database Status
python smoke/db_migration_check.py

# Celery Workers
python smoke/celery_check.py
```

### Deliverability Safety Tests
```bash
cd deliverability

# DNS validation (SPF/DKIM/DMARC)
python dns_validator.py --domain yourdomain.com

# Warm-up quota enforcement
python warmup_limit_test.py

# Rate limiting / throttling
python throttle_test.py
```

### Data Integrity Tools
```bash
# Find duplicate emails
python tools/detect_duplicates.py
python tools/detect_duplicates.py --fix  # Auto-delete duplicates

# Find orphan records
python tools/detect_orphans.py
python tools/detect_orphans.py --cleanup  # Auto-clean
```

## 📊 Test Metrics

**Total Test Cases:** 99+
- Core Functionality: 77 tests
- Failure Scenarios: 30 tests
- Security Tests: 25 tests

**Test Coverage:**
- Authentication: 8 tests
- Leads: 12 tests
- Discovery: 10 tests
- Campaigns: 15 tests
- Sending: 18 tests
- Security: 25 tests
- Failures: 30 tests

## 🚨 Before Production Deployment

Run this checklist:

```bash
# 1. Smoke tests
python run_all_smoke_tests.py

# 2. Data integrity
python tools/detect_duplicates.py
python tools/detect_orphans.py

# 3. Manual P0 tests
# See QA_MASTER_PLAN.md section "Critical Path"

# 4. Review gap report
cat 05_GAP_REPORT.md
```

## 📝 Test Execution Tips

### Running in Docker
```bash
# All commands assume you're in the project root
cd /path/to/lead-gen

# Services must be running
docker-compose ps  # Check status

# If not running
docker-compose up -d
```

### Test Environment
- Use **test data** only
- Don't use real email addresses
- Set low quotas (10/day) for safety
- Use test SMTP/SendGrid accounts

### Reporting Bugs
Use this format:
```markdown
## Bug Title
**Severity:** P0/P1/P2
**Test Case:** TC-XXX-NNN
**Steps:** ...
**Expected:** ...
**Actual:** ...
**Impact:** ...
```

## 🔗 Related Documents

- [Project Structure](../PROJECT_STRUCTURE.md)
- [API Reference](../API_REFERENCE.md)
- [User Guide](../USER_GUIDE.md)
- [Setup Instructions](../SETUP.md)

## 🆘 Troubleshooting

### Smoke Tests Failing?
```bash
# Check containers
docker-compose ps

# Check logs
docker-compose logs backend
docker-compose logs redis
docker-compose logs postgres

# Restart services
docker-compose restart
```

### Python Scripts Not Found?
```bash
# Make scripts executable
chmod +x qa/smoke/*.py
chmod +x qa/tools/*.py

# Or run with python explicitly
python qa/smoke/health_check.py
```

### Permission Errors?
```bash
# Run as current user
docker-compose exec -u $(id -u):$(id -g) backend python -c "..."
```

## 📞 Support

For questions or issues with the QA suite:
1. Check the [Gap Report](./05_GAP_REPORT.md) for known issues
2. Review test case documentation
3. Check recent test results

## ✅ Success Criteria

System is ready for beta when:
- ✅ All smoke tests pass
- ✅ No duplicate emails detected
- ✅ No orphan records
- ✅ All P0 manual tests pass
- ✅ No data corruption issues
- ✅ Workers stable for 24 hours

---

**Last Updated:** December 26, 2025  
**Version:** 1.0  
**Status:** Ready for use
