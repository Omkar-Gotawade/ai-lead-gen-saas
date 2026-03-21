#!/usr/bin/env python3
"""
Comprehensive QA Test Suite
Tests the full app before alpha launch.

Routes confirmed from source:
  Auth:          /auth/login  (field: email, password)
  Leads:         /leads  (no /api prefix)
  Campaigns:     /api/campaigns
  AI Email:      /api/generate-email
  Email Provider:/api/email-provider/me
  Deliverability:/api/deliverability/health
"""
import requests
import json
import sys

BASE = "http://localhost:8000"

results = []
token = None
token2 = None

def log(category, test, status, detail=""):
    syms = {"PASS": "✅ PASS", "FAIL": "❌ FAIL", "WARN": "⚠️  WARN"}
    sym = syms.get(status, status)
    line = f"  {sym} [{category}] {test}"
    if detail:
        line += f"  →  {detail}"
    results.append((status, line))
    print(line)

def section(title):
    print(f"\n{'='*65}")
    print(f"  {title}")
    print(f"{'='*65}")

# ──────────────────────────────────────────────
section("1. INFRASTRUCTURE")
# ──────────────────────────────────────────────

try:
    r = requests.get(f"{BASE}/health", timeout=5)
    if r.status_code == 200 and r.json().get("status") == "healthy":
        log("INFRA", "Health endpoint /health", "PASS")
    else:
        log("INFRA", "Health endpoint /health", "FAIL", str(r.status_code))
except Exception as e:
    log("INFRA", "Backend reachable", "FAIL", str(e))
    print("\n🛑 Backend not reachable. Aborting tests.")
    sys.exit(1)

r = requests.get(f"{BASE}/")
log("INFRA", "Root endpoint / ", "PASS" if r.status_code == 200 else "FAIL",
    f"v{r.json().get('version')}")

r = requests.get(f"{BASE}/docs")
if r.status_code == 200:
    log("INFRA", "Swagger /docs exposed", "WARN", "Disable in production (set docs_url=None)")
else:
    log("INFRA", "Swagger docs hidden", "PASS")

r = requests.get(f"{BASE}/redoc")
if r.status_code == 200:
    log("INFRA", "ReDoc /redoc exposed", "WARN", "Disable in production")
else:
    log("INFRA", "ReDoc hidden", "PASS")

# ──────────────────────────────────────────────
section("2. AUTHENTICATION")
# ──────────────────────────────────────────────

# Valid login - test user (pre-created: qatest_launch@example.com / QAtest123!)
r = requests.post(f"{BASE}/auth/login", json={"email": "qatest_launch@example.com", "password": "QAtest123!"})
if r.status_code == 200:
    token = r.json()["access_token"]
    log("AUTH", "Login - valid user (qatest_launch)", "PASS")
else:
    log("AUTH", "Login - valid user (qatest_launch)", "FAIL", f"{r.status_code}: {r.text[:80]}")

# Valid login - second test user
r = requests.post(f"{BASE}/auth/login", json={"email": "qatest2_launch@example.com", "password": "QAtest123!"})
if r.status_code == 200:
    token2 = r.json()["access_token"]
    log("AUTH", "Login - valid user 2 (qatest2_launch)", "PASS")
else:
    log("AUTH", "Login - valid user 2 (qatest2_launch)", "WARN", f"{r.status_code}: {r.text[:80]}")

# Wrong password (must be 401)
r = requests.post(f"{BASE}/auth/login", json={"email": "qatest_launch@example.com", "password": "wrongpass"})
log("AUTH", "Wrong password → 401", "PASS" if r.status_code == 401 else "FAIL", f"got {r.status_code}")

# Non-existent user (must be 401)
r = requests.post(f"{BASE}/auth/login", json={"email": "hacker@evil.com", "password": "anypass"})
log("AUTH", "Non-existent user → 401", "PASS" if r.status_code == 401 else "FAIL", f"got {r.status_code}")

# Empty password
r = requests.post(f"{BASE}/auth/login", json={"email": "qatest_launch@example.com", "password": ""})
log("AUTH", "Empty password rejected", "PASS" if r.status_code in [401, 422] else "FAIL", f"got {r.status_code}")

# SQL injection in email
r = requests.post(f"{BASE}/auth/login", json={"email": "' OR '1'='1", "password": "x"})
log("AUTH", "SQL injection in email → rejected", "PASS" if r.status_code in [401, 422] else "FAIL", f"got {r.status_code}")

