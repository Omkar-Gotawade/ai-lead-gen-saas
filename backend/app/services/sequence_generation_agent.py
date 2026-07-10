"""Sequence Generation Agent — AI sequence writing service.

Uses OpenRouter to generate a multi-step campaign sequence based on user input.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Dict, List

from pydantic import BaseModel

from app.services.ai_email_service import _request_openrouter_completion

logger = logging.getLogger(__name__)


class GeneratedSequenceStep(BaseModel):
    step: int
    purpose: str
    subject: str
    body: str


_SEQUENCE_AGENT_PROMPT_TEMPLATE = """\
You are an expert SDR and cold email copywriter. You write sequences that feel entirely human, natural, and never like they were built by AI or an automated tool.

CAMPAIGN CONTEXT:
Product/Service: {product_name}
Description: {product_description}
Target Audience: {target_audience}
Campaign Goal: {campaign_goal}
Tone: {tone}

YOUR TASK:
Write exactly {number_of_steps} email sequence steps for this campaign.

STRICT RULES:

STEP 1 (The Opener):
- 70–110 words
- Subject: 2-5 words, lowercase preferred, curiosity-focused (e.g., "quick question", "idea for {{company}}")
- Line 1: Observation/context. E.g., "Saw {{company}} has been..."
- Line 2: Connect to a problem
- Line 3: What you offer (rephrase "{product_description}" naturally, do NOT copy-paste)
- Line 4: Low-pressure CTA (e.g., "Worth a quick chat?")
- Sign off: {{sender_name}}

STEPS 2+ (Follow-ups):
- 40–70 words maximum
- Subject: Often starts with "Re: " + Step 1's subject
- NEVER repeat the pitch or product description.
- Reference the previous email briefly (e.g., "Just bringing this back up...")
- Add one new angle, insight, or softer CTA (e.g., "Open to a quick look?")
- Sign off: {{sender_name}}

TEMPLATE VARIABLES (Use exactly these where appropriate):
- {{first_name}}
- {{company}}
- {{sender_name}}

BANNED PHRASES (NEVER USE):
- "I hope this email finds you well"
- "I wanted to reach out"
- "Given your focus on"
- "In today's competitive landscape"
- "Revolutionary", "Cutting-edge", "Transform", "Unlock", "Synergy", "Leverage"

Write as if you are typing this in Gmail directly to a prospect.
Slightly imperfect is fine — perfect grammar feels AI-written.

RESPOND IN THIS EXACT JSON FORMAT (no markdown, no extra text):
[
  {{
    "step": 1,
    "purpose": "start conversation",
    "subject": "quick question",
    "body": "Hi {{first_name}},\n\nSaw {{company}} has been growing...\n\nWorth a quick chat?\n\n{{sender_name}}"
  }},
  {{
    "step": 2,
    "purpose": "gentle follow-up",
    "subject": "Re: quick question",
    "body": "Hi {{first_name}},\n\nJust bringing this back up...\n\nOpen to a quick look?\n\n{{sender_name}}"
  }}
]
"""

def _parse_sequence_steps(raw: str) -> List[GeneratedSequenceStep]:
    """Parse JSON array of sequence steps, tolerating markdown fences."""
    text = raw.strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```[a-z]*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n?```$", "", text)
    text = text.strip()

    # Extract first JSON array found
    match = re.search(r"\[.*\]", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Sequence Agent returned no JSON array: {raw[:200]}")

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        logger.error(f"Raw string was: {match.group()}")
        raise ValueError("Invalid JSON returned by Sequence Agent")

    steps = []
    for item in data:
        steps.append(GeneratedSequenceStep(
            step=int(item.get("step", 0)),
            purpose=str(item.get("purpose", "")),
            subject=str(item.get("subject", "")),
            body=str(item.get("body", ""))
        ))
    
    # Sort just in case
    steps.sort(key=lambda x: x.step)
    return steps


async def generate_sequence(
    product_name: str,
    product_description: str,
    target_audience: str,
    campaign_goal: str,
    tone: str,
    number_of_steps: int
) -> List[GeneratedSequenceStep]:
    """
    Generate an AI sequence.
    """
    prompt = _SEQUENCE_AGENT_PROMPT_TEMPLATE.format(
        product_name=product_name,
        product_description=product_description,
        target_audience=target_audience,
        campaign_goal=campaign_goal,
        tone=tone,
        number_of_steps=number_of_steps
    )
    
    raw = await asyncio.to_thread(_request_openrouter_completion, prompt)
    steps = _parse_sequence_steps(raw)
    
    if not steps:
         raise ValueError("Sequence Agent failed to generate steps.")
         
    return steps
