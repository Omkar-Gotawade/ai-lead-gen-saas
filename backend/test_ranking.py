"""Unit test for the 4-dimension scoring system.

Run from d:\\lead gen\\backend:
    venv\\Scripts\\python.exe test_ranking.py
"""
import sys, ast, pathlib, importlib.util
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from dotenv import load_dotenv; load_dotenv('.env')

GREEN = "\033[92m"; RED = "\033[91m"; CYAN = "\033[96m"; BOLD = "\033[1m"; RESET = "\033[0m"
ok   = lambda m: print(f"{GREEN}  [PASS] {m}{RESET}")
err  = lambda m: print(f"{RED}  [FAIL] {m}{RESET}")
info = lambda m: print(f"{CYAN}  --> {m}{RESET}")

# ============================================================
# 1. Syntax check
# ============================================================
print(f"\n{BOLD}[1] Syntax check{RESET}")
for f in ['app/services/lead_research_service.py', 'app/services/ai_email_service.py']:
    src = pathlib.Path(f).read_text(encoding='utf-8')
    try:
        ast.parse(src)
        ok(f"SYNTAX OK  {f}")
    except SyntaxError as e:
        err(f"SYNTAX ERR {f}: {e}")
        sys.exit(1)

# ============================================================
# 2. Load modules
# ============================================================
print(f"\n{BOLD}[2] Module imports{RESET}")

# Import directly from file to bypass services/__init__.py -> auth -> email-validator chain
_BASE = pathlib.Path(__file__).parent

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    # Pre-register so relative imports inside the module resolve
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m

# Register app.config so lead_research_service can import it
import app.config  # noqa — only config, no heavy deps
lrs = _load('app.services.lead_research_service',
            _BASE / 'app' / 'services' / 'lead_research_service.py')
ok("lead_research_service imported")

aes = _load('app.services.ai_email_service',
            _BASE / 'app' / 'services' / 'ai_email_service.py')
ok("ai_email_service imported")

# ============================================================
# 3. Verify new symbols exist
# ============================================================
print(f"\n{BOLD}[3] New symbols{RESET}")
assert hasattr(lrs, 'BUSINESS_IMPACT_DEFAULTS'), 'missing BUSINESS_IMPACT_DEFAULTS'
assert hasattr(lrs, 'W_CONFIDENCE'),             'missing W_CONFIDENCE'
assert hasattr(lrs, '_compute_recency_score'),   'missing _compute_recency_score'
assert hasattr(lrs, '_rank_signals'),            'missing _rank_signals'
assert hasattr(aes, '_get_buying_signal_context'), 'missing _get_buying_signal_context'
ok("All new symbols present")

weights_sum = lrs.W_CONFIDENCE + lrs.W_CAMPAIGN_RELEVANCE + lrs.W_RECENCY + lrs.W_BUSINESS_IMPACT
assert abs(weights_sum - 1.0) < 0.001, f"Weights must sum to 1.0, got {weights_sum}"
ok(f"Weights sum to 1.0  (conf={lrs.W_CONFIDENCE} + rel={lrs.W_CAMPAIGN_RELEVANCE} + rec={lrs.W_RECENCY} + imp={lrs.W_BUSINESS_IMPACT})")

# ============================================================
# 4. Recency scoring
# ============================================================
print(f"\n{BOLD}[4] Recency scoring{RESET}")
cases = [
    ('2025-01', 0,   'Old date ~18 months ago -> 0'),
    ('',        50,  'Unknown date -> neutral 50'),
    ('2026-07', 80,  'Current month (1st is ~13 days ago) -> >= 80'),
    ('2026-06', 50,  'Last month    -> >= 50'),
    ('2024-01', 0,   'Very old 2024-01 -> 0'),
]
for date_str, min_val, label in cases:
    score = lrs._compute_recency_score(date_str)
    if score >= min_val:
        ok(f"{label} -> {score}")
    else:
        err(f"{label}: expected >={min_val}, got {score}")
        sys.exit(1)

# ============================================================
# 5. _rank_signals: key correctness test
#    Old high-confidence funding (18 months ago) must NOT beat
#    recent high-relevance hiring or product_launch
# ============================================================
print(f"\n{BOLD}[5] Ranking: recency+relevance must beat old confidence{RESET}")