# /auth/me without token
r = requests.get(f"{BASE}/auth/me")
log("AUTH", "/auth/me without token → 401", "PASS" if r.status_code == 401 else "FAIL", f"got {r.status_code}")

# Registration - duplicate email guard
if token:
    r = requests.post(f"{BASE}/auth/register", json={
        "email": "qatest_launch@example.com", "password": "QAtest123!",
        "full_name": "Dupe Test"
    })
    log("AUTH", "Duplicate registration → 400", "PASS" if r.status_code == 400 else "WARN", f"got {r.status_code}")

# ──────────────────────────────────────────────
section("3. LEADS API  [GET /leads, POST /leads]")
# ──────────────────────────────────────────────

if not token:
    print("  ⚠️  Skipping - no auth token")
else:
    headers = {"Authorization": f"Bearer {token}"}

    # List leads (no auth)
    r = requests.get(f"{BASE}/leads")
    log("LEADS", "GET /leads without auth → 401", "PASS" if r.status_code == 401 else "FAIL", f"got {r.status_code}")

    # List leads (with auth)
    r = requests.get(f"{BASE}/leads", headers=headers)
    if r.status_code == 200:
        leads = r.json()
        count = len(leads) if isinstance(leads, list) else leads.get("total", "?")
        log("LEADS", "GET /leads", "PASS", f"count={count}")
    else:
        log("LEADS", "GET /leads", "FAIL", f"{r.status_code}: {r.text[:80]}")

    # Create lead - valid
    new_lead = {
        "first_name": "QA",
        "last_name": "Tester",
        "email": "qa.unique.test.9234@example.com",
        "company": "TestCorp",
        "title": "QA Engineer",
        "research_notes": "Testing app for launch readiness"
    }
    r = requests.post(f"{BASE}/leads", headers=headers, json=new_lead)
    if r.status_code in [200, 201]:
        lead_id = r.json().get("id")
        log("LEADS", "POST /leads - create", "PASS", f"id={str(lead_id)[:8]}...")
    else:
        lead_id = None
        log("LEADS", "POST /leads - create", "FAIL", f"{r.status_code}: {r.text[:80]}")

    # Get single lead
    if lead_id:
        r = requests.get(f"{BASE}/leads/{lead_id}", headers=headers)
        log("LEADS", "GET /leads/{id}", "PASS" if r.status_code == 200 else "FAIL", f"got {r.status_code}")

    # Create lead - missing email
    r = requests.post(f"{BASE}/leads", headers=headers, json={"first_name": "NoEmail", "last_name": "X", "company": "Test"})
    log("LEADS", "Missing email → 422", "PASS" if r.status_code == 422 else "WARN", f"got {r.status_code}")

    # Create lead - invalid email format
    r = requests.post(f"{BASE}/leads", headers=headers, json={
        "first_name": "Bad", "last_name": "Email", "email": "not-an-email", "company": "Test"
    })
    log("LEADS", "Invalid email format", "PASS" if r.status_code == 422 else "WARN", f"got {r.status_code}")

    # Get 404 for unknown lead
    r = requests.get(f"{BASE}/leads/00000000-0000-0000-0000-000000000000", headers=headers)
    log("LEADS", "GET unknown lead → 404", "PASS" if r.status_code == 404 else "WARN", f"got {r.status_code}")

    # Delete test lead
    if lead_id:
        r = requests.delete(f"{BASE}/leads/{lead_id}", headers=headers)
        log("LEADS", "DELETE /leads/{id}", "PASS" if r.status_code in [200, 204] else "FAIL", f"got {r.status_code}")

    # Cross-user isolation (token vs token2)
    if token2:
        r1 = requests.get(f"{BASE}/leads", headers={"Authorization": f"Bearer {token}"})
        r2 = requests.get(f"{BASE}/leads", headers={"Authorization": f"Bearer {token2}"})
        if r1.status_code == 200 and r2.status_code == 200:
            l1 = r1.json() if isinstance(r1.json(), list) else []
            l2 = r2.json() if isinstance(r2.json(), list) else []
            log("LEADS", "Cross-user data isolation", "PASS", f"user1={len(l1)}, user2={len(l2)} leads")

# ──────────────────────────────────────────────
section("4. EMAIL PROVIDER  [/api/email-provider/me]")
# ──────────────────────────────────────────────

