"""Optional Apify adapter for LinkedIn lead enrichment."""
import logging
from typing import Optional, List, Dict

import requests

logger = logging.getLogger(__name__)


class ApifyLinkedInService:
    """Use Apify Google Search Scraper actor to find LinkedIn profile URLs."""

    ACTOR_ID = "apify/google-search-scraper"

    def __init__(self, api_token: str):
        self.api_token = (api_token or "").strip()

    def find_linkedin_profile(self, full_name: str, company: str) -> Optional[str]:
        if not self.api_token or not full_name or not company:
            return None

        query = f'site:linkedin.com/in "{full_name}" "{company}"'
        endpoint = (
            f"https://api.apify.com/v2/acts/{self._actor_id_path()}/run-sync-get-dataset-items"
            f"?token={self.api_token}"
        )
        payload = {
            "queries": query,
            "maxPagesPerQuery": 1,
            "resultsPerPage": 5,
            "mobileResults": False,
            "languageCode": "en",
        }

        try:
            response = requests.post(endpoint, json=payload, timeout=40)
            response.raise_for_status()
            items = response.json() or []
            for item in items:
                organic = item.get("organicResults") or []
                for result in organic:
                    link = (result.get("url") or "").strip()
                    if "linkedin.com/in/" in link:
                        return link
        except Exception as exc:
            logger.warning("Apify LinkedIn lookup failed for %s @ %s: %s", full_name, company, exc)
        return None

    def find_people_for_company(
        self,
        company: str,
        domain: str,
        job_title: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 8,
    ) -> List[Dict[str, str]]:
        """Discover likely people at a company using Google search via Apify.

        Returns person-like dicts suitable for lead discovery pipelines.
        Email is intentionally empty here; caller may enrich with other providers
        or candidate generation + validation.
        """
        if not self.api_token or not company:
            return []

        role_hint = (job_title or "founder OR ceo OR vp sales OR head of sales OR revops").strip()
        location_hint = f' "{location}"' if location else ""
        query = (
            f'site:linkedin.com/in ("{company}" OR "{domain}") '
            f'({role_hint}){location_hint}'
        )

        endpoint = (
            f"https://api.apify.com/v2/acts/{self._actor_id_path()}/run-sync-get-dataset-items"
            f"?token={self.api_token}"
        )
        payload = {
            "queries": query,
            "maxPagesPerQuery": 1,
            "resultsPerPage": min(max(limit, 3), 20),
            "mobileResults": False,
            "languageCode": "en",
        }

        people: List[Dict[str, str]] = []
        seen_urls = set()

        try:
            response = requests.post(endpoint, json=payload, timeout=40)
            response.raise_for_status()
            items = response.json() or []

            for item in items:
                organic = item.get("organicResults") or []
                for result in organic:
                    link = (result.get("url") or "").strip()
                    title = (result.get("title") or "").strip()
                    snippet = (result.get("description") or "").strip()

                    if not link or "linkedin.com/in/" not in link or link in seen_urls:
                        continue

                    first_name, last_name = self._extract_name(title)
                    role = self._extract_role(title, snippet)

                    people.append({
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": "",
                        "title": role,
                        "seniority": "",
                        "company": company,
                        "company_domain": domain,
                        "industry": "",
                        "linkedin_url": link,
                        "location": location or "",
                        "source": "apify_linkedin",
                    })
                    seen_urls.add(link)

                    if len(people) >= limit:
                        return people
        except Exception as exc:
            logger.warning("Apify company people lookup failed for %s: %s", company, exc)

        return people

    @staticmethod
    def _extract_name(title: str):
        # Common format: "Jane Doe - VP Sales - Company | LinkedIn"
        head = title.split("|")[0].strip()
        name_part = head.split("-")[0].strip()
        tokens = [t for t in name_part.replace(".", " ").split() if t]
        if not tokens:
            return "", ""
        if len(tokens) == 1:
            return tokens[0], ""
        return tokens[0], tokens[-1]

    def _actor_id_path(self) -> str:
        # Apify API expects actor IDs in path form "owner~actor".
        return self.ACTOR_ID.replace("/", "~")

    @staticmethod
    def _extract_role(title: str, snippet: str) -> str:
        head = title.split("|")[0].strip()
        parts = [p.strip() for p in head.split("-") if p.strip()]
        if len(parts) >= 2:
            return parts[1]
        if snippet:
            return snippet[:120]
        return ""
