"""Domain Crawler service for extracting company information from websites.

This service crawls company websites to extract:
- Company name
- Company description
- Email addresses
- Contact information

Crawls multiple pages: /, /about, /contact
"""
import re
import time
from typing import List, Optional, Dict
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class DomainCrawler:
    """Crawler for extracting company information from websites."""
    
    # Core pages to crawl for company info
    PAGES_TO_CRAWL = ['/', '/about', '/about-us', '/contact', '/contact-us']

    # Signal-rich pages — crawled specifically for buying signal extraction
    SIGNAL_PAGES = [
        ('home',         '/'),
        ('about',        '/about'),
        ('about',        '/about-us'),
        ('blog',         '/blog'),
        ('blog',         '/news'),
        ('press',        '/press'),
        ('press',        '/press-releases'),
        ('press',        '/media'),
        ('careers',      '/careers'),
        ('careers',      '/jobs'),
        ('careers',      '/join-us'),
        ('products',     '/products'),
        ('products',     '/solutions'),
        ('services',     '/services'),
        ('case_studies', '/case-studies'),
        ('case_studies', '/customers'),
        ('partners',     '/partners'),
        ('partners',     '/partnerships'),
        ('investors',    '/investors'),
    ]
    
    # Email regex pattern
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    def __init__(self, timeout: int = 10, max_content_length: int = 500000):
        """Initialize domain crawler.
        
        Args:
            timeout: Request timeout in seconds
            max_content_length: Max content size to download (500KB default)
        """
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    
    def crawl_domain(self, domain: str) -> Dict[str, any]:
        """Crawl a domain and extract company information.
        
        Args:
            domain: Domain to crawl (e.g., "example.com")
            
        Returns:
            Dict with extracted information:
            {
                'company_name': str or None,
                'company_description': str or None,
                'emails': List[str],
                'raw_content': str (combined text from all pages),
                'success': bool,
                'error': str or None
            }
        """
        result = {
            'company_name': None,
            'company_description': None,
            'emails': [],
            'raw_content': '',
            'success': False,
            'error': None
        }
        
        try:
            # Ensure domain has protocol
            if not domain.startswith('http'):
                domain = f"https://{domain}"
            
            # Parse domain
            parsed = urlparse(domain)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            # Crawl each page
            all_text = []
            all_emails = set()
            
            for page_path in self.PAGES_TO_CRAWL:
                try:
                    page_url = urljoin(base_url, page_path)
                    page_result = self._crawl_page(page_url)
                    
                    if page_result['success']:
                        all_text.append(page_result['text'])
                        all_emails.update(page_result['emails'])
                        
                        # Try to extract company name from homepage title
                        if page_path == '/' and not result['company_name']:
                            result['company_name'] = page_result.get('title')
                    
                    # Add delay between requests
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.debug(f"Failed to crawl {page_url}: {str(e)}")
                    continue
            
            # Combine results
            if all_text:
                result['raw_content'] = '\n\n'.join(all_text)
                result['emails'] = list(all_emails)
                result['success'] = True
                
                # Try to extract description from content
                result['company_description'] = self._extract_description(result['raw_content'])
            else:
                result['error'] = "No pages could be crawled successfully"
            
            logger.info(f"Crawled {domain}: {len(all_emails)} emails found")
            
        except Exception as e:
            logger.error(f"Failed to crawl domain {domain}: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def _crawl_page(self, url: str) -> Dict[str, any]:
        """Crawl a single page.
        
        Args:
            url: Page URL to crawl
            
        Returns:
            Dict with page information
        """
        result = {
            'success': False,
            'text': '',
            'title': None,
            'emails': set(),
            'error': None
        }
        
        try:
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True,
                stream=True
            )
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type.lower():
                result['error'] = f"Not HTML content: {content_type}"
                return result
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_content_length:
                result['error'] = "Content too large"
                return result
            
            # Read content with size limit
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > self.max_content_length:
                    break
            
            # Parse HTML
            soup = BeautifulSoup(content, 'html.parser')

            # --- Pass 1: scan raw HTML for emails (catches JS vars, data-* attrs, etc.) ---
            raw_html = content.decode('utf-8', errors='ignore')
            emails_from_raw = set(self.EMAIL_PATTERN.findall(raw_html))

            # --- Pass 2: extract mailto: href links ---
            emails_from_mailto = set()
            for tag in soup.find_all('a', href=True):
                href = tag['href']
                if href.lower().startswith('mailto:'):
                    # Strip "mailto:" prefix and any query params (?subject=...)
                    address = href[7:].split('?')[0].strip()
                    if address:
                        emails_from_mailto.add(address)

            # Remove script and style tags before extracting visible text
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()

            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                result['title'] = title_tag.get_text().strip()

            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            result['text'] = self._clean_text(text)

            # --- Merge all email sources ---
            emails_from_text = set(self.EMAIL_PATTERN.findall(text))
            all_emails = emails_from_text | emails_from_mailto | emails_from_raw

            # Filter out common non-contact emails
            result['emails'] = {
                email for email in all_emails
                if not self._is_excluded_email(email)
            }

            if emails_from_mailto:
                logger.debug(f"mailto: links found at {url}: {emails_from_mailto}")
            extra = emails_from_raw - emails_from_text
            if extra:
                logger.debug(f"Emails found via raw HTML scan at {url}: {extra}")
            
            result['success'] = True
            
        except requests.RequestException as e:
            result['error'] = f"Request failed: {str(e)}"
        except Exception as e:
            result['error'] = f"Parsing failed: {str(e)}"
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        
        # Limit total length
        cleaned = '\n'.join(lines)
        if len(cleaned) > 10000:
            cleaned = cleaned[:10000] + '...'
        
        return cleaned
    
    def _extract_description(self, text: str) -> Optional[str]:
        """Try to extract a company description from text.
        
        Args:
            text: Full page text
            
        Returns:
            Description or None
        """
        # Look for common patterns
        patterns = [
            r'(?:we are|we\'re)\s+([^.!?]{20,200})',
            r'(?:about us|about)\s*[:\-]?\s*([^.!?]{20,200})',
            r'(?:our mission|our goal)\s*[:\-]?\s*([^.!?]{20,200})',
        ]
        
        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                # Return first 200 chars of match
                description = match.group(1).strip()
                if len(description) > 200:
                    description = description[:200] + '...'
                return description
        
        # Fallback: return first paragraph-like text
        lines = [line for line in text.split('\n') if len(line) > 50]
        if lines:
            description = lines[0][:200]
            if len(lines[0]) > 200:
                description += '...'
            return description
        
        return None
    
    def _is_excluded_email(self, email: str) -> bool:
        """Check if email should be excluded.
        
        Args:
            email: Email to check
            
        Returns:
            True if should be excluded
        """
        email_lower = email.lower()
        
        # Exclude common non-contact emails
        excluded_patterns = [
            'noreply@', 'no-reply@', 'donotreply@',
            'info@example', 'test@', 'admin@example',
            'support@wordpress', 'example@example'
        ]
        
        return any(pattern in email_lower for pattern in excluded_patterns)


    def crawl_for_signals(self, domain: str) -> Dict[str, any]:
        """Crawl signal-rich pages on a domain and return structured section text.

        Returns a dict keyed by section type (home, blog, press, careers, etc.)
        with the cleaned text for each successfully fetched page.  Individual
        page failures are silently skipped — the caller always gets a (possibly
        empty) dict.

        Args:
            domain: Company domain, e.g. "acme.com" or "https://acme.com"

        Returns:
            {
                "home": "...",
                "blog": "...",
                "press": "...",
                "careers": "...",
                "products": "...",
                ...
                "domain": "acme.com",
                "success": True,
            }
        """
        # Normalise domain
        if not domain.startswith('http'):
            domain = f"https://{domain}"
        parsed = urlparse(domain)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        clean_domain = parsed.netloc.lstrip('www.')

        sections: Dict[str, list] = {}
        seen_urls: set = set()

        for section, path in self.SIGNAL_PAGES:
            page_url = urljoin(base_url, path)
            if page_url in seen_urls:
                continue
            seen_urls.add(page_url)

            try:
                result = self._crawl_page(page_url)
                if result.get('success') and result.get('text'):
                    sections.setdefault(section, []).append(result['text'])
                time.sleep(0.3)
            except Exception as exc:
                logger.debug("Signal crawl skipped %s: %s", page_url, exc)
                continue

        # Merge text per section (multiple paths may map to same section)
        merged: Dict[str, any] = {
            section: '\n\n'.join(texts)[:6000]  # cap per section
            for section, texts in sections.items()
            if texts
        }
        merged['domain'] = clean_domain
        merged['success'] = bool(merged)
        return merged


# Convenience functions
def crawl_domain(domain: str) -> Dict[str, any]:
    """Convenience function to crawl a domain.

    Args:
        domain: Domain to crawl

    Returns:
        Extracted information dict
    """
    crawler = DomainCrawler()
    return crawler.crawl_domain(domain)


def crawl_for_signals(domain: str) -> Dict[str, any]:
    """Convenience function: crawl signal-rich pages on a company domain.

    Args:
        domain: Company domain, e.g. "acme.com"

    Returns:
        Dict of section → cleaned text, plus 'domain' and 'success' keys.
    """
    crawler = DomainCrawler()
    return crawler.crawl_for_signals(domain)
