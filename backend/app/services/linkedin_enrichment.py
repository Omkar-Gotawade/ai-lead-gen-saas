"""LinkedIn Profile Enrichment service.

This service enriches lead data using LinkedIn profile URLs.
Uses 3rd-party enrichment APIs (Clearbit, Apollo, Snov.io) to fetch:
- Job title
- Seniority level
- Company size
- LinkedIn headline

IMPORTANT: This does NOT scrape LinkedIn directly (which violates ToS).
It uses legitimate enrichment APIs that have proper LinkedIn partnerships.
"""
from typing import Dict, Optional
import logging
import requests

logger = logging.getLogger(__name__)


class LinkedInEnrichmentService:
    """Service for LinkedIn profile enrichment via 3rd-party APIs."""
    
    # Supported enrichment providers
    PROVIDERS = {
        'clearbit': 'https://person-stream.clearbit.com/v2/combined/find',
        'apollo': 'https://api.apollo.io/v1/people/match',
        'snov': 'https://api.snov.io/v1/get-profile-by-url'
    }
    
    def __init__(
        self,
        provider: str = 'clearbit',
        api_key: Optional[str] = None
    ):
        """Initialize LinkedIn enrichment service.
        
        Args:
            provider: Enrichment provider ('clearbit', 'apollo', 'snov')
            api_key: API key for the provider
        """
        self.provider = provider.lower()
        self.api_key = api_key
        
        if self.provider not in self.PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def enrich_from_linkedin_url(self, linkedin_url: str) -> Dict[str, any]:
        """Enrich lead data from LinkedIn URL.
        
        Args:
            linkedin_url: LinkedIn profile URL
            
        Returns:
            Dict with enriched data:
            {
                'job_title': str or None,
                'seniority': str or None,
                'company_size': str or None,
                'linkedin_headline': str or None,
                'success': bool,
                'error': str or None
            }
        """
        result = {
            'job_title': None,
            'seniority': None,
            'company_size': None,
            'linkedin_headline': None,
            'success': False,
            'error': None
        }
        
        try:
            if not self.api_key:
                result['error'] = "No API key provided for enrichment"
                return result
            
            # Route to appropriate provider
            if self.provider == 'clearbit':
                return self._enrich_with_clearbit(linkedin_url)
            elif self.provider == 'apollo':
                return self._enrich_with_apollo(linkedin_url)
            elif self.provider == 'snov':
                return self._enrich_with_snov(linkedin_url)
            else:
                result['error'] = f"Provider {self.provider} not implemented"
                return result
                
        except Exception as e:
            logger.error(f"LinkedIn enrichment failed: {str(e)}")
            result['error'] = str(e)
            return result
    
    def _enrich_with_clearbit(self, linkedin_url: str) -> Dict[str, any]:
        """Enrich using Clearbit API.
        
        Args:
            linkedin_url: LinkedIn profile URL
            
        Returns:
            Enriched data dict
        """
        result = {
            'job_title': None,
            'seniority': None,
            'company_size': None,
            'linkedin_headline': None,
            'success': False,
            'error': None
        }
        
        try:
            # Extract LinkedIn username from URL
            # Example: https://linkedin.com/in/username -> username
            username = linkedin_url.rstrip('/').split('/')[-1]
            
            # Clearbit API call
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            params = {
                'linkedin': linkedin_url
            }
            
            response = requests.get(
                self.PROVIDERS['clearbit'],
                headers=headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract person data
                person = data.get('person', {})
                employment = person.get('employment', {})
                
                result['job_title'] = employment.get('title')
                result['seniority'] = employment.get('seniority')
                result['linkedin_headline'] = person.get('bio')
                
                # Extract company size
                company = data.get('company', {})
                metrics = company.get('metrics', {})
                employees = metrics.get('employees')
                if employees:
                    result['company_size'] = self._format_company_size(employees)
                
                result['success'] = True
                logger.info(f"Successfully enriched LinkedIn profile: {linkedin_url}")
                
            elif response.status_code == 404:
                result['error'] = "Profile not found"
            else:
                result['error'] = f"API error: {response.status_code}"
                
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Clearbit enrichment failed: {str(e)}")
        
        return result
    
    def _enrich_with_apollo(self, linkedin_url: str) -> Dict[str, any]:
        """Enrich using Apollo.io API.
        
        Args:
            linkedin_url: LinkedIn profile URL
            
        Returns:
            Enriched data dict
        """
        result = {
            'job_title': None,
            'seniority': None,
            'company_size': None,
            'linkedin_headline': None,
            'success': False,
            'error': None
        }
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            }
            
            payload = {
                'api_key': self.api_key,
                'linkedin_url': linkedin_url
            }
            
            response = requests.post(
                self.PROVIDERS['apollo'],
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                person = data.get('person', {})
                
                result['job_title'] = person.get('title')
                result['seniority'] = person.get('seniority')
                result['linkedin_headline'] = person.get('headline')
                
                # Company size from organization
                organization = person.get('organization', {})
                employees = organization.get('estimated_num_employees')
                if employees:
                    result['company_size'] = self._format_company_size(employees)
                
                result['success'] = True
                logger.info(f"Successfully enriched with Apollo: {linkedin_url}")
                
            else:
                result['error'] = f"Apollo API error: {response.status_code}"
                
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Apollo enrichment failed: {str(e)}")
        
        return result
    
    def _enrich_with_snov(self, linkedin_url: str) -> Dict[str, any]:
        """Enrich using Snov.io API.
        
        Args:
            linkedin_url: LinkedIn profile URL
            
        Returns:
            Enriched data dict
        """
        result = {
            'job_title': None,
            'seniority': None,
            'company_size': None,
            'linkedin_headline': None,
            'success': False,
            'error': None
        }
        
        try:
            params = {
                'profile_url': linkedin_url,
                'access_token': self.api_key
            }
            
            response = requests.post(
                self.PROVIDERS['snov'],
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                result['job_title'] = data.get('current_job_title')
                result['seniority'] = data.get('seniority')
                result['linkedin_headline'] = data.get('headline')
                
                # Company info
                company = data.get('company', {})
                size = company.get('size')
                if size:
                    result['company_size'] = size
                
                result['success'] = True
                logger.info(f"Successfully enriched with Snov.io: {linkedin_url}")
                
            else:
                result['error'] = f"Snov.io API error: {response.status_code}"
                
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Snov.io enrichment failed: {str(e)}")
        
        return result
    
    def _format_company_size(self, employees: int) -> str:
        """Format employee count into size range.
        
        Args:
            employees: Number of employees
            
        Returns:
            Size range string
        """
        if employees < 10:
            return "1-10"
        elif employees < 50:
            return "11-50"
        elif employees < 200:
            return "51-200"
        elif employees < 500:
            return "201-500"
        elif employees < 1000:
            return "501-1000"
        elif employees < 5000:
            return "1001-5000"
        else:
            return "5000+"


# Convenience function
def enrich_linkedin_profile(
    linkedin_url: str,
    provider: str = 'clearbit',
    api_key: Optional[str] = None
) -> Dict[str, any]:
    """Convenience function to enrich LinkedIn profile.
    
    Args:
        linkedin_url: LinkedIn profile URL
        provider: Enrichment provider
        api_key: API key
        
    Returns:
        Enriched data dict
    """
    service = LinkedInEnrichmentService(provider=provider, api_key=api_key)
    return service.enrich_from_linkedin_url(linkedin_url)