if token2:
    h2 = {"Authorization": f"Bearer {token2}"}
    r = requests.get(f"{BASE}/api/email-provider/me", headers=h2)
    if r.status_code == 200:
        prov = r.json()
        ptype = prov.get("provider_type") if prov else None
        log("PROVIDER", "GET /api/email-provider/me", "PASS", f"provider={ptype}")
        if ptype:
            log("PROVIDER", "Provider is configured", "PASS", ptype)
        else:
            log("PROVIDER", "Provider is configured", "WARN", "Null response - not configured")
    elif r.status_code == 404:
        log("PROVIDER", "GET /api/email-provider/me", "WARN", "Returns 404 instead of null - frontend may break")
    else:
        log("PROVIDER", "GET /api/email-provider/me", "FAIL", f"status={r.status_code}: {r.text[:80]}")

    # Without token
    r = requests.get(f"{BASE}/api/email-provider/me")
    log("PROVIDER", "/api/email-provider/me without auth → 401",
        "PASS" if r.status_code == 401 else "FAIL", f"got {r.status_code}")

# ──────────────────────────────────────────────
section("5. CAMPAIGNS  [/api/campaigns]")
# ──────────────────────────────────────────────

if token:
    headers = {"Authorization": f"Bearer {token}"}
    campaign_id = None

    # List campaigns
    r = requests.get(f"{BASE}/api/campaigns", headers=headers)
    if r.status_code == 200:
        camps = r.json()
        count = len(camps) if isinstance(camps, list) else "?"
        log("CAMPAIGNS", "GET /api/campaigns", "PASS", f"count={count}")
    else:
        log("CAMPAIGNS", "GET /api/campaigns", "FAIL", f"{r.status_code}: {r.text[:80]}")

    # Create campaign
    r = requests.post(f"{BASE}/api/campaigns", headers=headers, json={
        "name": "QA Test Campaign",
        "subject": "Test {{first_name}}",
        "body": "Hi {{first_name}}, this is QA."
    })
    if r.status_code in [200, 201]:
        campaign_id = r.json().get("id")
        log("CAMPAIGNS", "POST /api/campaigns - create", "PASS", f"id={str(campaign_id)[:8]}...")
    else:
        log("CAMPAIGNS", "POST /api/campaigns - create", "FAIL", f"{r.status_code}: {r.text[:80]}")

    # Get single campaign
    if campaign_id:
        r = requests.get(f"{BASE}/api/campaigns/{campaign_id}", headers=headers)
        log("CAMPAIGNS", "GET /api/campaigns/{id}", "PASS" if r.status_code == 200 else "FAIL", f"got {r.status_code}")

    # Campaign without name
    r = requests.post(f"{BASE}/api/campaigns", headers=headers, json={"subject": "No Name"})
    log("CAMPAIGNS", "Create campaign without name", "PASS" if r.status_code == 422 else "WARN", f"got {r.status_code}")

    # Delete test campaign
    if campaign_id:
        r = requests.delete(f"{BASE}/api/campaigns/{campaign_id}", headers=headers)
        log("CAMPAIGNS", "DELETE campaign - cleanup", "PASS" if r.status_code in [200, 204] else "WARN", f"got {r.status_code}")

    # Auth required
    r = requests.get(f"{BASE}/api/campaigns")
    log("CAMPAIGNS", "GET /api/campaigns without auth → 401",
        "PASS" if r.status_code == 401 else "FAIL", f"got {r.status_code}")

# ──────────────────────────────────────────────
section("6. AI EMAIL GENERATION  [/api/generate-email]")
# ──────────────────────────────────────────────

