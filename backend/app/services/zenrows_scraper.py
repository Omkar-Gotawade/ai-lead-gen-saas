"""ZenRows website scrape adapter with domain-crawler fallback."""
import logging
from typing import Dict

import requests

from .domain_crawler import DomainCrawler

logger = logging.getLogger(__name__)


class ZenRowsScraper:
    """Scrape company website content using ZenRows."""

    API_URL = "https://api.zenrows.com/v1/"

    def __init__(self, api_key: str = ""):
        self.api_key = (api_key or "").strip()
        self._fallback = DomainCrawler()

    def scrape_company(self, domain: str) -> Dict[str, object]:
        url = f"https://{domain}"
        if not self.api_key:
            return self._fallback.crawl_domain(domain)

        try:
            response = requests.get(
                self.API_URL,
                params={
                    "apikey": self.api_key,
                    "url": url,
                    "js_render": "true",
                    "premium_proxy": "true",
                },
                timeout=25,
            )
            response.raise_for_status()
            html = response.text or ""
            text = " ".join(html.split())
            short = text[:5000]

            # Keep interface similar to DomainCrawler output.
            return {
                "success": True,
                "domain": domain,
                "company_name": domain.split(".")[0].replace("-", " ").title(),
                "company_description": short[:300],
                "raw_content": short,
                "emails": [],
                "linkedin_urls": self._extract_linkedin_urls(html),
            }
        except Exception as exc:
            logger.warning("ZenRows scrape failed for %s, fallback to DomainCrawler: %s", domain, exc)
            return self._fallback.crawl_domain(domain)

    @staticmethod
    def _extract_linkedin_urls(html: str):
        linkedin_urls = []
        for token in html.split('"'):
            if "linkedin.com/in/" in token and token.startswith("http"):
                linkedin_urls.append(token.strip())
        # de-duplicate while preserving order
        seen = set()
        unique = []
        for url in linkedin_urls:
            if url not in seen:
                seen.add(url)
                unique.append(url)
        return unique[:10]
