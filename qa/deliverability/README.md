# 🛡️ Deliverability Test Automation

Automated test scripts for validating deliverability safety controls.

## 📁 Scripts

### 1. `dns_validator.py`
**Purpose:** Validate DNS records (SPF, DKIM, DMARC)

**Usage:**
```bash
# Check domain DNS configuration
python dns_validator.py --domain yourdomain.com

# Specify DKIM selector
python dns_validator.py --domain yourdomain.com --dkim-selector s1

# Check additional DKIM selectors
python dns_validator.py --domain yourdomain.com --additional-selectors google k1 mail
```

**Exit Codes:**
- `0` = All critical records present, domain ready
- `1` = Critical issues found (missing SPF, multiple SPF records, etc.)

**What It Tests:**
- ✅ SPF record presence and validity
- ✅ DKIM record detection (multiple selectors)
- ✅ DMARC record check
- ✅ MX record existence
- ✅ Multiple SPF record detection (RFC violation)
- ✅ Risk assessment (Low/Medium/High)

**Example Output:**
```
🔍 DNS VALIDATION TEST
Domain: example.com
============================================================

Checking SPF...
✓ SPF Found
   v=spf1 include:_spf.google.com ~all
   ℹ Policy: Soft Fail (~all)

Checking DKIM (selector: default)...
✓ DKIM Found (selector: default)

Checking DMARC...
✓ DMARC Found
   v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com
   ℹ Policy: Quarantine (Moderate)

============================================================
📊 RISK ASSESSMENT
============================================================
✓ LOW RISK: Domain Properly Configured
   → SPF, DKIM, DMARC all present
   → Safe to send

✅ DOMAIN READY FOR SENDING
```

**Installation:**
```bash
pip install dnspython
```

---

### 2. `warmup_limit_test.py`
**Purpose:** Verify warm-up quota enforcement

**Usage:**
```bash
# Test quota enforcement (default localhost)
python warmup_limit_test.py

# Test against specific API
python warmup_limit_test.py --api-url https://api.yourdomain.com

# Use custom credentials
python warmup_limit_test.py --email admin@example.com --password secret123

# Dry run (check quota without sending)
python warmup_limit_test.py --skip-send-test
```

**Exit Codes:**
- `0` = Quota enforcement working correctly
- `1` = Can bypass quotas (CRITICAL BUG)

**What It Tests:**
- ✅ Retrieves current warm-up quota
- ✅ Attempts to exceed daily send limit
- ✅ Verifies sends are blocked at quota
- ✅ Confirms proper error responses (429)

**Example Output:**
```
🧪 WARM-UP QUOTA ENFORCEMENT TEST
============================================================

Step 1: Authentication
✓ Login successful

Step 2: Check Quota Status
✓ Quota status retrieved
  Daily limit: 50
  Used today: 5
  Remaining: 45
  Warm-up day: 5

Step 3: Over-Limit Send Test
Simulating over-limit sending attempt...
  Will attempt: 50 sends

  [1/50] ✓ Sent
  [2/50] ✓ Sent
  ...
  [45/50] ✓ Sent
  [46/50] ⚠ Blocked (429 Too Many Requests)
  [47/50] ⚠ Blocked (429 Too Many Requests)

============================================================
📊 ENFORCEMENT ANALYSIS
============================================================
Successful sends: 45
Blocked attempts: 5
Expected remaining quota: 45

✅ PASS: Sends limited to quota (45/45)
   5 over-limit attempts blocked correctly

============================================================
🎯 FINAL RESULT
============================================================
✅ TEST PASSED
Quota enforcement is working correctly
System properly controls warm-up limits
```

**Installation:**
```bash
pip install requests
```

---

### 3. `throttle_test.py`
**Purpose:** Test rate limiting and burst protection

**Usage:**
```bash
# Test with defaults (50 burst requests)
python throttle_test.py

# Custom burst size
python throttle_test.py --burst-count 100 --workers 20

# Skip sustained rate test
python throttle_test.py --skip-sustained
```

**Exit Codes:**
- `0` = Rate limiting active
- `1` = No throttling (RISK)

**What It Tests:**
- ✅ Burst request handling (parallel)
- ✅ Rate limit responses (429)
- ✅ Sustained sending rate over time
- ✅ Response time degradation

