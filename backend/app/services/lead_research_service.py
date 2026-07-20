"""Buying Signal Discovery Engine — Lead Research Service.

Researches companies like an experienced SDR:
  1. Crawls the company website (blog, careers, press, news, products, etc.)
  2. Runs 5 targeted news searches via Gemini web-search grounding
  3. Feeds all raw content to a Gemini extraction prompt that returns a
     structured JSON with ranked buying signals, personalisation candidates,
     a ready-to-use best_email_opener, and a recommended_email_angle.
  4. Caches the structured result per company for 7 days in Redis.

All public API signatures are identical to the original service:
    research_lead_with_status(lead) -> Tuple[Optional[str], str]
    research_lead(lead)             -> Optional[str]
    research_lead_sync(lead)        -> Optional[str]

The structured buying-signal JSON is also written to
    lead.enriched_data["buying_signals_result"]
so the Cold Email Agent can consume best_email_opener directly.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import google.generativeai as genai

from app.config import settings
from app.models.lead import Lead

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Status constants (kept identical to original)
# ---------------------------------------------------------------------------
RESEARCH_STATUS_LIVE = "live"
RESEARCH_STATUS_FALLBACK = "fallback"
RESEARCH_STATUS_NONE = "none"

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------
RESEARCH_MODEL = (
    (getattr(settings, "GEMINI_RESEARCH_MODEL", "") or "").strip()
    or (getattr(settings, "GEMINI_MODEL", "") or "").strip()
    or "gemini-1.5-flash"
)
RESEARCH_USE_WEB_SEARCH = bool(getattr(settings, "GEMINI_RESEARCH_ENABLE_WEB_SEARCH", True))
MAX_RETRIES = 3
MIN_NOTES_LENGTH = 40

# ---------------------------------------------------------------------------
# Scoring tables for the 4-dimension ranking system
# ---------------------------------------------------------------------------

# Business Impact defaults — how important is this event type for outbound sales?
BUSINESS_IMPACT_DEFAULTS: Dict[str, int] = {
    "funding":             100,
    "acquisition":          95,
    "product_launch":       95,
    "expansion":            90,
    "hiring":               90,
    "partnership":          85,
    "new_office":           80,
    "conference":           60,
    "award":                40,
    "blog":                 30,
    "company_description":  10,
}

# Final score weights
W_CONFIDENCE        = 0.30
W_CAMPAIGN_RELEVANCE = 0.30
W_RECENCY           = 0.20
W_BUSINESS_IMPACT   = 0.20

# Legacy priority list kept for fallback ordering only
SIGNAL_PRIORITY = list(BUSINESS_IMPACT_DEFAULTS.keys())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_response_text(response) -> str:
    """Extract text safely across SDK response variants."""
    text = getattr(response, "text", None)
    if isinstance(text, str):
        return text.strip()

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) if content else None
        if not parts:
            continue
        for part in parts:
            part_text = getattr(part, "text", None)
            if isinstance(part_text, str) and part_text.strip():
                return part_text.strip()

    return ""


def _is_quota_or_rate_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(
        marker in message
        for marker in [
            "429",
            "quota exceeded",
            "resourceexhausted",
            "please retry in",
            "retry_delay",
            "rate limit",
        ]
    )


def _extract_retry_seconds(exc: Exception) -> float:
    message = str(exc)
    retry_in = re.search(r"retry in\s+(\d+(?:\.\d+)?)s", message, flags=re.IGNORECASE)
    if retry_in:
        return max(0.5, float(retry_in.group(1)))
    proto_seconds = re.search(r"seconds:\s*(\d+)", message, flags=re.IGNORECASE)
    if proto_seconds:
        return max(0.5, float(proto_seconds.group(1)))
    return 2.0


def _infer_company_domain(lead: Lead) -> Optional[str]:
    """Try to derive the company domain from enriched_data or lead fields."""
    enriched = lead.enriched_data if isinstance(lead.enriched_data, dict) else {}

    # 1. Explicitly stored domain
    domain = enriched.get("company_domain") or enriched.get("domain")
    if domain:
        return str(domain).strip()

    # 2. Derive from lead email (rough heuristic)
    if lead.email:
        parts = lead.email.split("@")
        if len(parts) == 2:
            domain_part = parts[1].lower()
            # Skip common free providers
            if not any(
                provider in domain_part
                for provider in ["gmail", "yahoo", "hotmail", "outlook", "proton"]
            ):
                return domain_part

    return None


# ---------------------------------------------------------------------------
# Step 1: Company website crawl (non-blocking, errors isolated)
# ---------------------------------------------------------------------------

def _crawl_company_website(domain: str) -> Dict[str, str]:
    """Crawl signal-rich pages on the company website.

    Returns a dict of section → text.  Always returns a dict (never raises).
    """
    try:
        from app.services.domain_crawler import crawl_for_signals
        result = crawl_for_signals(domain)
        if isinstance(result, dict):
            # Remove meta keys; keep only section text
            return {
                k: v for k, v in result.items()
                if k not in ("domain", "success") and isinstance(v, str) and v.strip()
            }
    except Exception as exc:
        logger.warning("Website crawl failed for %s: %s", domain, exc)
    return {}


# ---------------------------------------------------------------------------
# Step 2: Targeted news searches via Gemini web-search grounding
# ---------------------------------------------------------------------------

NEWS_SEARCH_QUERIES = [
    "{company} latest news",
    "{company} funding OR investment",
    "{company} partnership OR acquisition",
    "{company} product launch OR expansion OR new office",
    "{company} hiring OR careers OR job openings",
]

NEWS_SEARCH_PROMPT = """Search the web for: "{query}"

