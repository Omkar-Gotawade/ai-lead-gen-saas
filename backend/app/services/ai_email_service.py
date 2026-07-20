"""Human SDR Copywriter Agent — AI email generation service.

Three-stage pipeline:
  1. Subject Agent   → generates 5 subject options, scores each, picks best
  2. Copywriter Agent → writes a 70–110 word SDR-style cold email body
  3. Quality Checker  → scores human/spam/AI risk; rewrites if thresholds fail

OpenRouter infrastructure (headers, retry, fallback models) is unchanged.
The existing Lead Research Agent (Gemini) is called upstream by the route layer
and its notes arrive here via lead.research_notes — completely untouched.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel

from app.config import settings
from app.models.lead import Lead

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class SubjectCandidate(BaseModel):
    """A single subject line candidate with scoring."""
    subject: str
    curiosity_score: int  # 0–10
    human_score: int      # 0–10
    reason: str


class EmailQualityReport(BaseModel):
    """Quality assessment from the Quality Checker Agent."""
    human_score: int            # 0–100
    personalization_score: int  # 0–100
    spam_risk: int              # 0–100
    sounds_ai_generated: bool


class GeneratedEmail(BaseModel):
    """Generated email with body, subject and A/B metadata."""
    subject: str
    body: str
    # A/B test metadata
    email_angle: Optional[str] = None          # pain_point|curiosity|question|case_study|direct
    word_count: Optional[int] = None
    tone: Optional[str] = None
    selected_subject: Optional[str] = None
    alternative_subjects: Optional[List[str]] = None
    quality_report: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Banned content lists
# ---------------------------------------------------------------------------

# Phrases that make emails feel generic or AI-written
BANNED_PHRASES = [
    "i came across your profile",
    "i came across your company",
    "i hope this email finds you well",
    "wanted to reach out",
    "my aim is to",
    "explore how we might",
    "align with your objectives",
    "thought i'd reach out",
    "i'd love to chat",
    "cutting-edge",
    "industry-leading",
    "revolutionize",
    "game-changing",
    "leverage",
    "synergy",
    "paradigm shift",
    "best-in-class",
    "must be a huge undertaking",
    "must be challenging",
    "are you ever finding it difficult",
    "ensuring consistent messaging",
    "optimizing campaign performance",
    "resonates and delivers",
    "measurable results",
    "fragmented effort",
    "unified brand voice",
    # New additions from spec
    "given your focus on",
    "i was impressed by",
    "in today's competitive landscape",
    "revolutionary",
    "transform",
    "unlock",
    "seamless",
    "enhance",
    "optimize",
    "maximize",
    "powerful solution",
    "tailored solution",
]

# Corporate jargon that inflates spam risk
CORPORATE_JARGON = [
    "ensuring consistent",
    "measurable results",
    "fragmented effort",
    "unified brand voice",
    "must be a huge",
    "must be challenging",
    "resonate and deliver",
    "massive scale",
    "huge undertaking",
]


# ---------------------------------------------------------------------------
# OpenRouter infrastructure (unchanged from original)
# ---------------------------------------------------------------------------

def _normalize_text_for_match(value: str) -> str:
    """Normalize text for robust fuzzy containment checks."""
    if not value:
        return ""
    normalized = value.lower()
    return re.sub(r"[^a-z0-9]", "", normalized)


def _body_mentions_company(body: str, company: str) -> bool:
    """Return True when the body references the company despite punctuation/spacing variance."""
    body_lower = (body or "").lower()
    company_lower = (company or "").lower().strip()
    if not company_lower:
        return True
    if company_lower in body_lower:
        return True
    body_norm = _normalize_text_for_match(body_lower)
    company_norm = _normalize_text_for_match(company_lower)
    return bool(company_norm and company_norm in body_norm)


def _strip_postscript(body: str) -> str:
    """Remove trailing postscript (P.S.) blocks from generated content."""
    if not body:
        return body
    return re.sub(r"\n\s*(p\.?\s*s\.?\s*:?).*$", "", body, flags=re.IGNORECASE | re.DOTALL).strip()


def _build_openrouter_headers() -> Dict[str, str]:
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    if settings.OPENROUTER_HTTP_REFERER:
        headers["HTTP-Referer"] = settings.OPENROUTER_HTTP_REFERER
    if settings.OPENROUTER_APP_NAME:
        headers["X-Title"] = settings.OPENROUTER_APP_NAME
    return headers


def _parse_retry_delay(response: requests.Response, attempt: int) -> float:
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return max(1.0, float(retry_after))
        except ValueError:
            pass
    return min(20.0, 2.0 ** attempt)


def _request_openrouter_completion(prompt: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    candidate_models: List[str] = []
    if settings.OPENROUTER_MODEL and settings.OPENROUTER_MODEL.strip():
        candidate_models.append(settings.OPENROUTER_MODEL.strip())

    fallback_raw = (settings.OPENROUTER_FALLBACK_MODELS or "").strip()
    if fallback_raw:
        for model in fallback_raw.split(","):
            model_id = model.strip()
            if model_id and model_id not in candidate_models:
                candidate_models.append(model_id)

    if not candidate_models:
        raise ValueError("No OpenRouter models configured. Set OPENROUTER_MODEL.")

    max_retries = 4
    last_error: Optional[str] = None
    rate_limited_models: List[str] = []

    for model_id in candidate_models:
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.75,
        }

        model_rate_limited = False
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    headers=_build_openrouter_headers(),
                    json=payload,
                    timeout=60,
                )

                if response.status_code == 404:
                    response_text = (response.text or "").lower()
                    if "no endpoints found" in response_text:
                        last_error = f"OpenRouter model '{model_id}' is unavailable for this account."
                        logger.warning(last_error)
                        break

                if response.status_code == 429:
                    model_rate_limited = True
                    delay_seconds = _parse_retry_delay(response, attempt)
                    logger.warning(
                        "OpenRouter rate limited model %s (attempt %s/%s). Retrying in %.1fs.",
                        model_id, attempt + 1, max_retries, delay_seconds,
                    )
                    if attempt < max_retries - 1:
                        time.sleep(delay_seconds)
                    continue

                response.raise_for_status()
                data = response.json()
                choices = data.get("choices") or []
                if not choices:
                    raise ValueError("OpenRouter returned no choices")
                message = choices[0].get("message") or {}
                content = (message.get("content") or "").strip()
                if not content:
                    raise ValueError("OpenRouter returned empty content")
                return content

            except requests.RequestException as exc:
                last_error = f"{model_id}: {exc}"
                if attempt >= max_retries - 1:
                    break
                time.sleep(min(20.0, 2.0 ** attempt))

        if model_rate_limited:
            rate_limited_models.append(model_id)
            continue

    if rate_limited_models:
        raise ValueError(
            "OpenRouter rate limit hit for all configured models: "
            + ", ".join(rate_limited_models)
        )

    raise ValueError(f"OpenRouter request failed after {max_retries} attempts: {last_error}")


# ---------------------------------------------------------------------------
# Existing quality helpers (unchanged — used as final rule-based safety net)
# ---------------------------------------------------------------------------

def _extract_lead_research_signals(lead: Lead) -> List[str]:
    """Collect concrete research signals from lead fields and enrichment JSON."""
    signals: List[str] = []

    if lead.linkedin_url:
        signals.append(f"LinkedIn URL: {lead.linkedin_url}")
    if lead.linkedin_headline:
        signals.append(f"LinkedIn headline: {lead.linkedin_headline}")
    if lead.job_title:
        signals.append(f"Job title: {lead.job_title}")
    if lead.seniority:
        signals.append(f"Seniority: {lead.seniority}")
    if lead.company_size:
        signals.append(f"Company size: {lead.company_size}")

    enriched = lead.enriched_data if isinstance(lead.enriched_data, dict) else None
    if enriched:
        preferred_keys = [
            "company_domain", "company_summary", "industry", "pain_points",
            "key_insights", "funding", "hiring", "tech_stack", "tools",
            "recent_news", "signals",
        ]
        for key in preferred_keys:
            value = enriched.get(key)
            if not value:
                continue
            if isinstance(value, list):
                cleaned = [str(v).strip() for v in value if str(v).strip()]
                if cleaned:
                    signals.append(f"{key}: {', '.join(cleaned[:5])}")
            elif isinstance(value, (str, int, float)):
                text = str(value).strip()
                if text:
                    signals.append(f"{key}: {text}")

    deduped: List[str] = []
    seen = set()
    for signal in signals:
        norm = signal.lower()
        if norm not in seen:
            seen.add(norm)
            deduped.append(signal)

    return deduped


def _check_email_quality(email: GeneratedEmail, lead: Lead) -> List[str]:
    """
    Rule-based quality validation. Returns list of issues (empty = passes).
    Used as the final safety net after the LLM Quality Checker stage.
    """
    issues = []
    body_lower = email.body.lower()

    for phrase in BANNED_PHRASES:
        if phrase in body_lower:
            issues.append(f"Contains banned phrase: '{phrase}'")

    if re.search(r"(^|\n)\s*p\.?\s*s\.?\s*:?,?", email.body, flags=re.IGNORECASE):
        issues.append("Contains postscript (P.S.) which is not allowed")

    body_without_sig = re.sub(r"Best regards,.*$", "", email.body, flags=re.DOTALL | re.IGNORECASE)
    word_count = len(body_without_sig.split())
    if word_count < 30:
        issues.append(f"Too short: {word_count} words (minimum 30)")
    elif word_count > 150:
        issues.append(f"Too long: {word_count} words (maximum 150)")

    if lead.first_name and lead.first_name.lower() not in body_lower:
        issues.append(f"Lead's first name '{lead.first_name}' not used in email body")

    if lead.company and not _body_mentions_company(email.body, lead.company):
        issues.append(f"Company name '{lead.company}' not mentioned in email")

    research_signals = _extract_lead_research_signals(lead)
    research_corpus = "\n".join([lead.research_notes or ""] + research_signals).strip()
    if research_corpus:
        research_lower = research_corpus.lower()
        has_specific_reference = False

        numbers_in_research = re.findall(r"\b\d+\b", research_corpus)
        for num in numbers_in_research:
            if num in email.body:
                has_specific_reference = True
                break

        tools = ["salesforce", "outreach", "sendgrid", "linkedin", "series a", "series b",
                 "hiring", "raised", "funding"]
        for tool in tools:
            if tool in research_lower and tool in body_lower:
                has_specific_reference = True
                break

        if not has_specific_reference:
            issues.append(
                "Research context available but email doesn't reference specific details "
                "(numbers, tools, events)"
            )

    has_question = "?" in email.body
    action_words = ["call", "chat", "meeting", "discuss", "talk", "connect", "demo",
                    "walkthrough", "conversation"]
    has_action = any(word in body_lower for word in action_words)
    if not has_question and not has_action:
        issues.append("Missing clear call-to-action (no question or action words)")

    sentences = [s.strip() for s in email.body.replace("?", ".").replace("!", ".").split(".") if s.strip()]
    if sentences:
        avg_words_per_sentence = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_words_per_sentence > 18:
            issues.append(f"Sentences too long (avg {avg_words_per_sentence:.1f} words, keep under 18)")

    for jargon in CORPORATE_JARGON:
        if jargon in body_lower:
            issues.append(f"Contains corporate jargon: '{jargon}'")

    return issues


# ---------------------------------------------------------------------------
# Stage 1 — Subject Agent
# ---------------------------------------------------------------------------

_SUBJECT_AGENT_PROMPT_TEMPLATE = """\
You are a Subject Line Specialist writing cold email subjects for a B2B SaaS SDR.

