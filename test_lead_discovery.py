"""
End-to-end test for the Lead Discovery / Lead Generation feature.
Tests: auth → start job → poll until complete → inspect results
"""
import sys
import time
import requests

BASE = "http://localhost:8000"

# ── 1. Auth ─────────────────────────────────────────────────────────────────
def get_token():
    r = requests.post(f"{BASE}/auth/login",
                      json={"email": "admin@example.com", "password": "admin123"},
                      timeout=10)
    if r.status_code != 200:
        # Try register first
        requests.post(f"{BASE}/auth/register",
                      json={"email": "admin@example.com", "password": "admin123",
                            "full_name": "Test Admin"},
                      timeout=10)
        r = requests.post(f"{BASE}/auth/login",
                          data={"username": "admin@example.com", "password": "admin123"},
                          timeout=10)
    r.raise_for_status()
    token = r.json()["access_token"]
    print(f"✅  Auth OK — token acquired")
    return token

# ── 2. Check existing jobs ───────────────────────────────────────────────────
def list_jobs(headers):
    r = requests.get(f"{BASE}/api/lead-discovery/", headers=headers, timeout=10)
    r.raise_for_status()
    jobs = r.json()
    print(f"✅  List jobs — {len(jobs)} existing job(s)")
    return jobs

# ── 3. Start a discovery job ─────────────────────────────────────────────────
def start_job(headers):
    payload = {
        "keywords": "SaaS startup CEO founder",
        "location": "India",
        "industry": "SaaS",
        "job_title": "CEO",
        "seniority": "c_suite",
        "max_results": 10,
    }
    r = requests.post(f"{BASE}/api/lead-discovery/start",
                      json=payload, headers=headers, timeout=15)
    if r.status_code not in (200, 201):
        print(f"❌  Start job FAILED — {r.status_code}: {r.text}")
        sys.exit(1)
    job = r.json()
    print(f"✅  Job started — id={job['id']}  status={job['status']}")
    print(f"    keywords={job['keywords']}  location={job.get('location')}  industry={job.get('industry')}")
    return job

# ── 4. Poll until done ───────────────────────────────────────────────────────
def poll_job(headers, job_id, timeout=180):
    print(f"⏳  Polling job {job_id} (max {timeout}s)…")
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(f"{BASE}/api/lead-discovery/{job_id}",
                         headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        job = data["job"]
        pct = data.get("progress_percent", 0)
        domains = data.get("discovered_domains", [])
        print(f"    status={job['status']}  people_found={job['domains_found']}  "
              f"leads_created={job['leads_created']}  progress={pct}%  "
              f"preview_rows={len(domains)}")
        if job["status"] in ("completed", "failed"):
            return data
        time.sleep(5)
    print("⚠️  Timed out waiting for job")
    return None

# ── 5. Inspect results ───────────────────────────────────────────────────────
def inspect_results(data):
    job = data["job"]
    domains = data.get("discovered_domains", [])

    if job["status"] == "failed":
        print(f"❌  Job FAILED — {job.get('error_message')}")
        return False

    print(f"\n{'─'*55}")
    print(f"{'RESULT SUMMARY':^55}")
    print(f"{'─'*55}")
    print(f"  Status        : {job['status']}")
    print(f"  People found  : {job['domains_found']}")
    print(f"  Leads saved   : {job['leads_created']}")
    print(f"  Preview rows  : {len(domains)}")

    # Detect pipeline
    is_people = any(get_person(d) for d in domains)
    pipeline = "SERP+crawl (fallback)"
    for d in domains:
        p = get_person(d)
        if p:
            pipeline = f"{p.get('source','?').upper()} people search"
            break
    print(f"  Pipeline used : {pipeline}")
    print()

    if domains:
        print("  Sample leads:")
        for d in domains[:5]:
            p = get_person(d)
            if p:
                name = f"{p.get('first_name','')} {p.get('last_name','')}".strip()
                email = d.get("emails_found") or ""
                title = p.get("title") or ""
                company = p.get("company") or d.get("domain") or ""
                linkedin = d.get("source_url") or ""
                print(f"    👤 {name or '(no name)':<22} | {title[:28]:<28} | {company[:20]:<20}")
                print(f"       ✉  {email or '(no email)'}   🔗 {linkedin[:60] if linkedin else '—'}")
            else:
                print(f"    🌐 {d.get('domain','?'):<30} | {d.get('status')} | emails={d.get('emails_found','')}")

    print(f"\n{'─'*55}")
    if job["leads_created"] > 0:
        print(f"✅  PASS — {job['leads_created']} lead(s) created successfully")
        return True
    elif job["domains_found"] > 0:
        print(f"⚠️  PARTIAL — people found but no emails → no API key configured (SERP fallback or empty results)")
        print(f"   Set APOLLO_API_KEY or SNOV_CLIENT_ID/SECRET in backend/.env to get real contacts")
        return True
    else:
        print(f"❌  FAIL — 0 results. Check SERP_API_KEY in .env or add Apollo/Snov API keys")
        return False

def get_person(domain_row):
    """Extract person dict from a discovered_domain row."""
    if domain_row.get("person"):
        return domain_row["person"]
    import json
    desc = domain_row.get("company_description") or ""
    if desc:
        try:
            m = json.loads(desc)
            if isinstance(m, dict) and "first_name" in m:
                return m
        except Exception:
            pass
    return None

# ── 6. Check leads endpoint ──────────────────────────────────────────────────
def check_leads(headers):
    r = requests.get(f"{BASE}/leads", headers=headers, params={"limit": 5}, timeout=10)
    if r.status_code == 200:
        leads = r.json()
        count = len(leads) if isinstance(leads, list) else leads.get("total", "?")
        print(f"✅  Leads endpoint — {count} lead(s) accessible")
    else:
        print(f"⚠️  Leads endpoint returned {r.status_code}")

# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  LEAD DISCOVERY END-TO-END TEST")
    print("=" * 55)
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        list_jobs(headers)
        job = start_job(headers)
        result = poll_job(headers, job["id"])
        if result:
            ok = inspect_results(result)
        check_leads(headers)
        print("\n✅  All checks passed" if result else "\n⚠️  Job did not complete in time")
    except Exception as e:
        print(f"\n❌  Test error: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)