Return a concise summary (max 200 words) of the most recent and relevant results found.
Focus on concrete facts: dates, numbers, names, announcements.
If nothing useful is found, return the single word: NONE
"""


def _run_single_search(query: str, model_name: str) -> Optional[str]:
    """Run one web-grounded Gemini search and return a text summary."""
    try:
        model = genai.GenerativeModel(model_name=model_name, tools=["google_search"])
    except Exception:
        model = genai.GenerativeModel(model_name=model_name)

    response = model.generate_content(
        NEWS_SEARCH_PROMPT.format(query=query)
    )
    text = _safe_response_text(response)
    if not text or text.strip().upper() == "NONE" or len(text) < 20:
        return None
    return text


def _collect_news_signals(company: str, model_name: str) -> Dict[str, str]:
    """Run all 5 news searches and return {query_label: summary}.

    Each search is independent — failures are skipped silently.
    """
    results: Dict[str, str] = {}
    labels = ["latest_news", "funding", "partnership_acquisition", "expansion_launch", "hiring"]

    for label, query_template in zip(labels, NEWS_SEARCH_QUERIES):
        query = query_template.format(company=company)
        try:
            summary = _run_single_search(query, model_name)
            if summary:
                results[label] = summary
            time.sleep(0.5)  # small buffer between searches
        except Exception as exc:
            if _is_quota_or_rate_error(exc):
                logger.warning("News search quota hit for '%s': %s", query, exc)
                break  # stop further searches on quota error
            logger.debug("News search skipped for '%s': %s", query, exc)
            continue

    return results


# ---------------------------------------------------------------------------
# Step 3: Gemini buying-signal extraction prompt
# ---------------------------------------------------------------------------

_EXTRACTION_PROMPT = """You are an expert B2B SDR researcher and sales strategist.

You have been given raw content from a company's website and recent news searches.

COMPANY NAME: {company}
INDUSTRY (if known): {industry}

=== WEBSITE CONTENT ===
{website_content}

=== RECENT NEWS ===
{news_content}

=== YOUR TASK ===

Analyse ALL the content and extract buying signals ranked by SALES OPPORTUNITY VALUE — not just
confidence. An experienced SDR asks: "What is the strongest reason to contact this company TODAY?"

BUYING SIGNAL TYPES:
funding | acquisition | product_launch | expansion | hiring | partnership | new_office |
conference | award | blog | company_description

FOR EACH SIGNAL score TWO dimensions:

