"""Hunter.io email finder service.

Hunter.io maintains a B2B email database built from public sources on the web.

Domain Search  – finds all known professional emails at a company domain.
Email Finder   – guesses a specific person's email given name + domain.

Free tier  :  25 searches / month
Paid       :  from $34 / month
API docs   :  https://hunter.io/api-documentation

Usage:
    service = HunterService(api_key="your_key")
    people = service.domain_search("stripe.com")
"""
import requests
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

_GENERIC_LOCAL_PARTS = frozenset({
    "info", "contact", "support", "admin", "hello", "team", "sales", "hr",
    "office", "billing", "noreply", "no-reply", "help", "service", "general",
    "enquiries", "enquiry", "mail", "webmaster", "postmaster",
})


class HunterService:
    """Email search via Hunter.io API."""

    BASE_URL = "https://api.hunter.io/v2"

    def __init__(self, api_key: str):
        self.api_key = api_key

    # ──────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────

    def domain_search(
        self,
        domain: str,
        company: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """Find all known professional email addresses at a domain.

        Args:
            domain   : Company domain, e.g. "stripe.com"
            company  : Human-readable company name (for display only)
            limit    : Max results to return

        Returns:
            List of normalised person dicts.
        """
        try:
            resp = requests.get(
                f"{self.BASE_URL}/domain-search",
                params={
                    "domain": domain,
                    "api_key": self.api_key,
                    "limit": min(limit, 100),
                    "type": "personal",  # prefer personal over generic addresses
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json().get("data", {}) or {}
            raw_emails = data.get("emails") or []
            logger.info("Hunter: found %d emails at %s", len(raw_emails), domain)
            return [
                p for p in (self._normalize_email(e, domain, company or domain) for e in raw_emails)
                if p
            ]
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "?"
            logger.error("Hunter HTTP error %s for domain %s", status, domain)
            return []
        except Exception as exc:
            logger.error("Hunter domain search failed for %s: %s", domain, exc)
            return []

    def email_finder(
        self,
        domain: str,
        first_name: str,
        last_name: str,
    ) -> Optional[str]:
        """Guess a specific person's work email.

        Args:
            domain      : Company domain, e.g. "stripe.com"
            first_name  : Person's first name
            last_name   : Person's last name

        Returns:
            Email address string if found and high-confidence, else None.
        """
        try:
            resp = requests.get(
                f"{self.BASE_URL}/email-finder",
                params={
                    "domain": domain,
                    "first_name": first_name,
                    "last_name": last_name,
                    "api_key": self.api_key,
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json().get("data", {}) or {}
            result = data.get("result")
            # Skip low confidence / risky guesses
            if result in ("risky", "webmail"):
                return None
            return data.get("email") or None
        except Exception as exc:
            logger.error("Hunter email finder failed: %s", exc)
            return None

    # ──────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────

    def _normalize_email(self, raw: Dict, domain: str, company: str) -> Optional[Dict]:
        email = (raw.get("value") or "").strip().lower()
        if not email or "@" not in email:
            return None

        local = email.split("@")[0]
        if local in _GENERIC_LOCAL_PARTS:
            return None

        confidence = raw.get("confidence") or 0
        if confidence < 30:
            return None

        return {
            "first_name": (raw.get("first_name") or "").strip(),
            "last_name": (raw.get("last_name") or "").strip(),
            "email": email,
            "title": (raw.get("position") or "").strip(),
            "seniority": (raw.get("seniority") or "").strip(),
            "company": company,
            "company_domain": domain,
            "industry": "",
            "linkedin_url": (raw.get("linkedin") or "").strip(),
            "location": "",
            "source": "hunter",
        }