LEAD CONTEXT:
- Name: {first_name} {last_name}
- Company: {company}
- Title: {title}
- Research notes: {research_snippet}

YOUR TASK:
Generate exactly 5 subject line options for this cold email.

STRICT RULES:
- 2 to 5 words only
- Under 50 characters
- Lowercase preferred
- Curiosity-focused — make the recipient want to open
- No clickbait, no emojis, no exclamation marks
- Zero sales words (no: offer, deal, pricing, solution, ROI, revenue, growth, boost, scale)
- Sound like a real person sending from Gmail, not a marketing blast

BAD EXAMPLES (never write like this):
- "Increase Sales With AI"
- "Transform Your Outreach Process"
- "TCS NVIDIA Partnership Update"
- "Unlock Your Revenue Potential"

GOOD EXAMPLES (write like this):
- "quick question"
- "idea for {company}"
- "noticed the expansion"
- "scaling your team?"
- "quick thought"
- "saw this about {company}"
- "curious about your stack"

RESPOND IN THIS EXACT JSON FORMAT (no markdown, no extra text):
[
  {{"subject": "...", "curiosity_score": 8, "human_score": 9, "reason": "..."}},
  {{"subject": "...", "curiosity_score": 7, "human_score": 8, "reason": "..."}},
  {{"subject": "...", "curiosity_score": 9, "human_score": 9, "reason": "..."}},
  {{"subject": "...", "curiosity_score": 6, "human_score": 7, "reason": "..."}},
  {{"subject": "...", "curiosity_score": 8, "human_score": 8, "reason": "..."}}
]
"""


def _parse_subject_candidates(raw: str) -> List[SubjectCandidate]:
    """Parse JSON array of subject candidates, tolerating markdown fences."""
    text = raw.strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```[a-z]*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n?```$", "", text)
    text = text.strip()

    # Extract first JSON array found
    match = re.search(r"\[.*\]", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Subject Agent returned no JSON array: {raw[:200]}")

    data = json.loads(match.group())
    candidates = []
    for item in data:
        candidates.append(SubjectCandidate(
            subject=str(item.get("subject", "")).strip(),
            curiosity_score=int(item.get("curiosity_score", 5)),
            human_score=int(item.get("human_score", 5)),
            reason=str(item.get("reason", "")),
        ))
    return candidates


def _run_subject_agent(
    lead: Lead,
    product_description: str,
    research_notes: Optional[str],
) -> tuple[str, List[str]]:
    """
    Stage 1: Generate 5 subject candidates, score them, return best + alternatives.

    Returns:
        (selected_subject, alternative_subjects)
    """
    company = lead.company or "your company"
    first_name = lead.first_name or ""
    last_name = lead.last_name or ""
    title = lead.title or lead.job_title or ""

    # Give the Subject Agent a short research snippet (first 200 chars)
    research_snippet = ""
    if research_notes:
        for line in research_notes.splitlines():
            cleaned = line.strip().lstrip("- ").strip()
            if cleaned and not cleaned.lower().startswith("research fallback"):
                research_snippet = cleaned[:200]
                break

    prompt = _SUBJECT_AGENT_PROMPT_TEMPLATE.format(
        first_name=first_name,
        last_name=last_name,
        company=company,
        title=title,
        research_snippet=research_snippet or "No specific recent activity found.",
    )

    raw = _request_openrouter_completion(prompt)
    candidates = _parse_subject_candidates(raw)

    if not candidates:
        # Deterministic fallback
        return f"quick question for {company}", []

    # Pick highest combined score
    candidates.sort(key=lambda c: c.curiosity_score + c.human_score, reverse=True)
    selected = candidates[0].subject
    alternatives = [c.subject for c in candidates[1:] if c.subject and c.subject != selected]

    return selected, alternatives


# ---------------------------------------------------------------------------
# Stage 2 — Human SDR Copywriter Agent
# ---------------------------------------------------------------------------

_COPYWRITER_AGENT_PROMPT_TEMPLATE = """\
You are an experienced SDR. You write every cold email yourself. \
You never use templates. \
You write the way you'd text a colleague: direct, natural, no fluff.