1. confidence (0-100): How certain are you this event actually happened?
2. campaign_relevance (0-100): How valuable is this signal as a cold B2B outreach
   conversation starter? Ask yourself: "Would a real SDR open with this?"
   - Directly actionable recent event → 90-100
   - Relevant but indirect           → 60-80
   - Generic or old                  → 0-40

RULES:
- Extract ONLY signals supported by the content provided.
- Prefer signals from the last 12 months. Note the date precisely if known.
- date format: YYYY-MM preferred, YYYY acceptable, leave blank if unknown.
- For best_email_openers: generate EXACTLY 3 variants using the highest-value signal.
  Each must start with a different lead-in: "Saw", "Noticed" / "Caught", "Looks like".
  Never start with "I noticed your company" or any generic opener.
- recommended_email_angle: the signal TYPE of the best opener.

FALLBACK: If no concrete buying signals found, use company description as fallback signal.

RESPOND WITH VALID JSON ONLY — no markdown, no explanation, no trailing commas:

{{
  "company_summary": "2-3 sentence description of what the company does",
  "industry": "the company's primary industry",
  "products_services": ["list", "of", "key", "products"],
  "buying_signals": [
    {{
      "type": "product_launch",
      "headline": "Short factual headline (max 15 words)",
      "description": "1-2 sentence detail with specifics (dates, numbers, names)",
      "source": "URL or source name if known, else blank",
      "date": "YYYY-MM or YYYY or blank",
      "confidence": 90,
      "campaign_relevance": 85
    }}
  ],
  "best_email_openers": [
    "Saw {company} recently ...",
    "Caught the announcement about {company} ...",
    "Looks like {company} has been ..."
  ],
  "recommended_email_angle": "product_launch"
}}
"""


def _extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Parse JSON from Gemini output, tolerating markdown fences."""
    text = text.strip()
    # Strip markdown fences
    text = re.sub(r"^```[a-z]*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n?```$", "", text)
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find the first {...} block
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def _run_extraction(
    company: str,
    industry: str,
    website_sections: Dict[str, str],
    news_signals: Dict[str, str],
    model_name: str,
) -> Optional[Dict[str, Any]]:
    """Call Gemini to extract structured buying signals from collected content."""

    # Build website content block
    website_parts = []
    section_order = ["home", "about", "blog", "press", "careers", "products", "services", "case_studies", "partners"]
    for section in section_order:
        if section in website_sections:
            label = section.replace("_", " ").title()
            website_parts.append(f"[{label}]\n{website_sections[section][:2000]}")
    # Any remaining sections not in order list
    for section, text in website_sections.items():
        if section not in section_order:
            website_parts.append(f"[{section.title()}]\n{text[:1000]}")

    website_content = "\n\n".join(website_parts) if website_parts else "No website content available."

    # Build news content block
    news_parts = []
    label_map = {
        "latest_news": "Latest News",
        "funding": "Funding & Investment",
        "partnership_acquisition": "Partnerships & Acquisitions",
        "expansion_launch": "Product Launches & Expansions",
        "hiring": "Hiring Signals",
    }
    for label, text in news_signals.items():
        news_parts.append(f"[{label_map.get(label, label)}]\n{text}")

    news_content = "\n\n".join(news_parts) if news_parts else "No recent news found."

    prompt = _EXTRACTION_PROMPT.format(
        company=company,
        industry=industry or "Unknown",
        website_content=website_content,
        news_content=news_content,
    )

    try:
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content(prompt)
        raw = _safe_response_text(response)
        if not raw:
            return None
        return _extract_json_from_text(raw)
    except Exception as exc:
        logger.warning("Extraction prompt failed for %s: %s", company, exc)
        return None


# ---------------------------------------------------------------------------
# Step 4: Recency scoring helper
# ---------------------------------------------------------------------------

