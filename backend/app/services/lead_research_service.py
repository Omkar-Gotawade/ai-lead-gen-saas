"""Lead research service for cold-email personalization.

Runs web-grounded Gemini research first (recent posts, interviews, and company
news), then gracefully falls back to local lead/enrichment context.
"""
import asyncio
import logging
import re
import time
from typing import Optional, Tuple

import google.generativeai as genai

from app.config import settings
from app.models.lead import Lead

logger = logging.getLogger(__name__)

RESEARCH_STATUS_LIVE = "live"
RESEARCH_STATUS_FALLBACK = "fallback"
RESEARCH_STATUS_NONE = "none"

RESEARCH_MODEL = (
    (getattr(settings, "GEMINI_RESEARCH_MODEL", "") or "").strip()
    or (getattr(settings, "GEMINI_MODEL", "") or "").strip()
    or "gemini-1.5-flash"
)
RESEARCH_USE_WEB_SEARCH = bool(getattr(settings, "GEMINI_RESEARCH_ENABLE_WEB_SEARCH", True))
MAX_RETRIES = 3
MIN_NOTES_LENGTH = 40


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


def _build_prompt(lead: Lead, include_web_search: bool) -> str:
    full_name = f"{lead.first_name or ''} {lead.last_name or ''}".strip()

    base_context = f"""Lead Name: {full_name or 'Unknown'}
Company: {lead.company or 'Unknown'}
Role: {lead.title or lead.job_title or 'Unknown'}
LinkedIn: {lead.linkedin_url or 'Unknown'}
Industry: {lead.industry or 'Unknown'}
"""

    if include_web_search:
        return f"""You are a top-tier SDR research assistant.

Research this lead and company using public web sources.
{base_context}

Find concrete and recent signals (prefer last 6 months):
1) Recent posts/articles/interviews by the lead
2) Recent company news (funding, launches, hiring, partnerships)
3) Team or role-relevant initiatives the lead likely owns
4) Tools/platforms mentioned publicly (CRM, outreach, marketing stack)
5) One personalized opening-line angle for a cold email

Output format:
- Bullet points only
- Include dates/numbers where possible
- If uncertain, label as "Likely:" instead of stating as fact
- Keep under 180 words
- No fluff
"""

    enriched_data = lead.enriched_data if isinstance(lead.enriched_data, dict) else {}
    return f"""You are a top-tier SDR research assistant.

Web search is unavailable. Use only this context to build useful personalization notes.
{base_context}
Company summary: {enriched_data.get('company_summary') or 'N/A'}
Key insights: {enriched_data.get('key_insights') or 'N/A'}
Pain points: {', '.join(enriched_data.get('pain_points', [])) if isinstance(enriched_data.get('pain_points', []), list) else 'N/A'}

Output format:
- Bullet points only
- Include concrete details from the context
- If uncertain, label as "Likely:"
- Keep under 140 words
"""


def _call_model_once(lead: Lead, include_web_search: bool, model_name: str) -> Optional[str]:
    if include_web_search:
        try:
            model = genai.GenerativeModel(model_name=model_name, tools=["google_search"])
        except Exception:
            model = genai.GenerativeModel(model_name=model_name)
    else:
        model = genai.GenerativeModel(model_name=model_name)

    response = model.generate_content(_build_prompt(lead, include_web_search=include_web_search))
    notes = _safe_response_text(response)

    if not notes or len(notes) < MIN_NOTES_LENGTH:
        return None

    lowered = notes.lower()
    if "no recent public activity" in lowered and len(notes) < 120:
        return None

    return notes


def _call_model_with_retry(lead: Lead, include_web_search: bool, model_name: str) -> Optional[str]:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return _call_model_once(lead, include_web_search=include_web_search, model_name=model_name)
        except Exception as exc:
            if not _is_quota_or_rate_error(exc):
                logger.warning("Lead research failed for %s (%s): %s", lead.first_name, model_name, str(exc))
                return None

            if attempt >= MAX_RETRIES:
                logger.warning("Lead research retries exhausted for %s (%s): %s", lead.first_name, model_name, str(exc))
                return None

            wait_seconds = min(30.0, _extract_retry_seconds(exc) * (2 ** (attempt - 1)))
            logger.warning(
                "Lead research rate-limited for %s with %s, retrying in %.2fs (attempt %d/%d)",
                lead.first_name,
                model_name,
                wait_seconds,
                attempt,
                MAX_RETRIES,
            )
            time.sleep(wait_seconds)

    return None


def _build_local_fallback_notes(lead: Lead) -> Optional[str]:
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


async def research_lead_with_status(lead: Lead) -> Tuple[Optional[str], str]:
    """Research a lead and return notes plus status indicator."""
    if not settings.GEMINI_API_KEY:
        local_notes = _build_local_fallback_notes(lead)
        return local_notes, (RESEARCH_STATUS_FALLBACK if local_notes else RESEARCH_STATUS_NONE)

    if not lead.first_name:
        local_notes = _build_local_fallback_notes(lead)
        return local_notes, (RESEARCH_STATUS_FALLBACK if local_notes else RESEARCH_STATUS_NONE)

    genai.configure(api_key=settings.GEMINI_API_KEY)

    # Primary path: live web-grounded research.
    live_notes = await asyncio.to_thread(
        _call_model_with_retry,
        lead,
        RESEARCH_USE_WEB_SEARCH,
        RESEARCH_MODEL,
    )
    if live_notes:
        return live_notes, RESEARCH_STATUS_LIVE

    # Secondary path: configured model without search grounding.
    fallback_model = (getattr(settings, "GEMINI_MODEL", "") or "").strip()
    if fallback_model and fallback_model != RESEARCH_MODEL:
        model_fallback_notes = await asyncio.to_thread(
            _call_model_with_retry,
            lead,
            False,
            fallback_model,
        )
        if model_fallback_notes:
            return model_fallback_notes, RESEARCH_STATUS_FALLBACK

    # Final path: deterministic local notes.
    local_notes = _build_local_fallback_notes(lead)
    if local_notes:
        return local_notes, RESEARCH_STATUS_FALLBACK

    return None, RESEARCH_STATUS_NONE


async def research_lead(lead: Lead) -> Optional[str]:
    """Backwards-compatible async API returning notes only."""
    notes, _ = await research_lead_with_status(lead)
    return notes


def research_lead_sync(lead: Lead) -> Optional[str]:
    """Synchronous wrapper for Celery/background contexts."""
    if not settings.GEMINI_API_KEY or not lead.first_name:
        return _build_local_fallback_notes(lead)

    genai.configure(api_key=settings.GEMINI_API_KEY)

    notes = _call_model_with_retry(
        lead,
        include_web_search=RESEARCH_USE_WEB_SEARCH,
        model_name=RESEARCH_MODEL,
    )
    if notes:
        return notes

    fallback_model = (getattr(settings, "GEMINI_MODEL", "") or "").strip()
    if fallback_model and fallback_model != RESEARCH_MODEL:
        notes = _call_model_with_retry(
            lead,
            include_web_search=False,
            model_name=fallback_model,
        )
        if notes:
            return notes

    return _build_local_fallback_notes(lead)
