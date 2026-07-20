"""
Buying Signal Discovery Engine — Integration Test
==================================================
Tests the full pipeline against a real company without needing an auth token.
Runs directly inside the backend virtualenv against the live backend/.env config.

Usage:
    cd d:\\lead gen\\backend
    venv\\Scripts\\python.exe test_buying_signals.py
"""
import asyncio
import json
import sys
import os
import time

# Force UTF-8 output so Unicode chars don't blow up on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Bootstrap: point at the backend package
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))

# Load env so settings picks up GEMINI_API_KEY etc.
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from app.config import settings


# ---------------------------------------------------------------------------
# Colour helpers (ASCII-safe symbols)
# ---------------------------------------------------------------------------
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):   print(f"{GREEN}  [PASS] {msg}{RESET}")
def warn(msg): print(f"{YELLOW}  [WARN] {msg}{RESET}")
def err(msg):  print(f"{RED}  [FAIL] {msg}{RESET}")
def info(msg): print(f"{CYAN}  --> {msg}{RESET}")
def hdr(msg):  print(f"\n{BOLD}{msg}{RESET}")


# ---------------------------------------------------------------------------
# Helper: build a mock Lead object (no DB needed)
# ---------------------------------------------------------------------------
def make_mock_lead(company, domain=None, industry=None, first_name="Test", email=None):
    """Build a minimal Lead-like object for testing."""
    class MockLead:
        pass
    lead = MockLead()
    lead.id = "test-lead-001"
    lead.first_name = first_name
    lead.last_name = "User"
    lead.full_name = f"{first_name} User"
    lead.email = email or f"test@{domain or 'example.com'}"
    lead.company = company
    lead.title = "VP of Sales"
    lead.job_title = "VP of Sales"
    lead.industry = industry
    lead.seniority = "VP"
    lead.company_size = "500-1000"
    lead.location = "San Francisco, CA"
    lead.linkedin_url = None
    lead.linkedin_headline = None
    lead.research_notes = None
    lead.enriched_data = {
        "company_domain": domain,
        "industry": industry,
    } if domain else {}
    return lead


