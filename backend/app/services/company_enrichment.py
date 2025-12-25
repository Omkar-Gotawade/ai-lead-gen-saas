"""Company Enrichment service using AI to analyze and enrich company data.

Uses Google Gemini AI to:
- Summarize company information
- Detect industry
- Identify pain points
- Extract key insights
"""
from typing import Dict, Optional
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)


class CompanyEnrichmentService:
    """Service for AI-powered company data enrichment."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        """Initialize enrichment service.
        
        Args:
            api_key: Google Gemini API key
            model: Gemini model to use
        """
        self.api_key = api_key
        self.model = model
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)
    
    def enrich_company(
        self,
        company_name: Optional[str],
        company_description: Optional[str],
        raw_content: str,
        domain: str
    ) -> Dict[str, any]:
        """Enrich company data using AI.
        
        Args:
            company_name: Extracted company name (may be None)
            company_description: Extracted description (may be None)
            raw_content: Raw scraped content from website
            domain: Company domain
            
        Returns:
            Dict with enriched data:
            {
                'summary': str,
                'industry': str,
                'pain_points': List[str],
                'key_insights': str,
                'confidence': str ('high', 'medium', 'low')
            }
        """
        try:
            # Prepare content for AI (limit size)
            content_sample = self._prepare_content(raw_content, company_name, company_description)
            
            # Build prompt
            prompt = self._build_enrichment_prompt(content_sample, domain)
            
            # Build full prompt with system context
            full_prompt = (
                "You are a business intelligence analyst specializing in B2B company research.\n\n"
                + prompt
            )
            
            # Call Gemini
            response = self.client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=500,
                )
            )
            
            # Parse response
            ai_response = response.text.strip()
            enriched_data = self._parse_ai_response(ai_response)
            
            logger.info(f"Successfully enriched company data for {domain}")
            return enriched_data
            
        except Exception as e:
            logger.error(f"Failed to enrich company {domain}: {str(e)}")
            # Return fallback data
            return self._fallback_enrichment(company_name, company_description, domain)
    
    def _prepare_content(
        self,
        raw_content: str,
        company_name: Optional[str],
        company_description: Optional[str]
    ) -> str:
        """Prepare content for AI analysis.
        
        Args:
            raw_content: Raw scraped content
            company_name: Company name
            company_description: Company description
            
        Returns:
            Prepared content string
        """
        parts = []
        
        if company_name:
            parts.append(f"Company Name: {company_name}")
        
        if company_description:
            parts.append(f"Description: {company_description}")
        
        # Limit raw content to 2000 chars
        if raw_content:
            content_sample = raw_content[:2000]
            parts.append(f"Website Content:\n{content_sample}")
        
        return "\n\n".join(parts)
    
    def _build_enrichment_prompt(self, content: str, domain: str) -> str:
        """Build prompt for AI enrichment.
        
        Args:
            content: Prepared content
            domain: Company domain
            
        Returns:
            Prompt string
        """
        return f"""Analyze this company information and provide a structured analysis:

{content}

Domain: {domain}

Please provide:
1. SUMMARY: A concise 2-3 sentence summary of what this company does
2. INDUSTRY: The primary industry (e.g., "SaaS", "E-commerce", "Healthcare Tech", "Marketing Agency")
3. PAIN_POINTS: 2-3 likely business pain points this company might have (comma-separated)
4. KEY_INSIGHTS: One key insight about this company's market position or offering

Format your response EXACTLY as:
SUMMARY: [your summary]
INDUSTRY: [industry]
PAIN_POINTS: [point 1], [point 2], [point 3]
KEY_INSIGHTS: [your insight]
CONFIDENCE: [high/medium/low]
"""
    
    def _parse_ai_response(self, response: str) -> Dict[str, any]:
        """Parse structured AI response.
        
        Args:
            response: AI response text
            
        Returns:
            Parsed enrichment data
        """
        data = {
            'summary': '',
            'industry': 'Unknown',
            'pain_points': [],
            'key_insights': '',
            'confidence': 'low'
        }
        
        # Parse line by line
        for line in response.split('\n'):
            line = line.strip()
            
            if line.startswith('SUMMARY:'):
                data['summary'] = line.replace('SUMMARY:', '').strip()
            elif line.startswith('INDUSTRY:'):
                data['industry'] = line.replace('INDUSTRY:', '').strip()
            elif line.startswith('PAIN_POINTS:'):
                points_str = line.replace('PAIN_POINTS:', '').strip()
                data['pain_points'] = [p.strip() for p in points_str.split(',') if p.strip()]
            elif line.startswith('KEY_INSIGHTS:'):
                data['key_insights'] = line.replace('KEY_INSIGHTS:', '').strip()
            elif line.startswith('CONFIDENCE:'):
                confidence = line.replace('CONFIDENCE:', '').strip().lower()
                if confidence in ['high', 'medium', 'low']:
                    data['confidence'] = confidence
        
        return data
    
    def _fallback_enrichment(
        self,
        company_name: Optional[str],
        company_description: Optional[str],
        domain: str
    ) -> Dict[str, any]:
        """Provide fallback enrichment when AI fails.
        
        Args:
            company_name: Company name
            company_description: Company description
            domain: Domain
            
        Returns:
            Basic enrichment data
        """
        summary = company_description if company_description else f"Company website: {domain}"
        
        return {
            'summary': summary[:200],
            'industry': 'Unknown',
            'pain_points': [],
            'key_insights': 'Manual review required',
            'confidence': 'low'
        }


# Convenience function
def enrich_company_data(
    company_name: Optional[str],
    company_description: Optional[str],
    raw_content: str,
    domain: str,
    api_key: str,
    model: str = "gemini-1.5-flash"
) -> Dict[str, any]:
    """Convenience function to enrich company data.
    
    Args:
        company_name: Company name
        company_description: Company description
        raw_content: Raw scraped content
        domain: Company domain
        api_key: Google Gemini API key
        model: Gemini model to use
        
    Returns:
        Enriched data dict
    """
    service = CompanyEnrichmentService(api_key=api_key, model=model)
    return service.enrich_company(company_name, company_description, raw_content, domain)