LEAD CONTEXT:
Name: {first_name} {last_name}
Company: {company}
Title: {title}
Industry: {industry}
Company size: {company_size}
Location: {location}

RESEARCHED BUYING SIGNAL (highest priority — this is a REAL, specific fact about the company):
{best_email_opener}

BUYING SIGNAL TYPE: {recommended_email_angle}

RESEARCH NOTES (from Gemini research agent — use these to personalize):
{research_notes}

ENRICHMENT SIGNALS:
{enrichment_signals}

EMAIL CONTEXT:
Product/Service: {product_description}
Your name (sign off with FIRST NAME ONLY): {sender_first_name}
Selected subject line: {subject}

EMAIL STRUCTURE — follow this exactly:
Hi {first_name},
[blank line]
Line 1: MUST use the RESEARCHED BUYING SIGNAL above as your opener if it is specific and non-empty.
        Adapt the wording naturally — e.g. "Saw {company} recently partnered with NVIDIA...",
        "Congrats on the Series A...", "Noticed you're expanding into Europe..."
        If the buying signal is empty or generic, write your own specific observation from the research notes.
        NEVER start with "I noticed your company" or generic openers.
[blank line]
Line 2: Connect it naturally to a real problem they likely face. One sentence.
[blank line]
Line 3: What you offer — describe it in plain words based on: "{product_description}". One or two sentences max. Do NOT copy-paste the description verbatim; rephrase it naturally in a sentence a real person would say.
[blank line]
Line 4: Low-pressure CTA. One short question. Examples: "Worth a quick chat?", "Open to a 10-min call?", "Curious to hear your take?"
[blank line]
{sender_first_name}

