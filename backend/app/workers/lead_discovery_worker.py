"""Celery worker for Lead Discovery automation.

This worker handles the complete lead discovery pipeline:
1. Search for companies via SERP
2. Crawl discovered domains
3. Extract contact information
4. Enrich with AI
5. Create Lead records
"""
from celery import shared_task
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import logging

from ..database import SessionLocal
from ..models.lead_discovery_job import LeadDiscoveryJob
from ..models.discovered_domain import DiscoveredDomain
from ..models.lead import Lead
from ..services.serp_scraper import SerpScraper
from ..services.domain_crawler import DomainCrawler
from ..services.company_enrichment import CompanyEnrichmentService
from ..config import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def run_lead_discovery(self, job_id: str, max_results: int = 20):
    """
    Execute the complete lead discovery pipeline for a job.
    
    This is a long-running task that:
    - Searches for companies
    - Crawls their websites
    - Extracts emails and information
    - Enriches data with AI
    - Creates Lead records
    
    Args:
        job_id: UUID of the LeadDiscoveryJob
        max_results: Maximum number of domains to discover
        
    Returns:
        dict: Summary of results
    """
    db: Session = SessionLocal()
    
    try:
        # Get job
        job = db.query(LeadDiscoveryJob).filter(
            LeadDiscoveryJob.id == uuid.UUID(job_id)
        ).first()
        
        if not job:
            logger.error(f"Job {job_id} not found")
            return {"error": "Job not found"}
        
        # Update job status
        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Starting lead discovery job {job_id}")
        
        # Step 1: SERP Scraping
        logger.info(f"Step 1: Searching for companies - {job.keywords}")
        serp_api_key = getattr(settings, 'SERP_API_KEY', None)
        scraper = SerpScraper(serp_api_key=serp_api_key)
        
        domains = scraper.search_companies(
            keywords=job.keywords,
            location=job.location,
            industry=job.industry,
            max_results=max_results
        )
        
        if not domains:
            logger.warning(f"No domains found for job {job_id}")
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.error_message = "No companies found matching search criteria"
            db.commit()
            return {"domains_found": 0}
        
        # Save discovered domains
        for domain_data in domains:
            discovered_domain = DiscoveredDomain(
                id=uuid.uuid4(),
                discovery_job_id=job.id,
                domain=domain_data['domain'],
                source_url=domain_data.get('source_url'),
                status='pending'
            )
            db.add(discovered_domain)
        
        job.domains_found = len(domains)
        db.commit()
        
        logger.info(f"Found {len(domains)} domains for job {job_id}")
        
        # Step 2: Crawl each domain
        logger.info(f"Step 2: Crawling domains")
        crawler = DomainCrawler()
        
        # Get enrichment service if available
        gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
        gemini_model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash-exp')
        enrichment_service = None
        if gemini_key:
            try:
                enrichment_service = CompanyEnrichmentService(
                    api_key=gemini_key,
                    model=gemini_model
                )
            except Exception as e:
                logger.warning(f"Could not initialize enrichment service: {e}")
        
        leads_created = 0
        domains_crawled = 0
        
        # Get discovered domains from DB
        discovered_domains = db.query(DiscoveredDomain).filter(
            DiscoveredDomain.discovery_job_id == job.id,
            DiscoveredDomain.status == 'pending'
        ).all()
        
        for discovered_domain in discovered_domains:
            try:
                # Crawl domain
                crawl_result = crawler.crawl_domain(discovered_domain.domain)
                
                if crawl_result['success']:
                    discovered_domain.status = 'crawled'
                    discovered_domain.company_name = crawl_result.get('company_name')
                    discovered_domain.company_description = crawl_result.get('company_description')
                    discovered_domain.emails_found = ','.join(crawl_result.get('emails', []))
                    discovered_domain.raw_content = crawl_result.get('raw_content', '')[:5000]  # Limit size
                    discovered_domain.crawled_at = datetime.utcnow()
                    
                    domains_crawled += 1
                    
                    # Step 3: AI Enrichment (if available)
                    enriched_data = {}
                    if enrichment_service and discovered_domain.raw_content:
                        try:
                            enriched_data = enrichment_service.enrich_company(
                                company_name=discovered_domain.company_name,
                                company_description=discovered_domain.company_description,
                                raw_content=discovered_domain.raw_content,
                                domain=discovered_domain.domain
                            )
                            logger.info(f"Enriched {discovered_domain.domain}")
                        except Exception as e:
                            logger.warning(f"Enrichment failed for {discovered_domain.domain}: {e}")
                    
                    # Step 4: Create Lead records
                    emails = crawl_result.get('emails', [])
                    if emails:
                        for email in emails[:5]:  # Limit to 5 emails per domain
                            try:
                                # Check if lead already exists
                                existing_lead = db.query(Lead).filter(
                                    Lead.email == email
                                ).first()
                                
                                if existing_lead:
                                    logger.debug(f"Lead already exists for {email}")
                                    continue
                                
                                # Parse name from email (basic)
                                email_local = email.split('@')[0]
                                name_parts = email_local.replace('.', ' ').replace('_', ' ').split()
                                first_name = name_parts[0].capitalize() if len(name_parts) > 0 else "Unknown"
                                last_name = name_parts[-1].capitalize() if len(name_parts) > 1 else ""
                                full_name = f"{first_name} {last_name}".strip()
                                
                                # Create lead
                                lead = Lead(
                                    id=uuid.uuid4(),
                                    org_id=job.org_id,
                                    first_name=first_name,
                                    last_name=last_name,
                                    full_name=full_name,
                                    email=email,
                                    company=discovered_domain.company_name or discovered_domain.domain,
                                    industry=enriched_data.get('industry') if enriched_data else job.industry,
                                    source='lead_discovery',
                                    enriched_data=enriched_data if enriched_data else None
                                )
                                
                                db.add(lead)
                                leads_created += 1
                                
                            except Exception as e:
                                logger.error(f"Failed to create lead for {email}: {e}")
                                continue
                    
                else:
                    discovered_domain.status = 'failed'
                    discovered_domain.error_message = crawl_result.get('error', 'Crawl failed')
                
                db.commit()
                
                # Update job progress
                job.domains_crawled = domains_crawled
                job.leads_created = leads_created
                db.commit()
                
            except Exception as e:
                logger.error(f"Failed to process domain {discovered_domain.domain}: {e}")
                discovered_domain.status = 'failed'
                discovered_domain.error_message = str(e)
                db.commit()
                continue
        
        # Mark job as completed
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.domains_crawled = domains_crawled
        job.leads_created = leads_created
        db.commit()
        
        logger.info(
            f"Lead discovery job {job_id} completed: "
            f"{domains_crawled} domains crawled, {leads_created} leads created"
        )
        
        return {
            "job_id": job_id,
            "domains_found": job.domains_found,
            "domains_crawled": domains_crawled,
            "leads_created": leads_created,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Lead discovery job {job_id} failed: {str(e)}")
        
        # Mark job as failed
        try:
            job = db.query(LeadDiscoveryJob).filter(
                LeadDiscoveryJob.id == uuid.UUID(job_id)
            ).first()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                db.commit()
        except Exception as update_error:
            logger.error(f"Failed to update job status: {update_error}")
        
        # Retry if possible
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)
        
        return {"error": str(e)}
        
    finally:
        db.close()
