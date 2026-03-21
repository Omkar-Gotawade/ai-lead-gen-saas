"""Snov.io people search service.

Uses OAuth2 client-credentials flow:
  1. POST /v1/oauth/access_token  → bearer token
  2. POST /v1/get-domain-emails-with-info  → people at a domain

Free tier: 50 credits/month, accepts Gmail sign-up.
Sign up at https://app.snov.io  → Settings → API Keys
"""
import requests
import logging
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

_TOKEN_URL = "https://api.snov.io/v1/oauth/access_token"
_DOMAIN_SEARCH_URL = "https://api.snov.io/v1/get-domain-emails-with-info"

# Generic mailboxes to skip
_GENERIC_PREFIXES = {
    "info", "support", "hello", "contact", "admin", "sales",
    "help", "office", "team", "noreply", "no-reply", "webmaster",
    "mail", "billing", "legal", "hr", "careers",
}


class SnovService:
    """Wrapper around Snov.io API."""

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: Optional[str] = None

    # ------------------------------------------------------------------ auth
    def _get_token(self) -> str:
        """Fetch (or reuse) an OAuth2 access token."""
        if self._token:
            return self._token
        resp = requests.post(
            _TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=15,
        )
        resp.raise_for_status()
        self._token = resp.json().get("access_token", "")
        logger.debug("Snov.io token acquired")
        return self._token

    # --------------------------------------------------------------- search
    def domain_search(
        self,
        domain: str,
        company: str = "",
        limit: int = 10,
    ) -> List[Dict]:
        """Return a list of people found at *domain*.

        Each dict has the same keys used by HunterService so the worker
        pipeline is plug-and-play compatible:
          first_name, last_name, email, title, seniority,
          company, company_domain, linkedin_url, source
        """
        try:
            token = self._get_token()
        except Exception as exc:
            logger.error("Snov.io auth failed: %s", exc)
            return []

        try:
            resp = requests.post(
                _DOMAIN_SEARCH_URL,
                json={
                    "access_token": token,
                    "domain": domain,
                    "type": "personal",   # personal emails only
                    "limit": min(limit, 50),
                    "lastId": 0,
                },
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.warning("Snov.io domain search failed for %s: %s", domain, exc)
            return []

        emails_raw = data.get("emails") or []
        people = []
        for entry in emails_raw:
            email = (entry.get("email") or "").lower().strip()
            if not email:
                continue
            prefix = email.split("@")[0].split("+")[0]
            if prefix in _GENERIC_PREFIXES:
                continue

            seniority_raw = (entry.get("seniority") or "").lower()
            seniority = _normalise_seniority(seniority_raw)

            people.append({
                "first_name":     entry.get("firstName") or "",
                "last_name":      entry.get("lastName") or "",
                "email":          email,
                "title":          entry.get("position") or "",
                "seniority":      seniority,
                "company":        company or domain,
                "company_domain": domain,
                "linkedin_url":   entry.get("linkedIn") or "",
                "location":       "",
                "industry":       "",
                "source":         "snov",
            })

        logger.info("Snov.io: %d people found at %s", len(people), domain)
        return people


# ------------------------------------------------------------------ helpers
def _normalise_seniority(raw: str) -> str:
    """Map Snov.io seniority strings to our badge values."""
    mapping = {
        "c-level": "c_suite",
        "c_level": "c_suite",
        "c level": "c_suite",
        "ceo": "c_suite",
        "cto": "c_suite",
        "cmo": "c_suite",
        "coo": "c_suite",
        "founder": "founder",
        "owner": "founder",
        "vp": "vp",
        "vice president": "vp",
        "director": "director",
        "manager": "manager",
        "senior": "senior",
    }
    for key, val in mapping.items():
        if key in raw:
            return val
    return raw