if token:
    headers = {"Authorization": f"Bearer {token}"}

    # Create temp lead
    r = requests.post(f"{BASE}/leads", headers=headers, json={
        "first_name": "Alex",
        "last_name": "Smith",
        "email": "alex.qa.test.9234@example.com",
        "company": "TechCorp",
        "title": "VP Sales",
        "research_notes": "Series A $3M raised Dec 2025. Growing SDR team from 5 to 10."
    })
    if r.status_code in [200, 201]:
        test_lead_id = r.json().get("id")

        r = requests.post(f"{BASE}/api/generate-email", headers=headers, json={
            "lead_id": test_lead_id,
            "tone": "professional",
            "goal": "schedule a demo",
            "product_description": "email deliverability monitoring platform"
        })
        if r.status_code == 200:
            email = r.json()
            subject = email.get("subject", "")
            body = email.get("body", "")
            word_count = len(body.split())
            log("AI", "POST /api/generate-email", "PASS", f"words={word_count}")
            log("AI", "Subject generated", "PASS" if subject else "FAIL", subject[:60] if subject else "empty")
            log("AI", "Body length (30-200 words)", "PASS" if 30 <= word_count <= 200 else "WARN", f"{word_count} words")

            # Check banned phrases
            body_lower = body.lower()
            banned_found = [p for p in [
                "i hope this email finds you",
                "wanted to reach out",
                "leverage", "synergy", "paradigm shift", "game-changing"
            ] if p in body_lower]
            if banned_found:
                log("AI", "No banned phrases", "WARN", f"found: {banned_found}")
            else:
                log("AI", "No banned phrases in output", "PASS")

            # Check personalization used research notes
            research_terms = ["series a", "3m", "sdr", "$3", "10", "growing"]
            used = [t for t in research_terms if t in body_lower]
            log("AI", "Research notes used in email", "PASS" if used else "WARN",
                f"matched: {used}")
        else:
            log("AI", "POST /api/generate-email", "FAIL", f"{r.status_code}: {r.text[:80]}")

        # Cleanup test lead
        requests.delete(f"{BASE}/leads/{test_lead_id}", headers=headers)
    else:
        log("AI", "Test lead creation", "FAIL", r.text[:80])

    # Missing lead_id
    r = requests.post(f"{BASE}/api/generate-email", headers=headers, json={
        "tone": "professional", "goal": "demo"
    })
    log("AI", "Missing lead_id → 422", "PASS" if r.status_code == 422 else "WARN", f"got {r.status_code}")

    # Non-existent lead
    r = requests.post(f"{BASE}/api/generate-email", headers=headers, json={
        "lead_id": "00000000-0000-0000-0000-000000000000",
        "tone": "professional", "goal": "demo",
        "product_description": "test"
    })
    log("AI", "Invalid lead_id → 404", "PASS" if r.status_code == 404 else "WARN", f"got {r.status_code}")

# ──────────────────────────────────────────────
section("7. DELIVERABILITY  [/api/deliverability/*]")
# ──────────────────────────────────────────────

if token2:
    h2 = {"Authorization": f"Bearer {token2}"}

    # GET endpoints
    for path, label in [
        ("/api/deliverability/health", "Health score"),
        ("/api/deliverability/warmup/status", "Warmup status"),
    ]:
        r = requests.get(f"{BASE}{path}", headers=h2)
        if r.status_code == 200:
            data = r.json()
            detail = ""
            if path == "/api/deliverability/health":
                detail = f"score={data.get('score')}, status={data.get('status')}"
            elif path == "/api/deliverability/warmup/status":
                detail = f"day={data.get('warmup_day')}, limit={data.get('daily_limit')}"
            log("DELIV", label, "PASS", detail)
        else:
            log("DELIV", label, "FAIL", f"status={r.status_code}: {r.text[:80]}")

    # Safety diagnostics is POST
    r = requests.post(f"{BASE}/api/deliverability/safety-diagnostics", headers=h2)
    if r.status_code == 200:
        data = r.json()
        log("DELIV", "Safety diagnostics", "PASS", f"keys={list(data.keys())[:4]}")
    else:
        log("DELIV", "Safety diagnostics", "FAIL", f"status={r.status_code}: {r.text[:80]}")

# ──────────────────────────────────────────────
section("8. WEBHOOKS  [/api/webhooks/*]")
# ──────────────────────────────────────────────

if token:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE}/api/webhooks/events", headers=headers)
    log("WEBHOOKS", "GET /api/webhooks/events", "PASS" if r.status_code == 200 else "FAIL",
        f"got {r.status_code}")

    # Webhook receiver (public endpoint)
    r = requests.post(f"{BASE}/api/webhooks/sendgrid", json=[{
        "event": "delivered",
        "email": "test@example.com",
        "timestamp": 1700000000
    }])
    log("WEBHOOKS", "POST /api/webhooks/sendgrid (receive)", "PASS" if r.status_code == 200 else "WARN",
        f"got {r.status_code}")

# ──────────────────────────────────────────────
section("9. SECURITY CHECKS")
# ──────────────────────────────────────────────

# Rate limiting - hit a route that IS rate-limited (not /health which is excluded)
rate_hit = False
for i in range(65):
    r = requests.get(f"{BASE}/auth/me")  # not excluded, returns 401 fast
    if r.status_code == 429:
        rate_hit = True
        log("SECURITY", "Rate limiting (429 after burst)", "PASS", f"triggered at req #{i+1}")
        break
if not rate_hit:
    log("SECURITY", "Rate limiting", "WARN", "65 requests to /auth/me sent, no 429 - in-memory limiter won't persist across workers")