WORD COUNT RULE: Total email body must be 70–110 words. Count carefully.

WRITING STYLE:
- Sound like you typed this in Gmail, not built it in a tool
- Short sentences (10–15 words ideal, 20 max)
- Casual but not sloppy
- Slightly imperfect is fine — perfect grammar feels AI-written
- No paragraphs longer than 2 sentences

GOOD OPENER PHRASES (use similar patterns):
"Saw your team recently expanded..."
"Noticed you're hiring a few SDRs..."
"Congrats on the Series A..."
"Saw the partnership announcement with..."
"Was reading your recent blog post about..."

NEVER USE:
- "I hope this email finds you well"
- "I noticed your company"
- "Given your focus on"
- "I was impressed by"
- "I came across"
- "In today's competitive landscape"
- revolutionary / cutting-edge / transform / unlock / leverage / seamless
- game-changing / enhance / optimize / maximize / powerful solution / tailored solution
- Any corporate jargon or marketing language
- Long paragraphs
- P.S. sections

BAD EMAIL (never write like this):
Hi John,
Given your company's focus on revolutionary AI transformation, I thought you might be \
interested in our cutting-edge platform that can optimize your workflow and leverage your \
existing data to seamlessly enhance team performance.
Let me know if you'd like to connect!
Best,
Alex