**Example Output:**
```
🚦 THROTTLE & RATE LIMIT TEST
============================================================

Step 2: Burst Request Test
Sending burst of 50 requests with 10 parallel workers...
  Progress: 50/50 requests completed...
✓ Burst test completed in 5.23s

============================================================
📊 THROTTLING ANALYSIS
============================================================
Total requests: 50
Successful (200): 30
Rate limited (429): 20
Errors: 0

Response times:
  Average: 0.152s
  Min: 0.045s
  Max: 0.987s

Throughput: 9.6 req/sec

✓ Rate limiting is active
  20 requests blocked (40.0%)
  ℹ Moderate throttling (20-50% blocked)

============================================================
🎯 FINAL RESULT
============================================================
✅ TEST PASSED
Rate limiting is active
System protects against aggressive sending
```

**Installation:**
```bash
pip install requests
```

---

## 🚀 Quick Start

**Install Dependencies:**
```bash
pip install dnspython requests
```

**Run All Tests:**
```bash
# DNS validation
python dns_validator.py --domain yourdomain.com

# Quota enforcement (requires running API)
python warmup_limit_test.py

# Rate limiting
python throttle_test.py
```

---

## 🎯 When to Run These Tests

### Before Production Launch
- [ ] Run `dns_validator.py` on production domain
- [ ] Run `warmup_limit_test.py` with test account
- [ ] Run `throttle_test.py` to verify protection

### After Deployments
- [ ] Re-run `warmup_limit_test.py` to verify quota logic intact
- [ ] Re-run `throttle_test.py` to verify rate limits unchanged

### During Development
- [ ] Run `dns_validator.py` when testing DNS changes
- [ ] Run `warmup_limit_test.py` when modifying quota logic
- [ ] Run `throttle_test.py` when changing rate limits

---

## 🔧 Configuration

### Environment Variables (Optional)
```bash
export API_BASE_URL="http://localhost:8000"
export TEST_EMAIL="test@example.com"
export TEST_PASSWORD="testpass123"
```

### Test Credentials
Update default credentials in scripts or pass via flags:
```python
# In scripts, change defaults:
parser.add_argument('--email', default='YOUR_EMAIL')
parser.add_argument('--password', default='YOUR_PASSWORD')
```

---

## 📊 CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Deliverability Tests
  run: |
    cd qa/deliverability
    
    # DNS validation
    python dns_validator.py --domain ${{ secrets.DOMAIN }}
    
    # Quota enforcement
    python warmup_limit_test.py \
      --api-url ${{ secrets.API_URL }} \
      --email ${{ secrets.TEST_EMAIL }} \
      --password ${{ secrets.TEST_PASSWORD }}
    
    # Rate limiting
    python throttle_test.py --api-url ${{ secrets.API_URL }}
```

### Exit Code Handling
```bash
#!/bin/bash
# run_deliverability_tests.sh

set -e  # Exit on first failure

echo "Running DNS validation..."
python dns_validator.py --domain yourdomain.com

echo "Running quota tests..."
python warmup_limit_test.py

echo "Running throttle tests..."
python throttle_test.py

echo "✅ All deliverability tests passed!"
```

---

## ⚠️ Important Notes

### DNS Validation
- Requires internet connectivity
- DNS propagation can take up to 48 hours
- False negatives possible during propagation

### Quota Testing
- **DO NOT** run against production with real campaigns active
- Use test accounts only
- May consume daily quota during test

### Rate Limit Testing
- Generates significant API traffic
- May trigger alerts if monitoring is active
- Run during off-peak hours in production

---

## 🐛 Troubleshooting

### "dnspython not installed"
```bash
pip install dnspython
```

### "Connection refused"
Check if API is running:
```bash
curl http://localhost:8000/health
```

### "Login failed"
Verify credentials:
```bash
# Check user exists
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

### "Quota endpoint not found"
Deliverability API may not be implemented yet. Test will skip gracefully.

---

## 📝 Test Coverage

These scripts validate:
- ✅ **DNS Configuration:** SPF, DKIM, DMARC presence and validity
- ✅ **Quota Enforcement:** Daily send limits respected
- ✅ **Rate Limiting:** Burst and sustained rate controls
- ✅ **Error Handling:** Proper 429 responses
- ✅ **Safety Controls:** Cannot bypass restrictions

These scripts DO NOT test:
- ❌ UI/UX of deliverability page
- ❌ Campaign scheduling logic
- ❌ Email content validation
- ❌ Actual email delivery (requires SMTP)

---

**Last Updated:** December 29, 2025  
**Version:** 1.0  
**Status:** Production Ready