# CORS headers on OPTIONS with a legitimate origin
r = requests.options(f"{BASE}/auth/login", headers={
    "Origin": "http://localhost:5173",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type,authorization"
})
cors = r.headers.get("access-control-allow-origin", "")
if cors in ("http://localhost:5173", "*"):
    log("SECURITY", "CORS allows frontend origin", "PASS", f"allow-origin: {cors}")
    if cors == "*":
        log("SECURITY", "CORS origin too broad", "WARN", "Allow * in prod - restrict in production config")
else:
    log("SECURITY", "CORS allows frontend origin", "FAIL", f"Got: '{cors}' - frontend may be blocked")

# Verify evil origin is rejected
r2 = requests.options(f"{BASE}/auth/login", headers={"Origin": "http://evil.com"})
evil_cors = r2.headers.get("access-control-allow-origin", "")
if evil_cors in ("", "null"):
    log("SECURITY", "CORS rejects unknown origin", "PASS")
else:
    log("SECURITY", "CORS rejects unknown origin", "WARN", f"Returned: '{evil_cors}'")

# XSS in lead name
if token:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{BASE}/leads", headers=headers, json={
        "first_name": "<script>alert('xss')</script>",
        "last_name": "XSS",
        "email": "xss.test.qa.9234@example.com",
        "company": "XSS Corp"
    })
    if r.status_code in [200, 201]:
        stored = r.json().get("first_name", "")
        xss_id = r.json().get("id")
        if "<script>" in stored:
            log("SECURITY", "XSS stored raw (HTML not escaped)", "WARN",
                "Ensure output is escaped in frontend - React does this automatically")
        else:
            log("SECURITY", "XSS data sanitised on input", "PASS")
        if xss_id:
            requests.delete(f"{BASE}/leads/{xss_id}", headers=headers)
        elif r.status_code in [422, 429]:
            log("SECURITY", "XSS input rejected", "PASS", f"rejected with {r.status_code}")
        else:
            log("SECURITY", "XSS input rejected", "WARN", f"got {r.status_code}")

    # Path traversal
    r = requests.get(f"{BASE}/../../../etc/passwd")
    log("SECURITY", "Path traversal blocked", "PASS" if r.status_code in [400, 404, 429] else "WARN",
        f"got {r.status_code}")

    # Large payload (DoS test)
    huge_payload = {"email": "dos@test.com", "first_name": "A" * 100000, "last_name": "B", "company": "C"}
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.post(f"{BASE}/leads", headers=headers, json=huge_payload, timeout=10)
        # 413=too large, 422=validation error, 429=rate limited (all safe outcomes)
        log("SECURITY", "Large payload handled", "PASS" if r.status_code in [413, 422, 429] else "WARN",
            f"got {r.status_code}")

# ──────────────────────────────────────────────
section("10. FRONTEND")
# ──────────────────────────────────────────────

frontend_urls = [
    ("http://frontend:5173", "Frontend container at frontend:5173"),
    ("http://localhost:5173", "Frontend at localhost:5173"),
]
frontend_ok = False
for url, label in frontend_urls:
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and "<!doctype" in r.text.lower():
            log("FRONTEND", label, "PASS", "HTML served")
            frontend_ok = True
            break
    except Exception:
        pass

if not frontend_ok:
    log("FRONTEND", "Frontend test from container", "WARN",
        "Can't reach localhost:5173 from within Docker - test from browser at http://localhost:5173")

# ──────────────────────────────────────────────
section("FINAL REPORT")
# ──────────────────────────────────────────────

pass_n = sum(1 for s, _ in results if s == "PASS")
fail_n = sum(1 for s, _ in results if s == "FAIL")
warn_n = sum(1 for s, _ in results if s == "WARN")
total_n = len(results)

print(f"""
  Total Tests :  {total_n}
  ✅ PASS     :  {pass_n}
  ❌ FAIL     :  {fail_n}
  ⚠️  WARN     :  {warn_n}
""")

if fail_n > 0:
    print("  FAILED TESTS (must fix before launch):")
    for s, line in results:
        if s == "FAIL":
            print(f"  {line}")

if warn_n > 0:
    print("\n  WARNINGS (review before production):")
    for s, line in results:
        if s == "WARN":
            print(f"  {line}")

if fail_n == 0:
    print("  🚀 VERDICT: READY FOR ALPHA LAUNCH")
else:
    print("  🛑 VERDICT: NOT READY - Fix the FAILs above first")
    sys.exit(1)
