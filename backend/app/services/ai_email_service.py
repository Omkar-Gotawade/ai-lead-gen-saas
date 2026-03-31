"""AI email generation service using Google Gemini."""
from typing import Optional, List, Tuple, Dict, Any
import google.generativeai as genai
from app.config import settings
from app.models.lead import Lead
from pydantic import BaseModel
import re


class GeneratedEmail(BaseModel):
    """Generated email response."""
    subject: str
    body: str


# Banned phrases that make emails sound too generic or AI-generated
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
]


def _extract_lead_research_signals(lead: Lead) -> List[str]:
    """Collect concrete research signals from lead fields and enrichment JSON."""
    signals: List[str] = []

    # Core LinkedIn/persona signals
    if lead.linkedin_url:
        signals.append(f"LinkedIn URL: {lead.linkedin_url}")
    if lead.linkedin_headline:
        signals.append(f"LinkedIn headline: {lead.linkedin_headline}")
    if lead.job_title:
        signals.append(f"Job title: {lead.job_title}")
    if lead.seniority:
        signals.append(f"Seniority: {lead.seniority}")

    # Existing enriched profile/company details
    if lead.company_size:
        signals.append(f"Company size: {lead.company_size}")

    enriched = lead.enriched_data if isinstance(lead.enriched_data, dict) else None
    if enriched:
        preferred_keys = [
            "company_domain",
            "company_summary",
            "industry",
            "pain_points",
            "key_insights",
            "funding",
            "hiring",
            "tech_stack",
            "tools",
            "recent_news",
            "signals",
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

    # Deduplicate while preserving order
    deduped: List[str] = []
    seen = set()
    for signal in signals:
        norm = signal.lower()
        if norm not in seen:
            seen.add(norm)
            deduped.append(signal)

    return deduped


def _format_research_notes_prompt(notes: str) -> str:
    """
    Format research notes for the LLM to extract key points.
    
    Args:
        notes: Raw research notes about the lead
        
    Returns:
        Formatted string highlighting key points
    """
    if not notes:
        return ""
    
    return f"""
[CRITICAL RESEARCH INSIGHTS - MUST USE IN EMAIL]
{notes}

⚠️ REQUIREMENT: You MUST reference at least ONE specific detail from these notes in your opening sentence.
Examples of good references:
- "saw you're growing the SDR team from 5 to 12"
- "congrats on the Series A ($5M)"
- "noticed you posted about deliverability issues"
- "saw you're using Outreach.io + Salesforce"
"""


def _check_email_quality(email: GeneratedEmail, lead: Lead) -> List[str]:
    """
    Validate email quality and return list of issues found.
    
    Args:
        email: Generated email to check
        lead: Lead object for context
        
    Returns:
        List of quality issue descriptions (empty if email passes all checks)
    """
    issues = []
    body_lower = email.body.lower()
    
    # Check for banned phrases
    for phrase in BANNED_PHRASES:
        if phrase in body_lower:
            issues.append(f"Contains banned phrase: '{phrase}'")
    
    # Check word count (30-150 words in body, excluding signature)
    # Remove signature for word count
    body_without_sig = re.sub(r'Best regards,.*$', '', email.body, flags=re.DOTALL | re.IGNORECASE)
    word_count = len(body_without_sig.split())
    if word_count < 30:
        issues.append(f"Too short: {word_count} words (minimum 30)")
    elif word_count > 150:
        issues.append(f"Too long: {word_count} words (maximum 150)")
    
    # Check if lead's first name is used in body
    if lead.first_name and lead.first_name.lower() not in body_lower:
        issues.append(f"Lead's first name '{lead.first_name}' not used in email body")
    
    # Check if company is mentioned (if available)
    if lead.company and lead.company.lower() not in body_lower:
        issues.append(f"Company name '{lead.company}' not mentioned in email")
    
    # CRITICAL: If any research context exists, ensure email references specific details
    research_signals = _extract_lead_research_signals(lead)
    research_corpus = "\n".join([lead.research_notes or ""] + research_signals).strip()
    if research_corpus:
        # Extract potential specific details (numbers, dollar signs, tool names, etc.)
        research_lower = research_corpus.lower()
        has_specific_reference = False
        
        # Check for numbers from research in email
        numbers_in_research = re.findall(r'\b\d+\b', research_corpus)
        for num in numbers_in_research:
            if num in email.body:
                has_specific_reference = True
                break
        
        # Check for common tools/platforms mentioned in research
        tools = ['salesforce', 'outreach', 'sendgrid', 'linkedin', 'series a', 'series b', 'hiring', 'raised', 'funding']
        for tool in tools:
            if tool in research_lower and tool in body_lower:
                has_specific_reference = True
                break
        
        if not has_specific_reference:
            issues.append("Research context available but email doesn't reference specific details (numbers, tools, events)")
    
    # Check for clear CTA (question mark or action words)
    has_question = '?' in email.body
    action_words = ['call', 'chat', 'meeting', 'discuss', 'talk', 'connect', 'demo', 'walkthrough', 'conversation']
    has_action = any(word in body_lower for word in action_words)
    
    if not has_question and not has_action:
        issues.append("Missing clear call-to-action (no question or action words)")
    
    # Check average sentence length
    sentences = [s.strip() for s in email.body.replace('?', '.').replace('!', '.').split('.') if s.strip()]
    if sentences:
        avg_words_per_sentence = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_words_per_sentence > 18:
            issues.append(f"Sentences too long (avg {avg_words_per_sentence:.1f} words, keep under 18)")
    
    # Check for corporate jargon
    corporate_jargon = [
        "ensuring consistent",
        "optimizing",
        "measurable results",
        "fragmented effort",
        "unified brand voice",
        "must be a huge",
        "must be challenging",
        "resonate and deliver",
        "massive scale",
        "huge undertaking",
    ]
    for jargon in corporate_jargon:
        if jargon in body_lower:
            issues.append(f"Contains corporate jargon: '{jargon}'")
    
    return issues


async def generate_email(
    lead: Lead,
    sender_name: str,
    tone: str = "professional",
    goal: str = "schedule a meeting",
    product_description: str = "our product"
) -> GeneratedEmail:
    """
    Generate personalized email copy using Google Gemini with quality validation.
    
    Uses manual research notes when available to create highly personalized emails
    that reference specific, recent information about the lead or their company.
    
    Implements retry logic: attempts generation up to 2 times, validating quality
    each time and returning the best attempt.
    
    Args:
        lead: Lead object with contact information and research notes
        sender_name: Name of the person sending the email (for signature)
        tone: Email tone (professional, friendly, casual, direct)
        goal: Email goal (e.g., "schedule a meeting", "get a reply")
        product_description: Description of product/service
        
    Returns:
        GeneratedEmail with subject and body
        
    Raises:
        ValueError: If GEMINI_API_KEY not configured or generation fails
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
    
    # Configure Gemini
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    # Build enriched context from lead data
    lead_context_parts = [f"- Name: {lead.first_name} {lead.last_name}"]
    
    if lead.title:
        lead_context_parts.append(f"- Title: {lead.title}")
    
    if lead.company:
        lead_context_parts.append(f"- Company: {lead.company}")
    
    if lead.industry:
        lead_context_parts.append(f"- Industry: {lead.industry}")
    
    if lead.company_size:
        lead_context_parts.append(f"- Company Size: {lead.company_size}")
    
    if lead.location:
        lead_context_parts.append(f"- Location: {lead.location}")

    if lead.linkedin_url:
        lead_context_parts.append(f"- LinkedIn URL: {lead.linkedin_url}")

    if lead.job_title:
        lead_context_parts.append(f"- LinkedIn Job Title: {lead.job_title}")

    if lead.seniority:
        lead_context_parts.append(f"- Seniority: {lead.seniority}")

    if lead.linkedin_headline:
        lead_context_parts.append(f"- LinkedIn Headline: {lead.linkedin_headline}")
    
    lead_context = "Lead Information:\n" + "\n".join(lead_context_parts)

    # Add enrichment signals (LinkedIn/company intelligence) if present
    research_signals = _extract_lead_research_signals(lead)
    enrichment_section = ""
    if research_signals:
        enrichment_section = "Research Signals (LinkedIn + Enrichment):\n" + "\n".join(f"- {s}" for s in research_signals)
    
    # Add research notes if available (MOST IMPORTANT)
    research_section = ""
    if lead.research_notes:
        research_section = _format_research_notes_prompt(lead.research_notes)
    
    # Build the new, improved prompt
    prompt = f"""You are a top-performing sales rep writing a cold outreach email. Write like you're sending a quick Slack message to a colleague, not a formal business letter. Use short sentences. Be direct. Skip the fluff.

{lead_context}

{research_section}

{enrichment_section}

Email Context:
- Tone: {tone}
- Goal: {goal}
- Product/Service: {product_description}
- Sender: {sender_name}

=== CRITICAL RULES ===

1. OPENING (15-30 words):
   - Start with "{lead.first_name} -" (casual, direct)
   - {"MANDATORY: Use a SPECIFIC detail from the research notes above (hiring numbers, funding, recent posts, specific tools they use)" if lead.research_notes else "reference their role/company in a specific way"}
   - NO generic greetings like "I hope this finds you well"
   
2. PROBLEM/CONTEXT (30-40 words):
   - Connect their situation to a likely problem they face
   - Be specific about the challenge (use numbers, roles, or situations when possible)
   - Make it feel like you understand their world
   
3. SOLUTION PREVIEW (20-30 words):
   - Briefly describe what you offer and the specific benefit
   - Use simple, direct language
   - Connect it directly to the problem mentioned
   
4. CALL TO ACTION (10-15 words):
   - Ask ONE clear question or propose ONE specific action
   - Keep it low-pressure (e.g., "Quick 10-min call?", "Worth a 15-min walkthrough?")
   
5. SIGNATURE:
   - End with: "Best regards,\\n{sender_name}"

=== WRITING STYLE RULES ===
- Use short, punchy sentences (10-15 words average, 20 max)
- Sound like you're texting a smart colleague, not writing a formal letter
- Be direct - get to the point fast
- Use simple words - avoid corporate jargon
- If you mention their scale/size, be specific with numbers ("55 countries" not "massive scale")
- Don't state the obvious ("must be challenging" adds no value - skip it)

=== SPECIFICITY REQUIREMENTS ===
- If research_notes mentions numbers (employees, countries, offices), USE THEM in your email
- If research_notes mentions recent activity (product launch, funding, hiring), REFERENCE IT in first sentence
- If research_notes mentions tech stack, MENTION IT to show you did research
- Don't just say "your scale is massive" - say "operating in 55 countries" or "with 600k employees"
- Don't say "must be challenging" - instead ask a specific question about HOW they handle it

=== VALUE PROP FORMAT ===
Instead of vague: "We help companies centralize their marketing"
Be specific: "We built a dashboard where all regional teams can create campaigns from approved templates"

Instead of: "ensuring every campaign delivers measurable results"
Be specific: "so you don't end up with 10 different versions of the same message"

=== BANNED PHRASES (NEVER USE) ===
- "I came across your profile/company"
- "I hope this email finds you well"
- "wanted to reach out"
- "thought I'd reach out"
- "I'd love to chat"
- "explore how we might"
- "cutting-edge" or "industry-leading"
- "must be a huge undertaking"
- "must be challenging"
- "are you ever finding it difficult"
- "ensuring consistent messaging"
- "optimizing campaign performance"
- "resonates and delivers"
- "measurable results"
- "fragmented effort"
- "unified brand voice"
- "massive scale"
- Any corporate buzzwords

=== EXAMPLE 1 - BAD (too generic and corporate) ===
SUBJECT: Marketing coordination at scale
---
Omkar - with TCS's massive scale, coordinating marketing efforts across so many business units must be a huge undertaking.

Even with excellent internal teams, ensuring consistent messaging and optimizing campaign performance for every sector can easily become fragmented. Are you ever finding it difficult to maintain a unified brand voice across all your global initiatives?

We help companies like TCS centralize their marketing strategy and execution, ensuring every campaign resonates and delivers measurable results, without the fragmented effort.

Worth a quick 15-min chat to see how we tackle this?

Best regards,
{sender_name}

=== EXAMPLE 2 - GOOD (specific and conversational) ===
SUBJECT: TCS's new AI practice rollout
---
Omkar - congrats on launching the AI consulting practice. Saw it's now live in 55 countries.

Quick question: How are you keeping messaging consistent across all those regions? Most teams we work with end up with 10 different versions of the same campaign.

We built {product_description} for exactly this - single hub where regional teams collaborate without bottlenecking through HQ. Works with your Salesforce setup.

15-min walkthrough?

Best regards,
{sender_name}

WHY EXAMPLE 2 IS BETTER:
- References specific recent activity (AI practice launch)
- Uses specific numbers (55 countries)
- Asks a genuine, short question
- Mentions their tech stack (Salesforce)
- Explains the solution specifically, not vaguely
- Shorter sentences, conversational tone
- 78 words vs 93 words

=== CONVERSATIONAL TONE EXAMPLES ===

FORMAL (avoid):
"Are you ever finding it difficult to maintain a unified brand voice across all your global initiatives?"

CONVERSATIONAL (use):
"How do you keep messaging consistent across all those regions?"

---

FORMAL (avoid):
"We help companies like yours centralize their marketing strategy and execution"

CONVERSATIONAL (use):
"We built [tool] for this exact problem"

---

FORMAL (avoid):
"with TCS's massive scale, coordinating marketing must be huge"

CONVERSATIONAL (use):
"with TCS operating in 55 countries"

=== YOUR TASK ===
Write a cold email following ALL rules above. Use research notes/signals if provided. Keep total length 80-120 words.

Format your response EXACTLY as:
SUBJECT: [short, specific subject line - 3-6 words]
---
[email body]

Best regards,
{sender_name}
"""
    
    max_attempts = 2
    best_email: Optional[GeneratedEmail] = None
    best_issues: List[str] = []
    
    for attempt in range(max_attempts):
        try:
            response = model.generate_content(prompt)
            content = response.text.strip()
            
            # Parse response
            if "---" in content:
                parts = content.split("---", 1)
                subject_part = parts[0].strip()
                body = parts[1].strip()
                
                # Extract subject (remove "SUBJECT:" prefix if present)
                if subject_part.startswith("SUBJECT:"):
                    subject = subject_part.replace("SUBJECT:", "").strip()
                else:
                    subject = subject_part
            else:
                # Fallback if format not followed
                lines = content.split("\n", 1)
                subject = lines[0].replace("SUBJECT:", "").strip() if lines else "Follow-up"
                body = lines[1].strip() if len(lines) > 1 else content
            
            email = GeneratedEmail(subject=subject, body=body)
            
            # Check quality
            issues = _check_email_quality(email, lead)
            
            # If no issues, return immediately
            if not issues:
                return email
            
            # Track best attempt
            if best_email is None or len(issues) < len(best_issues):
                best_email = email
                best_issues = issues
            
            # If this is not the last attempt and we found issues, try again
            if attempt < max_attempts - 1:
                # Modify prompt for retry to address specific issues
                prompt += f"\n\nPREVIOUS ATTEMPT HAD ISSUES:\n" + "\n".join(f"- {issue}" for issue in issues) + "\n\nPlease fix these issues in your next attempt."
                continue
            
        except Exception as e:
            if attempt == max_attempts - 1:
                # On last attempt, raise the error
                raise ValueError(f"Failed to generate email after {max_attempts} attempts: {str(e)}")
            # Otherwise, try again
            continue
    
    # Return best attempt even if it has some issues
    if best_email:
        return best_email
    
    raise ValueError("Failed to generate email: No valid attempts produced")