def _compute_recency_score(date_str: str) -> int:
    """Convert a date string (YYYY-MM or YYYY) into a 0-100 recency score.

    Scoring:
        0-3 days   → 100
        4-7 days   → 95
        8-30 days  → 90 – 70  (linear)
        31-60 days → 70 – 50  (linear)
        61-90 days → 50 – 20  (linear)
        91-180d    → 20 – 5   (linear)
        >180 days  → 0
        unknown    → 50  (neutral default)
    """
    import datetime
    if not date_str or not date_str.strip():
        return 50  # neutral — we simply don't know

    today = datetime.date.today()
    try:
        if re.match(r"^\d{4}-\d{2}$", date_str.strip()):
            parts = date_str.strip().split("-")
            event_date = datetime.date(int(parts[0]), int(parts[1]), 1)
        elif re.match(r"^\d{4}$", date_str.strip()):
            event_date = datetime.date(int(date_str.strip()), 1, 1)
        else:
            return 50
    except (ValueError, TypeError):
        return 50

    days = (today - event_date).days
    if days < 0:
        days = 0  # future date — treat as very recent

    if days <= 3:   return 100
    if days <= 7:   return 95
    if days <= 30:  return max(70, 90 - int((days - 7) * 20 / 23))
    if days <= 60:  return max(50, 70 - int((days - 30) * 20 / 30))
    if days <= 90:  return max(20, 50 - int((days - 60) * 30 / 30))
    if days <= 180: return max(5,  20 - int((days - 90) * 15 / 90))
    return 0


# ---------------------------------------------------------------------------
# Step 5: Sales Opportunity Ranking Engine
# ---------------------------------------------------------------------------

def _rank_signals(result: Dict[str, Any]) -> Dict[str, Any]:
    """Score every buying signal on 4 dimensions and build ranked output.

    Formula:
        final_score = 0.30 * confidence
                    + 0.30 * campaign_relevance
                    + 0.20 * recency_score
                    + 0.20 * business_impact
    """
    signals = result.get("buying_signals", [])

    scored: List[Dict[str, Any]] = []
    for sig in signals:
        sig_type = (sig.get("type") or "company_description").lower()

        confidence       = int(sig.get("confidence", 50))
        campaign_rel     = int(sig.get("campaign_relevance",
                               BUSINESS_IMPACT_DEFAULTS.get(sig_type, 50)))  # fallback to business_impact
        recency          = _compute_recency_score(sig.get("date", ""))
        business_impact  = int(sig.get("business_impact",
                               BUSINESS_IMPACT_DEFAULTS.get(sig_type, 50)))

        final_score = round(
            W_CONFIDENCE        * confidence
            + W_CAMPAIGN_RELEVANCE * campaign_rel
            + W_RECENCY           * recency
            + W_BUSINESS_IMPACT   * business_impact
        )

        scored.append({
            **sig,
            "confidence":        confidence,
            "campaign_relevance": campaign_rel,
            "recency_score":     recency,
            "business_impact":   business_impact,
            "final_score":       final_score,
        })

    # Sort highest final_score first
    scored.sort(key=lambda s: s["final_score"], reverse=True)
    result["buying_signals"] = scored

    # -----------------------------------------------------------------------
    # Build recommended_signal (rank #1)
    # -----------------------------------------------------------------------
    if scored:
        top = scored[0]
        top_type = (top.get("type") or "").lower()
        result["recommended_signal"] = {
            "type":              top.get("type", ""),
            "headline":          top.get("headline", ""),
            "summary":           top.get("description", ""),
            "confidence":        top["confidence"],
            "recency_score":     top["recency_score"],
            "campaign_relevance": top["campaign_relevance"],
            "business_impact":   top["business_impact"],
            "final_score":       top["final_score"],
            "reason": (
                f"Ranked #1 by weighted score ({top['final_score']}/100). "
                f"Type: {top_type} | Recency: {top['recency_score']} | "
                f"Campaign relevance: {top['campaign_relevance']} | "
                f"Business impact: {top['business_impact']}."
            ),
        }

        # alternative_signals = ranks #2 and #3
        result["alternative_signals"] = [
            {
                "type":        s.get("type", ""),
                "headline":    s.get("headline", ""),
                "summary":     s.get("description", ""),
                "final_score": s["final_score"],
            }
            for s in scored[1:3]
        ]
    else:
        result.setdefault("recommended_signal", {})
        result.setdefault("alternative_signals", [])

    # -----------------------------------------------------------------------
    # Ensure best_email_openers list (3 variants)
    # -----------------------------------------------------------------------
    openers = result.get("best_email_openers") or []
    # Migrate legacy single-opener field
    legacy = (result.get("best_email_opener") or "").strip()
    if legacy and legacy not in openers:
        openers = [legacy] + openers

    # If Gemini returned fewer than 3, generate fallback variants from top signal
    if len(openers) < 3 and scored:
        top = scored[0]
        headline = (top.get("headline") or top.get("description") or "").rstrip(".")
        company_name = result.get("company_summary", "").split()[0] if result.get("company_summary") else ""
        fallbacks = [
            f"Saw {headline}.",
            f"Caught the news about {headline.lower()}.",
            f"Looks like {company_name} has been active — {headline.lower()}.",
        ]
        for fb in fallbacks:
            if fb not in openers:
                openers.append(fb)
            if len(openers) >= 3:
                break

    result["best_email_openers"] = openers[:3]
    # Keep backward-compat single field pointing at the best one
    result["best_email_opener"] = openers[0] if openers else ""

    return result