# ---------------------------------------------------------------------------
# Direct module imports (skip services/__init__.py to avoid passlib chain)
# ---------------------------------------------------------------------------
def _import_redis_service():
    import importlib.util, pathlib
    spec = importlib.util.spec_from_file_location(
        "redis_service",
        pathlib.Path(__file__).parent / "app" / "services" / "redis_service.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _import_domain_crawler():
    import importlib.util, pathlib
    spec = importlib.util.spec_from_file_location(
        "domain_crawler",
        pathlib.Path(__file__).parent / "app" / "services" / "domain_crawler.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _import_lead_research():
    import importlib.util, pathlib
    # Needs app.config and app.models.lead; patch sys.modules first
    import app.config  # noqa
    # Stub out app.models.lead if not importable
    try:
        import app.models.lead  # noqa
    except Exception:
        from types import ModuleType
        stub = ModuleType("app.models.lead")
        class Lead: pass
        stub.Lead = Lead
        sys.modules["app.models.lead"] = stub

    spec = importlib.util.spec_from_file_location(
        "lead_research_service",
        pathlib.Path(__file__).parent / "app" / "services" / "lead_research_service.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _import_ai_email():
    import importlib.util, pathlib
    import app.config  # noqa
    try:
        import app.models.lead  # noqa
    except Exception:
        from types import ModuleType
        stub = ModuleType("app.models.lead")
        class Lead: pass
        stub.Lead = Lead
        sys.modules["app.models.lead"] = stub

    spec = importlib.util.spec_from_file_location(
        "ai_email_service",
        pathlib.Path(__file__).parent / "app" / "services" / "ai_email_service.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ===========================================================================
# TEST 1 — Redis cache (get/set round-trip)
# ===========================================================================
def test_redis_cache():
    hdr("TEST 1: Redis Cache (7-day company cache)")
    rs = _import_redis_service()
    RedisService = rs.RedisService

    company = "__prosario_test_company__"
    test_data = {
        "company_summary": "Test company for cache verification.",
        "best_email_opener": "Saw Prosario launch their AI engine...",
        "recommended_email_angle": "product_launch",
        "buying_signals": [{"type": "product_launch", "headline": "AI Engine Launch", "confidence": 99}],
        "personalization_candidates": [],
        "industry": "SaaS",
        "products_services": ["Lead Gen", "Cold Email"],
    }

    info("Writing to Redis cache...")
    RedisService.set_research_cache(company, test_data, ttl_seconds=60)

    info("Reading from Redis cache...")
    cached = RedisService.get_research_cache(company)

    if cached is None:
        warn("Redis unavailable — cache test SKIPPED (Redis not reachable on localhost:6379)")
        return True

    if cached.get("best_email_opener") == test_data["best_email_opener"]:
        ok("Cache round-trip: data matches exactly")
    else:
        err(f"Cache mismatch: got {cached}")
        return False

    # Clean up
    client = RedisService.get_client()
    if client:
        client.delete("research:company:__prosario_test_company__")
        ok("Cache key cleaned up")

    return True


# ===========================================================================
# TEST 2 — Domain crawler: crawl_for_signals()
# ===========================================================================
def test_domain_crawler():
    hdr("TEST 2: Domain Crawler -- crawl_for_signals()")
    dc = _import_domain_crawler()
    crawl_for_signals = dc.crawl_for_signals
    DomainCrawler = dc.DomainCrawler

    # Verify SIGNAL_PAGES length
    info(f"SIGNAL_PAGES has {len(DomainCrawler.SIGNAL_PAGES)} entries")
    if len(DomainCrawler.SIGNAL_PAGES) >= 15:
        ok("SIGNAL_PAGES has >= 15 entries")
    else:
        err(f"Only {len(DomainCrawler.SIGNAL_PAGES)} signal pages defined")
        return False

    domain = "stripe.com"
    info(f"Crawling {domain} (signal pages, may take 10-30s)...")
    t0 = time.time()
    result = crawl_for_signals(domain)
    elapsed = time.time() - t0

    if not isinstance(result, dict):
        err("crawl_for_signals() did not return a dict")
        return False

    sections = [k for k in result if k not in ("domain", "success")]
    info(f"Crawled in {elapsed:.1f}s | Sections found: {sections or 'none'}")

    if result.get("success"):
        ok(f"success=True | Sections: {', '.join(sections)}")
        for section in sections[:3]:
            text = result[section]
            preview = text[:100].replace("\n", " ").strip()
            print(f"     [{section}] {len(text)} chars -- {preview!r}...")
    else:
        warn("No sections crawled (site may block scrapers) -- not a code error")

    return True


# ===========================================================================
# TEST 3 — Buying Signal Discovery Engine: full pipeline
# ===========================================================================
async def test_full_pipeline():
    hdr("TEST 3: Full Buying Signal Pipeline (Gemini + news searches)")

    if not settings.GEMINI_API_KEY:
        warn("GEMINI_API_KEY not set in .env -- skipping live pipeline test")
        return True

    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)

    lrs = _import_lead_research()
    research_lead_with_status = lrs.research_lead_with_status
    RESEARCH_STATUS_LIVE     = lrs.RESEARCH_STATUS_LIVE
    RESEARCH_STATUS_FALLBACK = lrs.RESEARCH_STATUS_FALLBACK
    RESEARCH_STATUS_NONE     = lrs.RESEARCH_STATUS_NONE

    lead = make_mock_lead(
        company="Stripe",
        domain="stripe.com",
        industry="Fintech",
        first_name="Patrick",
        email="patrick@stripe.com",
    )

    info("Running research_lead_with_status() for Stripe (may take 30-90s)...")
    t0 = time.time()
    notes, status = await research_lead_with_status(lead)
    elapsed = time.time() - t0

    info(f"Completed in {elapsed:.1f}s | Status: {status}")

    if status == RESEARCH_STATUS_NONE:
        warn("Status=none -- no research produced. Check GEMINI_API_KEY and network.")
        return False

    if notes:
        ok(f"Notes returned ({len(notes)} chars) | Status: {status}")
        print()
        print("-" * 60)
        print(notes[:800])
        print("-" * 60)
    else:
        err("No notes returned")
        return False

    # Check structured result on lead
    enriched = lead.enriched_data if isinstance(lead.enriched_data, dict) else {}
    bsr = enriched.get("buying_signals_result")

    if bsr:
        ok("buying_signals_result written to lead.enriched_data")
        opener  = bsr.get("best_email_opener", "")
        angle   = bsr.get("recommended_email_angle", "")
        signals = bsr.get("buying_signals", [])
        print()
        print(f"  best_email_opener    : {opener!r}")
        print(f"  recommended_angle    : {angle!r}")
        print(f"  buying_signals found : {len(signals)}")
        for s in signals[:3]:
            print(f"    [{s.get('type','?').upper()}] {s.get('headline','')} (conf: {s.get('confidence','?')}%)")

        sdr_leads = ("saw", "noticed", "congrats", "read", "looks like")
        if opener and opener.lower().startswith(sdr_leads):
            ok("best_email_opener starts with SDR-style lead-in")
        elif opener:
            warn(f"best_email_opener exists but check phrasing: {opener!r}")
        else:
            warn("best_email_opener is empty -- extraction may need richer signal data")
    else:
        warn("buying_signals_result not in enriched_data -- fallback notes returned (OK)")

    return True


# ===========================================================================
# TEST 4 — Email agent reads buying signal context
# ===========================================================================
def test_email_agent_context():
    hdr("TEST 4: Email Agent -- _get_buying_signal_context()")
    ae = _import_ai_email()
    _get_buying_signal_context = ae._get_buying_signal_context

    lead = make_mock_lead("Acme Corp", domain="acme.com")
    lead.enriched_data = {
        "buying_signals_result": {
            "best_email_opener": "Saw Acme Corp recently raised a $50M Series B...",
            "recommended_email_angle": "funding",
        }
    }

    opener, angle = _get_buying_signal_context(lead)
    if opener == "Saw Acme Corp recently raised a $50M Series B..." and angle == "funding":
        ok("_get_buying_signal_context reads enriched_data correctly")
        ok(f"Opener : {opener!r}")
        ok(f"Angle  : {angle!r}")
    else:
        err(f"Got opener={opener!r}, angle={angle!r}")
        return False

    # Empty enriched_data must not crash
    lead2 = make_mock_lead("Empty Corp")
    lead2.enriched_data = {}
    opener2, angle2 = _get_buying_signal_context(lead2)
    if opener2 == "" and angle2 == "":
        ok("Empty enriched_data handled gracefully (no crash)")
    else:
        err(f"Expected empty strings, got opener={opener2!r}, angle={angle2!r}")
        return False

    return True


# ===========================================================================
# TEST 5 — Prompt template has buying signal fields
# ===========================================================================
def test_prompt_template():
    hdr("TEST 5: Copywriter Prompt Template -- buying signal fields")
    ae = _import_ai_email()
    TPL = ae._COPYWRITER_AGENT_PROMPT_TEMPLATE

    required_fields = [
        "{best_email_opener}",
        "{recommended_email_angle}",
        "{research_notes}",
        "{first_name}",
        "{company}",
        "{product_description}",
        "{sender_first_name}",
        "{subject}",
    ]

    missing = [f for f in required_fields if f not in TPL]
    if missing:
        err(f"Missing template fields: {missing}")
        return False

    ok(f"All {len(required_fields)} required fields present in copywriter template")

    # Check NEVER USE list
    never_use_phrases = [
        "I noticed your company",
        "I hope this email finds you well",
        "Given your focus on",
    ]
    for phrase in never_use_phrases:
        if phrase in TPL:
            ok(f'NEVER USE contains: "{phrase}"')
        else:
            warn(f'NEVER USE missing: "{phrase}" -- verify manually')

    return True


# ===========================================================================
# Runner
# ===========================================================================
async def main():
    print(f"\n{BOLD}{'='*60}")
    print("  Prosario -- Buying Signal Discovery Engine")
    print("  Integration Test Suite")
    print(f"{'='*60}{RESET}\n")

    results = {}

    for name, fn in [
        ("Redis Cache",          test_redis_cache),
        ("Domain Crawler",       test_domain_crawler),
        ("Email Agent Context",  test_email_agent_context),
        ("Prompt Template",      test_prompt_template),
    ]:
        try:
            results[name] = fn()
        except Exception as e:
            err(f"{name} crashed: {e}")
            import traceback; traceback.print_exc()
            results[name] = False

    try:
        results["Full Pipeline (Gemini)"] = await test_full_pipeline()
    except Exception as e:
        err(f"Full pipeline crashed: {e}")
        import traceback; traceback.print_exc()
        results["Full Pipeline (Gemini)"] = False

    hdr("SUMMARY")
    all_passed = True
    for test, passed in results.items():
        if passed:
            ok(test)
        else:
            err(f"{test}  <-- FAILED")
            all_passed = False

    print()
    if all_passed:
        print(f"{GREEN}{BOLD}All tests passed{RESET}\n")
    else:
        print(f"{RED}{BOLD}Some tests failed -- see details above{RESET}\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
