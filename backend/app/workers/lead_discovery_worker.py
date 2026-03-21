"""Celery worker for Lead Discovery.

Pipeline priority:
  1. Apollo.io People Search   - if APOLLO_API_KEY is set (falls through if 403/0 results)
  2. Snov.io Domain Search     - if SNOV_CLIENT_ID + SNOV_CLIENT_SECRET are set
  3. SERP + website crawl      - legacy fallback (finds emails on company home pages)

Person data is stored as a JSON blob in DiscoveredDomain.company_description so the
frontend can render rich person cards without a DB migration.
"""
from celery import shared_task
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import json
import logging

from ..database import SessionLocal
from ..models.lead_discovery_job import LeadDiscoveryJob
from ..models.discovered_domain import DiscoveredDomain
from ..models.lead import Lead
from ..services.apollo_service import ApolloService
from ..services.icypeas_service import IcypeasService
from ..services.pdl_service import PDLService
from ..services.snov_service import SnovService
from ..services.serp_scraper import SerpScraper
from ..services.domain_crawler import DomainCrawler
from ..services.company_enrichment import CompanyEnrichmentService
from ..config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _person_to_lead(db, person, job):
    """Persist a person dict as a Lead. Returns True if a new lead was created."""
    email = (person.get("email") or "").strip().lower()
    if not email:
        return False
    if db.query(Lead).filter(Lead.email == email).first():
        logger.debug("Lead already exists for %s", email)
        return False
    first = person.get("first_name") or email.split("@")[0].split(".")[0].capitalize()
    last = person.get("last_name") or ""
    db.add(Lead(
        id=uuid.uuid4(),
        org_id=job.org_id,
        first_name=first,
        last_name=last,
        full_name=(first + " " + last).strip(),
        email=email,
        title=person.get("title") or None,
        company=person.get("company") or None,
        industry=person.get("industry") or job.industry or None,
        linkedin_url=person.get("linkedin_url") or None,
        source="lead_discovery",
        enriched_data={
            "seniority": person.get("seniority"),
            "company_domain": person.get("company_domain"),
            "discovery_source": person.get("source"),
            "location": person.get("location"),
        },
    ))
    return True


def _store_person_as_domain_row(db, person, job_id):
    """Store a discovered person in the DiscoveredDomain table for UI preview.

    Repurposes existing columns (no DB migration needed):
      domain              = company_domain
      company_name        = "FirstName LastName"
      source_url          = linkedin_url
      company_description = JSON with full person metadata
      emails_found        = email
    """
    meta = {
        "first_name": person.get("first_name", ""),
        "last_name":  person.get("last_name", ""),
        "title":      person.get("title", ""),
        "seniority":  person.get("seniority", ""),
        "location":   person.get("location", ""),
        "industry":   person.get("industry", ""),
        "source":     person.get("source", ""),
        "company":    person.get("company", ""),
    }
    fn = person.get("first_name", "")
    ln = person.get("last_name", "")
    name = (fn + " " + ln).strip()
    db.add(DiscoveredDomain(
        id=uuid.uuid4(),
        discovery_job_id=job_id,
        domain=person.get("company_domain") or person.get("company") or "unknown",
        source_url=person.get("linkedin_url") or None,
        status="crawled",
        company_name=name or person.get("company", ""),
        company_description=json.dumps(meta),
        emails_found=person.get("email", ""),
        crawled_at=datetime.utcnow(),
    ))


# ---------------------------------------------------------------------------
# Main Celery task
# ---------------------------------------------------------------------------

