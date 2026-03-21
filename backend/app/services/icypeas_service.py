"""Icypeas email search service.

Free tier: 5,000 searches/month — accepts Gmail sign-up.
Sign up: https://app.icypeas.com  (Settings → API)

Flow:
  1. SERP finds company domains for the keywords
  2. Icypeas domain-search finds people at each domain
     POST https://app.icypeas.com/api/domain-search
"""
import requests
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

_BASE = "https://app.icypeas.com/api"

_GENERIC = {
    "info", "support", "hello", "contact", "admin", "sales",
    "help", "office", "team", "noreply", "no-reply", "webmaster",
    "mail", "billing", "legal", "hr", "careers", "press", "media",
}


class IcypeasService:
    """Find people at company domains via Icypeas."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

    # --------------------------------------------------------- domain search
    def domain_search(
        self,
        domain: str,
        company: str = "",
        limit: int = 10,
    ) -> List[Dict]:
        """Return people found at *domain*.

        Icypeas endpoint: POST /api/domain-search
        Body: { "domainOrCompany": "<domain>" }
        """
        try:
            resp = self._session.post(
                f"{_BASE}/domain-search",
                json={"domainOrCompany": domain},
                timeout=20,
            )
            if resp.status_code == 401:
                logger.error("Icypeas: invalid API key.")
                return []
            if resp.status_code == 402:
                logger.warning("Icypeas: free quota exhausted for this month.")
                return []
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.warning("Icypeas domain search failed for %s: %s", domain, exc)
            return []

        # Response shape: { "item": { "emails": [...] } }  or { "items": [...] }
        raw_emails = []
        item = data.get("item") or {}
        if isinstance(item, dict):
            raw_emails = item.get("emails") or item.get("results") or []
        if not raw_emails:
            raw_emails = data.get("items") or data.get("emails") or []

        people = []
        for entry in raw_emails[:limit]:
            if isinstance(entry, str):
                email = entry.lower().strip()
                first, last = _split_email_name(email)
                people.append(_make_person(first, last, email, "", domain, company, ""))
                continue

            email = (entry.get("email") or "").lower().strip()
            if not email or "@" not in email:
                continue
            prefix = email.split("@")[0].split("+")[0].lower()
            if prefix in _GENERIC:
                continue

            first = (entry.get("firstname") or entry.get("first_name") or "").strip()
            last = (entry.get("lastname") or entry.get("last_name") or "").strip()
            if not first and not last:
                first, last = _split_email_name(email)

            title = (entry.get("position") or entry.get("title") or "").strip()
            linkedin = (entry.get("linkedin") or entry.get("linkedinUrl") or "").strip()
            seniority = _infer_seniority(title)

            people.append(_make_person(first, last, email, title, domain, company, linkedin, seniority))

        logger.info("Icypeas: %d people at %s", len(people), domain)
        return people


# ------------------------------------------------------------ helpers
def _split_email_name(email: str):
    local = email.split("@")[0]
    parts = local.replace(".", " ").replace("_", " ").replace("-", " ").split()
    first = parts[0].capitalize() if parts else ""
    last = parts[-1].capitalize() if len(parts) > 1 else ""
    return first, last


def _infer_seniority(title: str) -> str:
    t = title.lower()
    if any(x in t for x in ["ceo", "cto", "cmo", "coo", "cfo", "chief"]):
        return "c_suite"
    if any(x in t for x in ["founder", "co-founder", "owner"]):
        return "founder"
    if "vp" in t or "vice president" in t:
        return "vp"
    if "director" in t:
        return "director"
    if "manager" in t:
        return "manager"
    if "senior" in t or "sr." in t:
        return "senior"
    return ""


def _make_person(first, last, email, title, domain, company, linkedin, seniority=""):
    return {
        "first_name":     first,
        "last_name":      last,
        "email":          email,
        "title":          title,
        "seniority":      seniority,
        "company":        company or domain,
        "company_domain": domain,
        "linkedin_url":   linkedin,
        "location":       "",
        "industry":       "",
        "source":         "icypeas",
    }
