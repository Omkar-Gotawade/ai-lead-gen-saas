"""Apollo.io People Search service.

Apollo.io is a B2B prospecting database with 275M+ contacts.
Their People Search API returns real professionals with:
  - Full name, job title, seniority level
  - Verified or unverified work email
  - Company name, domain, industry, size
  - LinkedIn URL

Free tier :  50 export credits / month
Paid        :  from $49 / month
API docs    :  https://apolloio.github.io/apollo-api-docs/

Usage:
    service = ApolloService(api_key="your_key")
    people = service.search_people("VP Sales SaaS India", location="India")
"""
import requests
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

# Email placeholders Apollo returns when the credit isn't spent to unlock the real address
_PLACEHOLDER_EMAILS = {
    "email_not_unlocked@domain.com",
    "emailnotunlocked@domain.com",
    "email_not_found@domain.com",
}


class ApolloService:
    """People search via Apollo.io REST API."""

    BASE_URL = "https://api.apollo.io/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,   # Apollo requires key in header, not body
            "Cache-Control": "no-cache",
        })

    # ──────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────

    def search_people(
        self,
        keywords: str,
        location: Optional[str] = None,
        industry: Optional[str] = None,
        job_title: Optional[str] = None,
        seniority: Optional[str] = None,
        per_page: int = 25,
        page: int = 1,
    ) -> List[Dict]:
        """Search for people matching the given criteria.

        Args:
            keywords     : Free-text query (job title, skill, company type …)
            location     : City / country string, e.g. "India" or "New York"
            industry     : Industry keyword, e.g. "SaaS"
            job_title    : Specific title filter, e.g. "VP Sales"
            seniority    : One of: senior | manager | director | vp | c_suite | founder
            per_page     : Results per page (max 100)
            page         : Page number (1-indexed)

        Returns:
            List of normalised person dicts (see _normalize_person).
        """
        payload = self._build_payload(keywords, location, industry, job_title, seniority, per_page, page)

        try:
            resp = self._session.post(
                f"{self.BASE_URL}/mixed_people/search",
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            raw_people = data.get("people", [])
            logger.info("Apollo: found %d people for query '%s'", len(raw_people), keywords)
            return [p for p in (self._normalize_person(r) for r in raw_people) if p]
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "?"
            if status == 401:
                logger.error("Apollo API key is invalid (401).")
            elif status == 403:
                logger.warning(
                    "Apollo 403: People Search API requires a PAID plan ($49+/mo). "
                    "Free plan only searches your own saved contacts, not Apollo's database. "
                    "Use PDL_API_KEY instead (free, 1000 calls/mo, Gmail OK): "
                    "https://dashboard.people-datalabs.com/signup"
                )
            elif status == 422:
                logger.error("Apollo: invalid request params — %s", exc.response.text[:200])
            else:
                logger.error("Apollo HTTP error %s: %s", status, str(exc)[:200])
            return []
        except Exception as exc:
            logger.error("Apollo search failed: %s", exc)
            return []

    def search_multiple_pages(
        self,
        keywords: str,
        location: Optional[str] = None,
        industry: Optional[str] = None,
        job_title: Optional[str] = None,
        seniority: Optional[str] = None,
        max_results: int = 50,
    ) -> List[Dict]:
        """Fetch up to max_results people across multiple pages."""
        all_people: List[Dict] = []
        per_page = min(max_results, 100)
        page = 1

        while len(all_people) < max_results:
            batch = self.search_people(
                keywords=keywords,
                location=location,
                industry=industry,
                job_title=job_title,
                seniority=seniority,
                per_page=per_page,
                page=page,
            )
            if not batch:
                break
            all_people.extend(batch)
            if len(batch) < per_page:
                break  # no more pages
            page += 1

        return all_people[:max_results]

    # ──────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────

    def _build_payload(
        self,
        keywords: str,
        location: Optional[str],
        industry: Optional[str],
        job_title: Optional[str],
        seniority: Optional[str],
        per_page: int,
        page: int,
    ) -> Dict:
        q_parts = [keywords]
        if industry and industry.lower() not in keywords.lower():
            q_parts.append(industry)
        if job_title and job_title.lower() not in keywords.lower():
            q_parts.append(job_title)

        payload: Dict = {
            "page": page,
            "per_page": min(per_page, 100),
            "q_keywords": " ".join(q_parts),
            # Only return people where we can get an email
            "contact_email_status": ["verified", "unverified"],
        }

        if location:
            payload["person_locations"] = [location]

        if seniority:
            _SENIORITY_MAP = {
                "senior": ["senior"],
                "manager": ["manager"],
                "director": ["director"],
                "vp": ["vp"],
                "c_suite": ["c_suite"],
                "founder": ["founder"],
                "executive": ["c_suite", "vp", "director"],
            }
            mapped = _SENIORITY_MAP.get(seniority.lower())
            if mapped:
                payload["person_seniorities"] = mapped

        return payload

    def _normalize_person(self, raw: Dict) -> Optional[Dict]:
        """Convert a raw Apollo person object to our standard format.

        Returns None if no usable email is found.
        """
        # Apollo may return the email directly or inside a nested 'contact' object
        email = raw.get("email") or ""
        if not email:
            contact = raw.get("contact") or {}
            email = contact.get("email") or ""
        email = email.strip().lower()

        if not email or email in _PLACEHOLDER_EMAILS or "@" not in email:
            return None

        # Resolve organisation object (can be dict or list of employment history)
        org = raw.get("organization") or {}
        if not isinstance(org, dict):
            org = {}
        if not org:
            history = raw.get("employment_history") or []
            if history and isinstance(history[0], dict):
                org = history[0]

        location_parts = [raw.get("city"), raw.get("state"), raw.get("country")]
        location_str = ", ".join(p for p in location_parts if p)

        return {
            "first_name": (raw.get("first_name") or "").strip(),
            "last_name": (raw.get("last_name") or "").strip(),
            "email": email,
            "title": (raw.get("title") or "").strip(),
            "seniority": (raw.get("seniority") or "").strip(),
            "company": (org.get("name") or "").strip(),
            "company_domain": (org.get("primary_domain") or "").strip(),
            "industry": (org.get("industry") or "").strip(),
            "linkedin_url": (raw.get("linkedin_url") or "").strip(),
            "location": location_str,
            "source": "apollo",
        }
