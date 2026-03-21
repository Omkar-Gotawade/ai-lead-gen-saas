"""People Data Labs (PDL) people search service.

Free tier: 1,000 API calls/month — accepts Gmail sign-up.
Sign up: https://dashboard.people-datalabs.com/signup

API docs: https://docs.people-datalabs.com/docs/person-search-api
Endpoint: POST https://api.peopledatalabs.com/v5/person/search
"""
import requests
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.peopledatalabs.com/v5"

_SENIORITY_MAP = {
    "c_suite":  ["ceo", "cto", "cmo", "coo", "cfo", "chief"],
    "vp":       ["vp", "vice president"],
    "director": ["director"],
    "manager":  ["manager"],
    "senior":   ["senior", "sr."],
    "founder":  ["founder", "owner", "co-founder"],
}


class PDLService:
    """People search via People Data Labs REST API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._session = requests.Session()
        self._session.headers.update({
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
        })

    # ---------------------------------------------------------------- search
    def search_people(
        self,
        keywords: str,
        location: Optional[str] = None,
        industry: Optional[str] = None,
        job_title: Optional[str] = None,
        seniority: Optional[str] = None,
        size: int = 25,
        from_: int = 0,
    ) -> List[Dict]:
        """Search people using PDL's Elasticsearch-style query."""
        must_clauses = []

        # Keywords → job title match
        if keywords:
            must_clauses.append({
                "bool": {
                    "should": [
                        {"match": {"job_title": keywords}},
                        {"match": {"skills": keywords}},
                    ]
                }
            })

        if job_title:
            must_clauses.append({"match": {"job_title": job_title}})

        if location:
            must_clauses.append({
                "bool": {
                    "should": [
                        {"term": {"location_country": location.lower()}},
                        {"match": {"location_name": location}},
                    ]
                }
            })

        if industry:
            must_clauses.append({"match": {"industry": industry}})

        if seniority and seniority in _SENIORITY_MAP:
            title_terms = _SENIORITY_MAP[seniority]
            must_clauses.append({
                "bool": {
                    "should": [
                        {"match": {"job_title": t}} for t in title_terms
                    ]
                }
            })

        query = {"bool": {"must": must_clauses}} if must_clauses else {"match_all": {}}

        payload = {
            "query": query,
            "size": min(size, 100),
            "from": from_,
            # Only return records with a work email
            "required": "work_email",
        }

        try:
            resp = self._session.post(
                f"{_BASE_URL}/person/search",
                json=payload,
                timeout=30,
            )
            if resp.status_code == 402:
                logger.warning("PDL: free tier quota exhausted for this month.")
                return []
            if resp.status_code == 401:
                logger.error("PDL: invalid API key.")
                return []
            resp.raise_for_status()
            data = resp.json()
            raw = data.get("data", [])
            logger.info("PDL: %d people returned (total=%s)", len(raw), data.get("total", "?"))
            return [p for p in (self._normalize(r) for r in raw) if p]
        except requests.HTTPError as exc:
            logger.error("PDL HTTP error %s: %s",
                         exc.response.status_code if exc.response else "?", str(exc)[:200])
            return []
        except Exception as exc:
            logger.error("PDL search failed: %s", exc)
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
        """Paginate through PDL results up to max_results."""
        all_people: List[Dict] = []
        page_size = min(max_results, 100)
        from_ = 0

        while len(all_people) < max_results:
            batch = self.search_people(
                keywords=keywords,
                location=location,
                industry=industry,
                job_title=job_title,
                seniority=seniority,
                size=page_size,
                from_=from_,
            )
            if not batch:
                break
            all_people.extend(batch)
            if len(batch) < page_size:
                break
            from_ += page_size

        return all_people[:max_results]

    # --------------------------------------------------------------- helpers
    def _normalize(self, raw: Dict) -> Optional[Dict]:
        email = (raw.get("work_email") or raw.get("personal_emails", [None])[0] or "").lower().strip()
        if not email or "@" not in email:
            return None

        exp = (raw.get("experience") or [{}])[0] if raw.get("experience") else {}
        company = exp.get("company", {}).get("name", "") or raw.get("job_company_name", "")
        domain = exp.get("company", {}).get("website", "") or raw.get("job_company_website", "")
        industry = (raw.get("industry") or exp.get("company", {}).get("industry", "")).strip()

        loc_parts = [raw.get("location_locality"), raw.get("location_region"), raw.get("location_country")]
        location_str = ", ".join(p for p in loc_parts if p)

        return {
            "first_name":     (raw.get("first_name") or "").strip(),
            "last_name":      (raw.get("last_name") or "").strip(),
            "email":          email,
            "title":          (raw.get("job_title") or "").strip(),
            "seniority":      _map_seniority(raw.get("job_title_levels") or []),
            "company":        company.strip(),
            "company_domain": domain.strip(),
            "industry":       industry,
            "linkedin_url":   (raw.get("linkedin_url") or "").strip(),
            "location":       location_str,
            "source":         "pdl",
        }


def _map_seniority(levels: List[str]) -> str:
    mapping = {
        "owner": "founder", "founder": "founder",
        "c_suite": "c_suite", "vp": "vp",
        "director": "director", "manager": "manager", "senior": "senior",
    }
    for lv in levels:
        lv_lower = lv.lower().replace(" ", "_")
        if lv_lower in mapping:
            return mapping[lv_lower]
    return levels[0].lower() if levels else ""
