"""AI email generation service using Google Gemini."""
from typing import Optional
import google.generativeai as genai
from app.config import settings
from app.models.lead import Lead
from pydantic import BaseModel


class GeneratedEmail(BaseModel):
    """Generated email response."""
    subject: str
    body: str


async def generate_email(
    lead: Lead,
    sender_name: str,
    tone: str = "professional",
    goal: str = "schedule a meeting",
    product_description: str = "our product"
) -> GeneratedEmail:
    """
    Generate personalized email copy using Google Gemini.
    
    Args:
        lead: Lead object with contact information
        sender_name: Name of the person sending the email (for signature)
        tone: Email tone (formal, friendly, casual, aggressive)
        goal: Email goal (e.g., "book a demo", "get a reply")
        product_description: Description of product/service
        
    Returns:
        GeneratedEmail with subject and body
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
    
    # Configure Gemini
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    # Build context from lead data
    lead_context = f"""
Lead Information:
- Name: {lead.first_name} {lead.last_name}
- Title: {lead.title or 'N/A'}
- Company: {lead.company or 'N/A'}
- Industry: {lead.industry or 'N/A'}
"""
    
    # Build prompt
    prompt = f"""You are an expert cold email copywriter. Write a personalized cold email with the following requirements:

{lead_context}

Email Requirements:
- Tone: {tone}
- Goal: {goal}
- Product/Service: {product_description}
- Sender's Name: {sender_name}

Guidelines:
- Keep it concise (under 150 words)
- Personalize based on the lead's title and company
- Make it conversational and human
- Include a clear call-to-action
- No buzzwords or corporate jargon
- IMPORTANT: End with proper email signature: "Best regards,\\n{sender_name}"
- Format: Return ONLY the subject line and body (including signature), separated by "---"

Format your response exactly as:
SUBJECT: [subject line here]
---
[email body here]

Best regards,
{sender_name}
"""
    
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
        
        return GeneratedEmail(subject=subject, body=body)
        
    except Exception as e:
        raise ValueError(f"Failed to generate email: {str(e)}")