@shared_task(bind=True, max_retries=3)
def run_lead_discovery(self, job_id: str, max_results: int = 25):
    """Execute the full lead discovery pipeline for a job."""
    db = SessionLocal()
    try:
        job = db.query(LeadDiscoveryJob).filter(
            LeadDiscoveryJob.id == uuid.UUID(job_id)
        ).first()
        if not job:
            logger.error("Job %s not found", job_id)
            return {"error": "Job not found"}

        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()
        logger.info("Starting job %s  keywords=%r", job_id, job.keywords)

        pdl_key = (getattr(settings, "PDL_API_KEY", "") or "").strip()
        icypeas_key = (getattr(settings, "ICYPEAS_API_KEY", "") or "").strip()
        apollo_key = (getattr(settings, "APOLLO_API_KEY", "") or "").strip()
        snov_id = (getattr(settings, "SNOV_CLIENT_ID", "") or "").strip()
        snov_secret = (getattr(settings, "SNOV_CLIENT_SECRET", "") or "").strip()

        people = None
        pipeline = "serp_crawl"

        # --- Pipeline 1: People Data Labs ---
        if pdl_key:
            result = _pdl_pipeline(job, pdl_key, max_results)
            if result:
                people, pipeline = result, "pdl"
            else:
                logger.warning("PDL returned 0 results -- falling through")

        # --- Pipeline 2: Icypeas (Gmail OK, 5k free/mo) ---
        if people is None and icypeas_key:
            result = _icypeas_pipeline(job, icypeas_key, max_results)
            if result:
                people, pipeline = result, "icypeas"
            else:
                logger.warning("Icypeas returned 0 results -- falling through")

        # --- Pipeline 3: Apollo.io (paid API plan) ---
        if people is None and apollo_key:
            result = _apollo_pipeline(job, apollo_key, max_results)
            if result:
                people, pipeline = result, "apollo"
            else:
                logger.warning("Apollo returned 0 results -- falling through to next pipeline")

        # --- Pipeline 4: Snov.io ---
        if people is None and snov_id and snov_secret:
            result = _snov_pipeline(job, snov_id, snov_secret, max_results)
            if result:
                people, pipeline = result, "snov"

        # --- Pipeline 3: SERP + crawl fallback ---
        if people is None:
            _serp_crawl_pipeline(job, max_results, db)
            db.refresh(job)
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            db.commit()
            logger.info("Job %s done via serp_crawl -- leads=%d", job_id, job.leads_created)
            return {"job_id": job_id, "pipeline": "serp_crawl",
                    "leads_created": job.leads_created, "status": "completed"}

        # --- People-based pipeline: store previews + create leads ---
        logger.info("Pipeline %r returned %d people", pipeline, len(people))
        job.domains_found = len(people)
        db.commit()

        leads_created = 0
        for person in people:
            _store_person_as_domain_row(db, person, job.id)
            if _person_to_lead(db, person, job):
                leads_created += 1
        db.commit()

        job.domains_crawled = len(people)
        job.leads_created = leads_created
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        db.commit()

        logger.info("Job %s done via %s -- people=%d leads=%d", job_id, pipeline, len(people), leads_created)
        return {"job_id": job_id, "pipeline": pipeline,
                "people_found": len(people), "leads_created": leads_created, "status": "completed"}

    except Exception as exc:
        logger.error("Job %s failed: %s", job_id, exc)
        try:
            j = db.query(LeadDiscoveryJob).filter(LeadDiscoveryJob.id == uuid.UUID(job_id)).first()
            if j:
                j.status = "failed"
                j.error_message = str(exc)[:900]
                j.completed_at = datetime.utcnow()
                db.commit()
        except Exception as inner:
            logger.error("Could not update job status: %s", inner)
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60)
        return {"error": str(exc)}
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Pipeline implementations
# ---------------------------------------------------------------------------

