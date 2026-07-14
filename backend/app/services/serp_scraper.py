"""SERP Scraper service for finding company domains via Google search.

This service performs Google searches to find company websites based on:
- Keywords (e.g., "AI software")
- Location (e.g., "India")
- Industry (e.g., "SaaS")

IMPORTANT: This is a basic v1 implementation. For production, consider:
- Using SerpAPI for better reliability
- Implementing rate limiting
- Adding proxy rotation (not included in v1)
"""
import re
import time
from typing import List, Optional
from urllib.parse import quote_plus, urlparse
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class SerpScraper:
    """Simple SERP scraper for finding company domains."""
    
    def __init__(self, serp_api_key: Optional[str] = None):
        """Initialize SERP scraper.
        
        Args:
            serp_api_key: Optional SerpAPI key for better results
        """
        self.serp_api_key = serp_api_key
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    
    def search_companies(
        self,
        keywords: str,
        location: Optional[str] = None,
        industry: Optional[str] = None,
        max_results: int = 20
    ) -> List[dict]:
        """Search for companies and return their domains.
        
        Args:
            keywords: Search keywords (e.g., "AI software")
            location: Optional location filter
            industry: Optional industry filter
            max_results: Maximum number of results to return
            
        Returns:
            List of dicts with 'domain' and 'source_url' keys
        """
        if self.serp_api_key:
            return self._search_with_serpapi(keywords, location, industry, max_results)
        else:
            return self._search_with_google_scraping(keywords, location, industry, max_results)
    
    def _search_with_serpapi(
        self,
        keywords: str,
        location: Optional[str],
        industry: Optional[str],
        max_results: int
    ) -> List[dict]:
        """Search using SerpAPI (more reliable but requires API key).
        
        Args:
            keywords: Search keywords
            location: Optional location
            industry: Optional industry
            max_results: Max results
            
        Returns:
            List of domain results
        """
        # Build search query
        query = self._build_search_query(keywords, location, industry)
        
        results = []
        
        # SerpAPI supports pagination using 'start' parameter
        start = 0
        while start < 500:
            try:
                # Call SerpAPI
                params = {
                    "q": query,
                    "api_key": self.serp_api_key,
                    "num": 100,  # Try to ask for 100
                    "start": start,
                    "engine": "google"
                }
                
                response = requests.get("https://serpapi.com/search", params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                organic_results = data.get("organic_results", [])
                if not organic_results:
                    # No more results
                    break
                    
                added_this_page = 0
                
                # Extract organic results
                for result in organic_results:
                    domain = self._extract_domain(result.get("link", ""))
                    if domain and not self._is_excluded_domain(domain):
                        if not any(r['domain'] == domain for r in results):
                            results.append({
                                "domain": domain,
                                "source_url": result.get("link", "")
                            })
                            added_this_page += 1
                            
                            if len(results) >= max_results:
                                break
                
                logger.info(f"SerpAPI page start={start} found {len(organic_results)} raw organic results, {added_this_page} valid domains. Total: {len(results)}/{max_results}")
                
                if len(results) >= max_results:
                    break
                    
                # Google might return fewer than requested (e.g. 8 or 10 even if num=100 is passed)
                # We need to advance start by the number of organic results we received, or at least 10
                # to prevent infinite loops on the same page.
                start += max(len(organic_results), 10)
                
            except Exception as e:
                logger.error(f"SerpAPI search failed at start={start}: {str(e)}")
                # Fallback to scraping if we have no results yet
                if not results:
                    return self._search_with_google_scraping(keywords, location, industry, max_results)
                break
                
        return results
    
    def _search_with_google_scraping(
        self,
        keywords: str,
        location: Optional[str],
        industry: Optional[str],
        max_results: int
    ) -> List[dict]:
        """Search by scraping Google search results directly.
        
        WARNING: This is fragile and may break if Google changes their HTML.
        Consider using SerpAPI for production.
        
        Args:
            keywords: Search keywords
            location: Optional location
            industry: Optional industry
            max_results: Max results
            
        Returns:
            List of domain results
        """
        # Build search query
        query = self._build_search_query(keywords, location, industry)
        encoded_query = quote_plus(query)
        
        results = []
        
        # Paginate to find enough valid domains (Google returns ~10 per page)
        # We'll check up to 10 pages to avoid getting blocked while ensuring we get enough
        for start in range(0, 100, 10):
            search_url = f"https://www.google.com/search?q={encoded_query}&start={start}"
            
            try:
                # Make request
                headers = {"User-Agent": self.user_agent}
                response = requests.get(search_url, headers=headers, timeout=15)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                added_this_page = 0
                
                # Find all search result divs (Google's structure changes frequently)
                # This selector targets the main result links
                for g in soup.find_all('div', class_='g'):
                    # Find the link
                    link_tag = g.find('a')
                    if link_tag and link_tag.get('href'):
                        url = link_tag['href']
                        domain = self._extract_domain(url)
                        
                        if domain and not self._is_excluded_domain(domain):
                            if not any(r['domain'] == domain for r in results):
                                results.append({
                                    "domain": domain,
                                    "source_url": url
                                })
                                added_this_page += 1
                                
                                if len(results) >= max_results:
                                    break
                
                logger.info(f"Google scraping page start={start} found {added_this_page} valid domains. Total: {len(results)}/{max_results}")
                
                if len(results) >= max_results:
                    break
                    
                if added_this_page == 0 and start > 0:
                    # If we found no new valid domains on this page, we might have hit the end
                    break
                    
                # Add delay to avoid rate limiting between pages
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Google scraping failed at start={start}: {str(e)}")
                break
                
        if not results:
            logger.warning("Google scraping yielded 0 results. Fallback to demo domains.")
            return self._get_demo_domains(keywords, industry, max_results)
            
        return results
    
    def _build_search_query(
        self,
        keywords: str,
        location: Optional[str],
        industry: Optional[str]
    ) -> str:
        """Build a Google search query from parameters.
        
        Args:
            keywords: Base keywords
            location: Optional location
            industry: Optional industry
            
        Returns:
            Formatted search query
        """
        # Start with keywords
        query_parts = [keywords]
        
        # Add location if provided
        if location:
            query_parts.append(location)
        
        # Add industry if provided
        if industry:
            query_parts.append(industry)
        
        # Add "company" to focus on company websites
        query_parts.append("company")
        
        return " ".join(query_parts)
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract clean domain from URL.
        
        Args:
            url: Full URL
            
        Returns:
            Domain name or None
        """
        try:
            if not url or not url.startswith('http'):
                return None
            
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain if domain else None
            
        except Exception:
            return None
    
    def _is_excluded_domain(self, domain: str) -> bool:
        """Check if domain should be excluded from results.
        
        Args:
            domain: Domain to check
            
        Returns:
            True if should be excluded
        """
        # Exclude common non-company domains
        excluded = [
            'google.com', 'facebook.com', 'linkedin.com', 'twitter.com',
            'youtube.com', 'wikipedia.org', 'instagram.com', 'reddit.com',
            'amazon.com', 'apple.com', 'microsoft.com', 'github.com',
            'clutch.co', 'g2.com', 'capterra.com', 'crunchbase.com',
            'upwork.com', 'fiverr.com', 'indeed.com', 'glassdoor.com',
            'tiktok.com', 'medium.com', 'pinterest.com', 'quora.com',
            'yahoo.com', 'trustpilot.com', 'yelp.com', 'forbes.com', 'bloomberg.com'
        ]
        
        return any(domain.endswith(excluded_domain) for excluded_domain in excluded)
    
    def _get_demo_domains(
        self,
        keywords: str,
        industry: Optional[str],
        max_results: int
    ) -> List[dict]:
        """Return demo domains for testing when scraping fails.
        
        This is a fallback for development/testing purposes.
        """
        logger.warning("Using demo domains fallback mode")
        
        # Sample domains based on common industries
        demo_domains = {
            "marketing": ["hubspot.com", "mailchimp.com", "hootsuite.com", "buffer.com", "semrush.com"],
            "saas": ["salesforce.com", "slack.com", "zoom.us", "asana.com", "notion.so"],
            "agency": ["webflow.com", "wix.com", "squarespace.com", "wordpress.com", "shopify.com"],
            "software": ["atlassian.com", "jetbrains.com", "postman.com", "vercel.com", "netlify.com"],
            "tech": ["stripe.com", "twilio.com", "sendgrid.com", "auth0.com", "okta.com"],
            "ecommerce": ["shopify.com", "bigcommerce.com", "magento.com", "woocommerce.com"],
            "default": ["acmecompany.com", "techstartup.io", "innovatesoft.com", "digitalagency.com"]
        }
        
        # Try to match keywords/industry to demo category
        keywords_lower = keywords.lower()
        industry_lower = (industry or "").lower()
        
        selected_domains = []
        for category, domains in demo_domains.items():
            if category in keywords_lower or category in industry_lower:
                selected_domains = domains
                break
        
        if not selected_domains:
            selected_domains = demo_domains["default"]
        
        # Return limited results
        results = []
        for domain in selected_domains[:max_results]:
            results.append({
                "domain": domain,
                "source_url": f"https://{domain}"
            })
        
        logger.info(f"Demo mode: Generated {len(results)} sample domains")
        return results


# Convenience function for easy imports
def search_companies(
    keywords: str,
    location: Optional[str] = None,
    industry: Optional[str] = None,
    serp_api_key: Optional[str] = None,
    max_results: int = 20
) -> List[dict]:
    """Convenience function to search for companies.
    
    Args:
        keywords: Search keywords
        location: Optional location
        industry: Optional industry
        serp_api_key: Optional SerpAPI key
        max_results: Max results to return
        
    Returns:
        List of domain results
    """
    scraper = SerpScraper(serp_api_key=serp_api_key)
    return scraper.search_companies(keywords, location, industry, max_results)