# ---------------------------------------------------------------------------
# Step 5: Convert structured result → plain-text research notes
# ---------------------------------------------------------------------------

def _structured_to_notes(result: Dict[str, Any], company: str) -> str:
    """Convert the structured buying-signal JSON into plain-text notes.

    Keeps backwards-compatibility: existing code that reads lead.research_notes
    still gets useful, human-readable text.
    """
    lines: List[str] = []

    # --- Best openers (new ranked format) ---
    openers = result.get("best_email_openers") or []
    legacy_opener = result.get("best_email_opener") or ""
    if openers:
        lines.append(f"BEST OPENER: {openers[0]}")
        for i, alt in enumerate(openers[1:], 2):
            lines.append(f"OPENER OPTION {i}: {alt}")
    elif legacy_opener:
        lines.append(f"BEST OPENER: {legacy_opener}")

    angle = result.get("recommended_email_angle", "")
    if angle:
        lines.append(f"EMAIL ANGLE: {angle}")

    # --- Recommended signal (rank #1) ---
    rec = result.get("recommended_signal")
    if rec and rec.get("headline"):
        fs = rec.get('final_score', '?')
        lines.append(
            f"\nRECOMMENDED SIGNAL (score {fs}/100):"
        )
        lines.append(f"  [{rec.get('type','').upper()}] {rec.get('headline','')}")
        lines.append(f"  {rec.get('summary','')}")
        lines.append(
            f"  Confidence:{rec.get('confidence','?')} | "
            f"Recency:{rec.get('recency_score','?')} | "
            f"Relevance:{rec.get('campaign_relevance','?')} | "
            f"Impact:{rec.get('business_impact','?')}"
        )

    # --- Alternative signals (ranks #2–3) ---
    alts = result.get("alternative_signals", [])
    if alts:
        lines.append("\nALTERNATIVE SIGNALS:")
        for i, alt in enumerate(alts, 2):
            fs = alt.get('final_score', '?')
            lines.append(
                f"  #{i} [{alt.get('type','').upper()}] "
                f"{alt.get('headline','')} (score {fs}/100)"
            )

    # --- All signals with scores ---
    signals = result.get("buying_signals", [])
    if signals:
        lines.append("\nALL RANKED SIGNALS:")
        for sig in signals[:5]:
            sig_type = (sig.get("type") or "").upper()
            headline  = sig.get("headline") or ""
            date      = sig.get("date") or ""
            date_str  = f" ({date})" if date else ""
            fs        = sig.get("final_score", "?")
            lines.append(f"  [{sig_type}]{date_str} {headline} [final:{fs}]")

    summary = result.get("company_summary", "")
    if summary:
        lines.append(f"\nCOMPANY: {summary}")

    products = result.get("products_services", [])
    if products:
        lines.append(f"PRODUCTS/SERVICES: {', '.join(products[:5])}")

    return "\n".join(lines) if lines else ""