GOOD EMAIL (write like this):
Hi John,
Saw TCS recently partnered with NVIDIA to build an industrial metaverse center.
At that scale, coordinating outbound across a growing sales team gets messy fast.
We help teams find and contact the right leads without spending hours manually.
Worth a quick chat?
Omkar

OUTPUT ONLY THE EMAIL BODY — no subject line, no JSON, no explanation. \
Start with "Hi {first_name}," and end with just your first name on its own line.
"""


def _count_body_words(body: str) -> int:
    """Count words in body excluding the final signature line."""
    sig_pattern = re.compile(r"\n\s*\w+\s*$")
    cleaned = sig_pattern.sub("", body).strip()
    return len(cleaned.split())


def _get_buying_signal_context(lead: Lead) -> tuple[str, str]:
    """Extract best_email_opener and recommended_email_angle from structured research.

    Priority:
        1. recommended_signal (4-dimension weighted rank #1) — highest quality
        2. best_email_openers[0] (Gemini-generated, pre-ranked)
        3. best_email_opener (legacy single field)

    Returns:
        (best_email_opener, recommended_email_angle)
        Both may be empty strings if not available.
    """
    try:
        enriched = lead.enriched_data if isinstance(lead.enriched_data, dict) else {}
        bsr = enriched.get("buying_signals_result")
        if not isinstance(bsr, dict):
            return "", ""

        angle = (bsr.get("recommended_email_angle") or "").strip()

        # Prefer the headline of the weighted rank-#1 recommended_signal
        rec = bsr.get("recommended_signal")
        if isinstance(rec, dict):
            # Use the pre-built openers list whose #1 is calibrated to recommended_signal
            openers = bsr.get("best_email_openers") or []
            opener = (openers[0] if openers else "").strip()
            if not opener:
                # Build a quick opener from the signal headline
                headline = (rec.get("headline") or "").strip()
                if headline:
                    opener = f"Saw {headline}"
            if opener:
                return opener, angle

        # Fallback: plain best_email_opener (backward-compat)
        opener = (bsr.get("best_email_opener") or "").strip()
        return opener, angle

    except Exception:
        pass
    return "", ""


def _run_copywriter_agent(
    lead: Lead,
    sender_name: str,
    product_description: str,
    subject: str,
    research_notes: Optional[str],
) -> str:
    """
    Stage 2: Write the email body. Returns raw body string.
    """
    first_name = lead.first_name or "there"
    last_name = lead.last_name or ""
    company = lead.company or "your company"
    title = lead.title or lead.job_title or "your role"
    industry = lead.industry or ""
    company_size = lead.company_size or ""
    location = lead.location or ""

    # First name only for signature (feels more human)
    sender_first_name = sender_name.split()[0] if sender_name else sender_name

    notes_text = (research_notes or "No research notes available.").strip()

    enrichment_signals = _extract_lead_research_signals(lead)
    enrichment_text = (
        "\n".join(f"- {s}" for s in enrichment_signals) if enrichment_signals
        else "No enrichment signals available."
    )

    # Pull the structured buying signal opener (highest priority context)
    best_email_opener, recommended_email_angle = _get_buying_signal_context(lead)

    # If no structured opener, extract the best line from research notes as fallback
    if not best_email_opener and research_notes:
        for line in research_notes.splitlines():
            cleaned = line.strip()
            # Skip meta-lines like "BUYING SIGNALS:" or "COMPANY:" headers
            if cleaned and not cleaned.startswith(("BEST OPENER:", "EMAIL ANGLE:", "BUYING SIGNALS", "COMPANY:", "PRODUCTS", "Research fallback", "[", "-")):
                best_email_opener = cleaned[:300]
                break
        # Also check for explicitly labelled BEST OPENER line
        for line in research_notes.splitlines():
            if line.strip().startswith("BEST OPENER:"):
                best_email_opener = line.strip().removeprefix("BEST OPENER:").strip()
                break

    prompt = _COPYWRITER_AGENT_PROMPT_TEMPLATE.format(
        first_name=first_name,
        last_name=last_name,
        company=company,
        title=title,
        industry=industry,
        company_size=company_size,
        location=location,
        best_email_opener=best_email_opener or "No specific buying signal found — use research notes to create a natural opener.",
        recommended_email_angle=recommended_email_angle or "general",
        research_notes=notes_text,
        enrichment_signals=enrichment_text,
        product_description=product_description,
        sender_first_name=sender_first_name,
        subject=subject,
    )

    return _request_openrouter_completion(prompt)


# ---------------------------------------------------------------------------
# Stage 3 — Quality Checker Agent
# ---------------------------------------------------------------------------

_QUALITY_CHECKER_PROMPT_TEMPLATE = """\
You are a Quality Checker for a cold email SDR system. \
Your job is to assess whether this email sounds like it was written by a real human SDR \
or by an AI.

EMAIL TO EVALUATE:
---
{email_body}
---

Ask yourself these questions internally before scoring:
1. "Would a busy founder actually type this email?"
2. "Does this reference something specific and real about the company/person?"
3. "Does it use any AI giveaway patterns (corporate language, over-explaining, fake excitement)?"
4. "Is this 70–110 words, short sentences, natural tone?"

SCORE THE EMAIL:
- human_score: 0–100 (100 = reads exactly like a real SDR wrote it)
- personalization_score: 0–100 (100 = references specific, verified detail about this person/company)
- spam_risk: 0–100 (100 = will definitely hit spam)
- sounds_ai_generated: true or false

IMPORTANT THRESHOLDS:
- human_score < 85 → email needs a rewrite
- sounds_ai_generated = true → email needs a rewrite
- spam_risk > 60 → email needs a rewrite

Also classify the email angle:
- pain_point: opens by touching a pain/problem
- curiosity: opens with an interesting observation
- question: opens with a direct question
- case_study: references a similar company result
- direct: goes straight to what you offer

RESPOND IN THIS EXACT JSON FORMAT (no markdown, no extra text):
{{
  "human_score": 88,
  "personalization_score": 75,
  "spam_risk": 12,
  "sounds_ai_generated": false,
  "email_angle": "curiosity",
  "needs_rewrite": false,
  "rewrite_reason": ""
}}
"""


def _parse_quality_report(raw: str) -> Dict[str, Any]:
    """Parse the quality checker JSON response, tolerating markdown fences."""
    text = raw.strip()
    text = re.sub(r"^```[a-z]*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n?```$", "", text)
    text = text.strip()

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Quality Checker returned no JSON: {raw[:200]}")

    return json.loads(match.group())


def _run_quality_checker(email_body: str) -> Dict[str, Any]:
    """
    Stage 3: Score the email. Returns a quality report dict.
    """
    prompt = _QUALITY_CHECKER_PROMPT_TEMPLATE.format(email_body=email_body)
    raw = _request_openrouter_completion(prompt)
    return _parse_quality_report(raw)


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

async def generate_email(
    lead: Lead,
    sender_name: str,
    tone: str = "professional",
    goal: str = "schedule a meeting",
    product_description: str = "our product",
) -> GeneratedEmail:
    """
    Human SDR Copywriter Agent — generate a cold email that reads like
    a real person wrote it.

    Pipeline:
        Stage 1 → Subject Agent  (1 LLM call)
        Stage 2 → Copywriter Agent  (1 LLM call)
        Stage 3 → Quality Checker  (1 LLM call)
        [optional] Rewrite if quality thresholds fail  (1–2 more calls)
        Final → Rule-based _check_email_quality() safety net

    Args:
        lead:                Lead object (research_notes already populated by route layer)
        sender_name:         Full name of the sending user (first name used in signature)
        tone:                Kept for API compatibility; not used (style is baked into prompts)
        goal:                Kept for API compatibility
        product_description: What Prosario does / what the campaign is selling

    Returns:
        GeneratedEmail with body, subject, and A/B metadata fields

    Raises:
        ValueError: If OPENROUTER_API_KEY not configured or all generation attempts fail
    """
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not configured")

    research_notes = lead.research_notes or None

    # -----------------------------------------------------------------------
    # Stage 1 — Subject Agent
    # -----------------------------------------------------------------------
    try:
        selected_subject, alternative_subjects = await asyncio.to_thread(
            _run_subject_agent, lead, product_description, research_notes
        )
        logger.info(
            "Subject Agent selected '%s' for lead %s (alternatives: %s)",
            selected_subject, lead.id, alternative_subjects,
        )
    except Exception as exc:
        logger.warning("Subject Agent failed for lead %s, using fallback: %s", lead.id, exc)
        company = lead.company or "your company"
        selected_subject = f"quick question for {company}"
        alternative_subjects = []

    # -----------------------------------------------------------------------
    # Stage 2 — Copywriter Agent (up to 2 attempts if output is empty)
    # -----------------------------------------------------------------------
    raw_body: Optional[str] = None
    for copy_attempt in range(2):
        try:
            raw_body = await asyncio.to_thread(
                _run_copywriter_agent,
                lead, sender_name, product_description, selected_subject, research_notes,
            )
            raw_body = _strip_postscript(raw_body)
            if raw_body and len(raw_body.strip()) > 20:
                break
        except Exception as exc:
            logger.warning(
                "Copywriter Agent attempt %d failed for lead %s: %s",
                copy_attempt + 1, lead.id, exc,
            )
            raw_body = None

    if not raw_body:
        raise ValueError("Copywriter Agent failed to produce an email body after 2 attempts.")

    # -----------------------------------------------------------------------
    # Stage 3 — Quality Checker (with one rewrite if thresholds fail)
    # -----------------------------------------------------------------------
    quality_report: Dict[str, Any] = {}
    email_angle: Optional[str] = None
    final_body = raw_body

    try:
        quality_report = await asyncio.to_thread(_run_quality_checker, raw_body)
        email_angle = quality_report.get("email_angle")
        needs_rewrite = quality_report.get("needs_rewrite", False)

        # Enforce thresholds regardless of model's own `needs_rewrite` flag
        human_score = int(quality_report.get("human_score", 100))
        spam_risk = int(quality_report.get("spam_risk", 0))
        sounds_ai = bool(quality_report.get("sounds_ai_generated", False))

        if human_score < 85 or sounds_ai or spam_risk > 60:
            needs_rewrite = True
            logger.info(
                "Quality Checker triggered rewrite for lead %s "
                "(human=%d, spam=%d, ai=%s)",
                lead.id, human_score, spam_risk, sounds_ai,
            )

        if needs_rewrite:
            rewrite_reason = quality_report.get("rewrite_reason", "")
            logger.info("Rewriting email for lead %s. Reason: %s", lead.id, rewrite_reason)
            try:
                rewritten_body = await asyncio.to_thread(
                    _run_copywriter_agent,
                    lead, sender_name, product_description, selected_subject, research_notes,
                )
                rewritten_body = _strip_postscript(rewritten_body)
                if rewritten_body and len(rewritten_body.strip()) > 20:
                    final_body = rewritten_body
                    # Re-score the rewrite
                    try:
                        quality_report = await asyncio.to_thread(
                            _run_quality_checker, final_body
                        )
                        email_angle = quality_report.get("email_angle", email_angle)
                    except Exception as qc_exc:
                        logger.warning(
                            "Quality re-check after rewrite failed for lead %s: %s",
                            lead.id, qc_exc,
                        )
            except Exception as rw_exc:
                logger.warning(
                    "Rewrite attempt failed for lead %s, keeping original: %s",
                    lead.id, rw_exc,
                )

    except Exception as qc_exc:
        logger.warning(
            "Quality Checker failed for lead %s (continuing with raw body): %s",
            lead.id, qc_exc,
        )

    # -----------------------------------------------------------------------
    # Final — rule-based safety net (existing _check_email_quality)
    # -----------------------------------------------------------------------
    email_obj = GeneratedEmail(subject=selected_subject, body=final_body)
    issues = _check_email_quality(email_obj, lead)
    if issues:
        logger.info(
            "Rule-based quality check found %d issue(s) for lead %s: %s",
            len(issues), lead.id, issues,
        )

    # -----------------------------------------------------------------------
    # Build enriched response with A/B metadata
    # -----------------------------------------------------------------------
    word_count = _count_body_words(final_body)

    return GeneratedEmail(
        subject=selected_subject,
        body=final_body,
        email_angle=email_angle,
        word_count=word_count,
        tone=tone,
        selected_subject=selected_subject,
        alternative_subjects=alternative_subjects,
        quality_report={
            "human_score": quality_report.get("human_score"),
            "personalization_score": quality_report.get("personalization_score"),
            "spam_risk": quality_report.get("spam_risk"),
            "sounds_ai_generated": quality_report.get("sounds_ai_generated"),
        } if quality_report else None,
    )

# ---------------------------------------------------------------------------
# FollowUp Agent
# ---------------------------------------------------------------------------

_FOLLOWUP_AGENT_PROMPT_TEMPLATE = """\
You are an experienced SDR writing a follow-up email to a cold prospect.
You NEVER use templates. You write naturally, like sending a quick reply in Gmail.

LEAD CONTEXT:
Name: {first_name} {last_name}
Company: {company}
Title: {title}

PREVIOUS EMAIL (Sent by you):
{original_email}

PREVIOUS FOLLOW-UPS (If any):
{previous_followups}

YOUR TASK:
Write a SHORT, natural follow-up email. It should thread directly onto the previous email.

STRICT RULES:
- Length: 20-50 words MAXIMUM.
- Do NOT repeat the product pitch.
- Just a quick bump, a new angle, or a short question.
- Sound casual but polite.
- NO corporate jargon.
- Do NOT use: "I hope this email finds you well", "Just bubbling this up", "Just wanted to follow up", "Checking in".

GOOD EXAMPLES (write like this):
"Hi {first_name} - any thoughts on this?"
"Hi {first_name}, just bringing this to the top of your inbox in case you missed it. Worth a brief chat?"
"Hi {first_name}, wanted to see if {company} is still prioritizing this right now?"

OUTPUT ONLY THE EMAIL BODY — no subject line, no JSON, no explanation.
Start with "Hi {first_name}," and end with your first name on its own line:
{sender_first_name}
"""

def _run_followup_agent(
    lead: Lead,
    sender_name: str,
    original_email: str,
    previous_followups: str,
) -> str:
    first_name = lead.first_name or "there"
    last_name = lead.last_name or ""
    company = lead.company or "your company"
    title = lead.title or lead.job_title or "your role"
    sender_first_name = sender_name.split()[0] if sender_name else sender_name

    prompt = _FOLLOWUP_AGENT_PROMPT_TEMPLATE.format(
        first_name=first_name,
        last_name=last_name,
        company=company,
        title=title,
        original_email=original_email,
        previous_followups=previous_followups or "None",
        sender_first_name=sender_first_name,
    )
    return _request_openrouter_completion(prompt)


async def generate_followup_email(
    lead: Lead,
    sender_name: str,
    original_email: str,
    previous_followups: str = "",
) -> GeneratedEmail:
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not configured")

    raw_body: Optional[str] = None
    for copy_attempt in range(2):
        try:
            raw_body = await asyncio.to_thread(
                _run_followup_agent,
                lead, sender_name, original_email, previous_followups,
            )
            raw_body = _strip_postscript(raw_body)
            if raw_body and len(raw_body.strip()) > 5:
                break
        except Exception as exc:
            logger.warning(
                "FollowUp Agent attempt %d failed for lead %s: %s",
                copy_attempt + 1, lead.id, exc,
            )
            raw_body = None

    if not raw_body:
        raise ValueError("FollowUp Agent failed to produce an email body.")
    
    return GeneratedEmail(
        subject="", # Threaded reply, no subject needed
        body=raw_body,
    )