test_result = {
    'company_summary': 'Acme Corp builds widgets.',
    'industry': 'SaaS',
    'products_services': ['widgets'],
    'buying_signals': [
        {
            'type': 'funding',
            'headline': 'Series B raised $50M',
            'description': 'Raised $50M in Series B',
            'date': '2025-01',          # 18 months ago -> recency = 0
            'confidence': 95,
            'campaign_relevance': 40,   # old funding, not very relevant
        },
        {
            'type': 'hiring',
            'headline': 'Hiring 50 support agents',
            'description': 'Expanding support team aggressively',
            'date': '2026-07',          # current month -> recency = 90+
            'confidence': 80,
            'campaign_relevance': 95,   # directly relevant for AI support SaaS
        },
        {
            'type': 'product_launch',
            'headline': 'Launched new AI assistant feature',
            'description': 'New AI-powered customer assistant launched',
            'date': '2026-06',          # 1 month ago
            'confidence': 90,
            'campaign_relevance': 92,
        },
    ],
    'best_email_openers': [
        'Saw Acme hiring 50 support agents this month.',
        'Caught the news about Acme expanding their support team.',
        'Looks like Acme has been scaling support aggressively.',
    ],
    'recommended_email_angle': 'hiring',
}

ranked = lrs._rank_signals(test_result)
signals = ranked['buying_signals']

info("Ranked signals (highest final_score first):")
for i, s in enumerate(signals, 1):
    print(
        f"    #{i} [{s['type'].upper():20}] "
        f"final={s['final_score']:3} | "
        f"conf={s['confidence']:3} | "
        f"relevance={s['campaign_relevance']:3} | "
        f"recency={s['recency_score']:3} | "
        f"impact={s['business_impact']:3}"
    )

top = signals[0]
if top['type'] in ('hiring', 'product_launch'):
    ok(f"Winner: {top['type']} (score {top['final_score']}) -- old funding correctly de-ranked")
else:
    err(f"Expected hiring or product_launch to win, got {top['type']} (score {top['final_score']})")
    sys.exit(1)

# ============================================================
# 6. recommended_signal structure
# ============================================================
print(f"\n{BOLD}[6] recommended_signal / alternative_signals{RESET}")
rec = ranked['recommended_signal']
required_keys = ['type', 'headline', 'summary', 'confidence', 'recency_score',
                 'campaign_relevance', 'business_impact', 'final_score', 'reason']
for k in required_keys:
    assert k in rec, f"recommended_signal missing key: {k}"
ok(f"recommended_signal has all {len(required_keys)} required keys")
ok(f"  headline    : {rec['headline']}")
ok(f"  final_score : {rec['final_score']}")
ok(f"  reason      : {rec['reason']}")

alts = ranked['alternative_signals']
assert len(alts) == 2, f"Expected 2 alternative_signals, got {len(alts)}"
ok(f"alternative_signals: {[a['headline'] for a in alts]}")

# ============================================================
# 7. best_email_openers (3 variants)
# ============================================================
print(f"\n{BOLD}[7] 3 opener variants{RESET}")
openers = ranked['best_email_openers']
assert len(openers) == 3, f"Expected 3 openers, got {len(openers)}"
ok("3 openers returned")
for i, o in enumerate(openers, 1):
    ok(f"  Option {i}: {o}")

# backward-compat single field
assert ranked['best_email_opener'] == openers[0]
ok(f"best_email_opener (backward-compat) == openers[0]")

# ============================================================
# 8. _get_buying_signal_context reads recommended_signal
# ============================================================
print(f"\n{BOLD}[8] Email agent reads recommended_signal{RESET}")

class FakeLead:
    enriched_data = {
        'buying_signals_result': {
            'recommended_signal': {
                'type': 'hiring',
                'headline': 'Hiring 50 support agents',
                'final_score': 91,
            },
            'best_email_openers': [
                'Saw Acme hiring 50 support agents this month.',
                'Caught the news about Acme expanding support.',
                'Looks like Acme is scaling support aggressively.',
            ],
            'recommended_email_angle': 'hiring',
            'best_email_opener': 'LEGACY OPENER -- should not be chosen',
        }
    }

opener, angle = aes._get_buying_signal_context(FakeLead())
assert opener == 'Saw Acme hiring 50 support agents this month.', (
    f"Expected openers[0] but got: {opener!r}"
)
assert angle == 'hiring'
ok(f"opener : {opener!r}")
ok(f"angle  : {angle!r}")

# Empty enriched_data must not crash
class EmptyLead:
    enriched_data = {}
o2, a2 = aes._get_buying_signal_context(EmptyLead())
assert o2 == "" and a2 == ""
ok("Empty enriched_data: returns ('', '') without error")

# ============================================================
print(f"\n{GREEN}{BOLD}=== ALL TESTS PASSED ==={RESET}\n")