# ---------------------------------------------------------------------------
# Main orchestration — full pipeline
# ---------------------------------------------------------------------------

def _run_buying_signal_pipeline(lead: Lead, model_name: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Run the complete buying-signal discovery pipeline synchronously.

    Returns (notes_text, structured_result) or None if everything fails.
    """
    company = (lead.company or "").strip()
    if not company:
        return None

    # --- Cache check ---
    try:
        from app.services.redis_service import RedisService
        cached = RedisService.get_research_cache(company)
        if cached:
            notes = _structured_to_notes(cached, company)
            if notes:
                logger.info("Returning cached buying-signal research for %s", company)
                return notes, cached
    except Exception as exc:
        logger.debug("Cache read error for %s: %s", company, exc)

    # --- Collect data from all sources ---
    industry = lead.industry or (
        (lead.enriched_data or {}).get("industry") if isinstance(lead.enriched_data, dict) else ""
    ) or ""

    # Source A: Website crawl
    website_sections: Dict[str, str] = {}
    domain = _infer_company_domain(lead)
    if domain:
        logger.info("Crawling website for %s (%s)", company, domain)
        website_sections = _crawl_company_website(domain)

    # Source B: News searches (only if web search enabled)
    news_signals: Dict[str, str] = {}
    if RESEARCH_USE_WEB_SEARCH:
        logger.info("Running news searches for %s", company)
        news_signals = _collect_news_signals(company, model_name)

    # If we have no data at all, bail early
    if not website_sections and not news_signals:
        logger.warning("No data collected for %s — skipping extraction", company)
        return None

    # --- Extract buying signals ---
    logger.info("Running buying-signal extraction for %s", company)
    result = _run_extraction(company, industry, website_sections, news_signals, model_name)
    if not result:
        return None

    # --- Rank and finalise ---
    result = _rank_signals(result)

    # --- Store structured result on lead ---
    try:
        enriched = lead.enriched_data if isinstance(lead.enriched_data, dict) else {}
        enriched["buying_signals_result"] = result
        lead.enriched_data = enriched
    except Exception:
        pass  # never block on this

    # --- Cache the result ---
    try:
        from app.services.redis_service import RedisService
        RedisService.set_research_cache(company, result)
    except Exception as exc:
        logger.debug("Cache write error for %s: %s", company, exc)

    notes = _structured_to_notes(result, company)
    return (notes, result) if notes else None


# ---------------------------------------------------------------------------
# Fallback — identical to original (never fails)
# ---------------------------------------------------------------------------

def _build_local_fallback_notes(lead: Lead) -> Optional[str]:
    """Deterministic fallback using locally available lead data."""
    signals = []

    if lead.job_title or lead.title:
        signals.append(f"- Role focus: {lead.job_title or lead.title}")
    if lead.company:
        signals.append(f"- Company: {lead.company}")
    if lead.industry:
        signals.append(f"- Industry: {lead.industry}")
    if lead.seniority:
        signals.append(f"- Seniority: {lead.seniority}")
    if lead.company_size:
        signals.append(f"- Company size: {lead.company_size}")
    if lead.linkedin_headline:
        signals.append(f"- LinkedIn headline: {lead.linkedin_headline}")

    enriched_data = lead.enriched_data if isinstance(lead.enriched_data, dict) else {}
    company_summary = enriched_data.get("company_summary")
    key_insights = enriched_data.get("key_insights")
    pain_points = enriched_data.get("pain_points")

    if company_summary:
        signals.append(f"- Company summary: {company_summary}")
    if key_insights:
        signals.append(f"- Key insights: {key_insights}")
    if isinstance(pain_points, list) and pain_points:
        signals.append(f"- Potential pain points: {', '.join(str(p) for p in pain_points[:4])}")

    if not signals:
        return None

    return "\n".join(["Research fallback (local context):", *signals])


# ---------------------------------------------------------------------------
# Retry wrapper (preserved from original)
# ---------------------------------------------------------------------------

def _run_pipeline_with_retry(lead: Lead, model_name: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Run _run_buying_signal_pipeline with exponential back-off on quota errors."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return _run_buying_signal_pipeline(lead, model_name)
        except Exception as exc:
            if not _is_quota_or_rate_error(exc):
                logger.warning(
                    "Buying signal pipeline failed for %s (attempt %d): %s",
                    lead.company, attempt, exc,
                )
                return None

            if attempt >= MAX_RETRIES:
                logger.warning(
                    "Buying signal pipeline retries exhausted for %s: %s",
                    lead.company, exc,
                )
                return None

            wait = min(30.0, _extract_retry_seconds(exc) * (2 ** (attempt - 1)))
            logger.warning(
                "Rate-limited for %s, retrying in %.1fs (attempt %d/%d)",
                lead.company, wait, attempt, MAX_RETRIES,
            )
            time.sleep(wait)

    return None


# ---------------------------------------------------------------------------
# Public API — signatures IDENTICAL to original
# ---------------------------------------------------------------------------

async def research_lead_with_status(lead: Lead) -> Tuple[Optional[str], str]:
    """Research a lead and return (notes, status_indicator).

    This is the primary entry-point called by the route layer.
    """
    if not settings.GEMINI_API_KEY:
        local_notes = _build_local_fallback_notes(lead)
        return local_notes, (RESEARCH_STATUS_FALLBACK if local_notes else RESEARCH_STATUS_NONE)

    if not lead.company:
        local_notes = _build_local_fallback_notes(lead)
        return local_notes, (RESEARCH_STATUS_FALLBACK if local_notes else RESEARCH_STATUS_NONE)

    genai.configure(api_key=settings.GEMINI_API_KEY)

    # Primary path: full buying-signal pipeline
    pipeline_result = await asyncio.to_thread(
        _run_pipeline_with_retry,
        lead,
        RESEARCH_MODEL,
    )
    if pipeline_result:
        notes, _structured = pipeline_result
        if notes and len(notes) >= MIN_NOTES_LENGTH:
            return notes, RESEARCH_STATUS_LIVE

    # Secondary fallback: try the configured model without the full pipeline
    fallback_model = (getattr(settings, "GEMINI_MODEL", "") or "").strip()
    if fallback_model and fallback_model != RESEARCH_MODEL:
        pipeline_result = await asyncio.to_thread(
            _run_pipeline_with_retry,
            lead,
            fallback_model,
        )
        if pipeline_result:
            notes, _structured = pipeline_result
            if notes and len(notes) >= MIN_NOTES_LENGTH:
                return notes, RESEARCH_STATUS_FALLBACK

    # Final path: deterministic local notes
    local_notes = _build_local_fallback_notes(lead)
    if local_notes:
        return local_notes, RESEARCH_STATUS_FALLBACK

    return None, RESEARCH_STATUS_NONE


async def research_lead(lead: Lead) -> Optional[str]:
    """Backwards-compatible async API returning notes only."""
    notes, _ = await research_lead_with_status(lead)
    return notes


def research_lead_sync(lead: Lead) -> Optional[str]:
    """Synchronous wrapper for Celery / background task contexts."""
    if not settings.GEMINI_API_KEY or not lead.company:
        return _build_local_fallback_notes(lead)

    genai.configure(api_key=settings.GEMINI_API_KEY)

    pipeline_result = _run_pipeline_with_retry(lead, RESEARCH_MODEL)
    if pipeline_result:
        notes, _structured = pipeline_result
        if notes and len(notes) >= MIN_NOTES_LENGTH:
            return notes

    fallback_model = (getattr(settings, "GEMINI_MODEL", "") or "").strip()
    if fallback_model and fallback_model != RESEARCH_MODEL:
        pipeline_result = _run_pipeline_with_retry(lead, fallback_model)
        if pipeline_result:
            notes, _structured = pipeline_result
            if notes and len(notes) >= MIN_NOTES_LENGTH:
                return notes

    return _build_local_fallback_notes(lead)