def _icypeas_pipeline(job, api_key, max_results):
    scraper = SerpScraper(serp_api_key=(getattr(settings, "SERP_API_KEY", "") or None))
    domains = scraper.search_companies(
        keywords=job.keywords,
        location=job.location,
        industry=job.industry,
        max_results=min(max_results, 20),
    )
    icypeas = IcypeasService(api_key=api_key)
    people = []
    per_domain = max(3, max_results // max(len(domains), 1))
    for d in domains:
        if len(people) >= max_results:
            break
        domain = d.get("domain", "")
        if domain:
            people.extend(icypeas.domain_search(
                domain=domain,
                company=d.get("company_name", ""),
                limit=per_domain,
            ))
    return people[:max_results]


def _pdl_pipeline(job, api_key, max_results):
    svc = PDLService(api_key=api_key)
    return svc.search_multiple_pages(
        keywords=job.keywords,
        location=job.location or None,
        industry=job.industry or None,
        job_title=getattr(job, "job_title", None),
        seniority=getattr(job, "seniority", None),
        max_results=max_results,
    )


def _apollo_pipeline(job, api_key, max_results):
    svc = ApolloService(api_key=api_key)
    return svc.search_multiple_pages(
        keywords=job.keywords,
        location=job.location or None,
        industry=job.industry or None,
        job_title=getattr(job, "job_title", None),
        seniority=getattr(job, "seniority", None),
        max_results=max_results,
    )


def _snov_pipeline(job, client_id, client_secret, max_results):
    scraper = SerpScraper(serp_api_key=(getattr(settings, "SERP_API_KEY", "") or None))
    domains = scraper.search_companies(
        keywords=job.keywords,
        location=job.location,
        industry=job.industry,
        max_results=min(max_results, 20),
    )
    snov = SnovService(client_id=client_id, client_secret=client_secret)
    people = []
    per_domain = max(3, max_results // max(len(domains), 1))
    for d in domains:
        if len(people) >= max_results:
            break
        domain = d.get("domain", "")
        if domain:
            people.extend(snov.domain_search(domain=domain, limit=per_domain))
    return people[:max_results]


def _serp_crawl_pipeline(job, max_results, db):
    """Legacy pipeline. Mutates job stats directly and commits to db."""
    serp_api_key = (getattr(settings, "SERP_API_KEY", "") or None)
    scraper = SerpScraper(serp_api_key=serp_api_key)
    domains = scraper.search_companies(
        keywords=job.keywords, location=job.location,
        industry=job.industry, max_results=max_results,
    )
    if not domains:
        job.error_message = "No companies found for these search terms."
        db.commit()
        return

    for d in domains:
        db.add(DiscoveredDomain(
            id=uuid.uuid4(), discovery_job_id=job.id,
            domain=d["domain"], source_url=d.get("source_url"), status="pending",
        ))
    job.domains_found = len(domains)
    db.commit()

    crawler = DomainCrawler()
    enrichment_service = None
    gemini_key = (getattr(settings, "GEMINI_API_KEY", "") or "").strip()
    if gemini_key:
        try:
            enrichment_service = CompanyEnrichmentService(
                api_key=gemini_key,
                model=getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash"),
            )
        except Exception as e:
            logger.warning("Could not init enrichment service: %s", e)

    leads_created = 0
    crawled = 0
    for dd in db.query(DiscoveredDomain).filter(
        DiscoveredDomain.discovery_job_id == job.id,
        DiscoveredDomain.status == "pending",
    ).all():
        try:
            result = crawler.crawl_domain(dd.domain)
            if result["success"]:
                dd.status = "crawled"
                dd.company_name = result.get("company_name")
                dd.company_description = result.get("company_description")
                dd.emails_found = ",".join(result.get("emails", []))
                dd.raw_content = result.get("raw_content", "")[:5000]
                dd.crawled_at = datetime.utcnow()
                crawled += 1

                enriched = {}
                if enrichment_service and dd.raw_content:
                    try:
                        enriched = enrichment_service.enrich_company(
                            company_name=dd.company_name,
                            company_description=dd.company_description,
                            raw_content=dd.raw_content, domain=dd.domain,
                        )
                    except Exception as e:
                        logger.warning("Enrichment failed for %s: %s", dd.domain, e)

                for email in result.get("emails", [])[:5]:
                    if db.query(Lead).filter(Lead.email == email).first():
                        continue
                    local = email.split("@")[0]
                    parts = local.replace(".", " ").replace("_", " ").split()
                    first = parts[0].capitalize() if parts else "Unknown"
                    last = parts[-1].capitalize() if len(parts) > 1 else ""
                    db.add(Lead(
                        id=uuid.uuid4(), org_id=job.org_id,
                        first_name=first, last_name=last,
                        full_name=(first + " " + last).strip(), email=email,
                        company=dd.company_name or dd.domain,
                        industry=enriched.get("industry") if enriched else job.industry,
                        source="lead_discovery", enriched_data=enriched or None,
                    ))
                    leads_created += 1
            else:
                dd.status = "failed"
                dd.error_message = result.get("error", "Crawl failed")
            db.commit()
            job.domains_crawled = crawled
            job.leads_created = leads_created
            db.commit()
        except Exception as e:
            logger.error("Domain %s failed: %s", dd.domain, e)
            dd.status = "failed"
            dd.error_message = str(e)
            db.commit()
