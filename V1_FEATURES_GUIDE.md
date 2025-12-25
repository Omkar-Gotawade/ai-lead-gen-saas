# v1 Pre-Launch Features Guide

## Overview

This document covers the three major features added in v1:

1. **Lead Discovery & Scraping Automation** - Automatically discover and create leads
2. **LinkedIn Profile Enrichment** - Enrich leads with LinkedIn data
3. **Enhanced Deliverability Tools** - DNS checking and email warm-up

---

## 🔍 Feature 1: Lead Discovery & Scraping Automation

### What It Does

Allows users to automatically discover company leads by searching the web, crawling company websites, and extracting contact information - without manually uploading CSVs.

### How It Works

1. User provides search parameters (keywords, location, industry)
2. System searches Google for matching companies
3. Crawls discovered company websites (homepage, about, contact pages)
4. Extracts company information and email addresses
5. Uses AI (OpenAI) to enrich company data
6. Creates Lead records automatically

### API Endpoints

#### Start Discovery Job
```http
POST /api/lead-discovery/start
Content-Type: application/json

{
  "keywords": "AI software",
  "location": "India",
  "industry": "SaaS",
  "max_results": 20
}
```

**Response:**
```json
{
  "id": "uuid",
  "status": "pending",
  "keywords": "AI software",
  "created_at": "2025-12-16T..."
}
```

#### Get Job Status
```http
GET /api/lead-discovery/{job_id}
```

**Response:**
```json
{
  "job": {
    "id": "uuid",
    "status": "running",
    "domains_found": 20,
    "domains_crawled": 15,
    "leads_created": 12
  },
  "discovered_domains": [...],
  "progress_percent": 75
}
```

#### List Recent Jobs
```http
GET /api/lead-discovery/
```

### Frontend Usage

Navigate to `/discover-leads` in the application.

1. Fill in search criteria:
   - Keywords (required): e.g., "AI software", "marketing agency"
   - Location (optional): e.g., "India", "USA"
   - Industry (optional): e.g., "SaaS", "E-commerce"
   - Max Results: 1-100 domains

2. Click "Discover Leads"

3. Monitor progress in real-time:
   - Job status
   - Domains found and crawled
   - Leads created
   - Progress percentage

4. View discovered domains in preview table

5. Click "View Leads" when completed

### Backend Architecture

**Models:**
- `LeadDiscoveryJob` - Tracks discovery jobs
- `DiscoveredDomain` - Stores discovered domains and crawl data

**Services:**
- `serp_scraper.py` - Google search scraping
- `domain_crawler.py` - Website crawling and data extraction
- `company_enrichment.py` - AI-powered company analysis

**Workers:**
- `lead_discovery_worker.py` - Celery task orchestrating the pipeline

### Configuration

Add to `.env`:

```env
# Optional: For better search results (otherwise uses basic scraping)
SERP_API_KEY=your_serpapi_key_here

# Note: AI company enrichment uses your existing GEMINI_API_KEY
# No additional API key needed!
```

### Limitations (v1)

- No proxy rotation (keep requests reasonable)
- Basic Google scraping (may be fragile, consider SerpAPI)
- No advanced filtering
- Limited to ~100 domains per job

---

## 🔗 Feature 2: LinkedIn Profile Enrichment

### What It Does

Enriches lead profiles with professional data from LinkedIn URLs using legitimate 3rd-party enrichment APIs.

**Important:** This does NOT scrape LinkedIn directly (which violates ToS). It uses official enrichment APIs.

### How It Works

1. User provides LinkedIn profile URL
2. System calls 3rd-party enrichment API (Clearbit, Apollo.io, or Snov.io)
3. Fetches professional information:
   - Job title
   - Seniority level
   - Company size
   - LinkedIn headline
4. Updates Lead record

### API Endpoint

```http
POST /api/leads/{lead_id}/linkedin-enrich?linkedin_url=https://linkedin.com/in/username
```

**Response:**
```json
{
  "id": "uuid",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "job_title": "Senior Marketing Manager",
  "seniority": "Senior",
  "company_size": "51-200",
  "linkedin_headline": "Growth Marketing Expert | B2B SaaS"
}
```

### Frontend Usage

**Creating Leads:**
- New LinkedIn URL field in Create Lead modal
- Optional fields for job title, seniority, company size

**Enriching Existing Leads:**
- Add LinkedIn URL to lead
- Click "Enrich from LinkedIn" button
- Data automatically populates

### Supported Enrichment Providers

1. **Clearbit** (recommended)
   - API: https://clearbit.com/
   - Best for US/international profiles

2. **Apollo.io**
   - API: https://apollo.io/
   - Great B2B database

3. **Snov.io**
   - API: https://snov.io/
   - Good for bulk enrichment

### Configuration

Add to `.env`:

```env
# Choose provider: clearbit, apollo, or snov
ENRICHMENT_PROVIDER=clearbit

# API key for your chosen provider
ENRICHMENT_API_KEY=your_enrichment_api_key_here
```

### Database Changes

New fields added to `leads` table:
- `linkedin_url` - VARCHAR(500)
- `job_title` - VARCHAR(255)
- `seniority` - VARCHAR(100) (Entry, Mid, Senior, Manager, Director, VP, C-Level)
- `company_size` - VARCHAR(100) (1-10, 11-50, 51-200, etc.)
- `linkedin_headline` - VARCHAR(500)

---

## 📧 Feature 3: Enhanced Deliverability Tools

### What It Does

Provides tools to ensure email deliverability and avoid spam filters:
1. DNS record checker (SPF, DKIM, DMARC, MX)
2. Domain warm-up scheduler

### 3.1 DNS Record Checker

Checks email authentication records for any domain.

#### API Endpoint

```http
POST /api/deliverability/check-dns
Content-Type: application/json

{
  "domain": "example.com"
}
```

**Response:**
```json
{
  "domain": "example.com",
  "spf": {
    "exists": true,
    "record": "v=spf1 include:_spf.google.com ~all",
    "valid": true,
    "issues": []
  },
  "dkim": {
    "exists": true,
    "record": "...",
    "note": "Found DKIM record with selector: google"
  },
  "dmarc": {
    "exists": true,
    "record": "v=DMARC1; p=quarantine; rua=...",
    "policy": "quarantine",
    "valid": true,
    "issues": []
  },
  "mx": {
    "exists": true,
    "records": ["10 mx.example.com"]
  },
  "overall_score": 90,
  "recommendations": [...]
}
```

#### Frontend Usage

Navigate to `/deliverability-tools`:

1. Enter domain name
2. Click "Check DNS"
3. View results:
   - Overall score (0-100)
   - Individual record status
   - DNS record values
   - Recommendations

#### Scoring System

- **SPF**: 30 points (20 for exists, 10 for valid)
- **DKIM**: 25 points
- **DMARC**: 30 points (20 for exists, 10 for valid)
- **MX**: 15 points

**Score Interpretation:**
- 80-100: Excellent
- 50-79: Needs improvement
- 0-49: Critical issues

### 3.2 Email Warm-up Scheduler

Gradually increases sending volume to build domain reputation.

#### How It Works

**Warm-up Schedule:**
- Day 1: 10 emails/day
- Days 2-7: Increase by 5 emails/day
- Days 8+: Increase by 10 emails/day
- Cap: 200 emails/day

The system enforces these limits automatically during email sending.

#### API Endpoints

**Create Warmup Schedule:**
```http
POST /api/deliverability/warmup-domains
Content-Type: application/json

{
  "domain": "example.com"
}
```

**List Warmup Domains:**
```http
GET /api/deliverability/warmup-domains
```

**Get Warmup Status:**
```http
GET /api/deliverability/warmup-domains/{domain}/status
```

**Response:**
```json
{
  "domain": "example.com",
  "warmup_day": 5,
  "daily_limit": 30,
  "emails_sent_today": 12,
  "remaining_today": 18,
  "next_limit": 35,
  "warmup_complete": false
}
```

#### Frontend Usage

On `/deliverability-tools` page:

1. Enter domain to warm up
2. Click "Add Domain"
3. View warmup table:
   - Current day
   - Daily limit
   - Emails sent today
   - Remaining quota

#### Integration with Email Sending

The warmup limits are enforced automatically in the `send_email_task` worker:

```python
# Check warmup quota before sending
warmup_domain = get_warmup_domain(sender_domain)
if warmup_domain.emails_sent_today >= warmup_domain.daily_limit:
    raise QuotaExceededError("Daily warmup limit reached")
```

### Database Changes

New table `email_warmup_domains`:
- `id` - UUID
- `org_id` - UUID
- `domain` - VARCHAR(500)
- `daily_limit` - INTEGER
- `warmup_day` - INTEGER
- `emails_sent_today` - INTEGER
- `last_reset_date` - TIMESTAMP

---

## 🗄️ Database Migrations

Run migrations to add new tables and fields:

```bash
cd backend
alembic upgrade head
```

This applies migration `009_v1_features` which:
- Creates `lead_discovery_jobs` table
- Creates `discovered_domains` table
- Adds LinkedIn fields to `leads` table
- Creates `email_warmup_domains` table

---

## 📦 Dependencies

New Python packages added (see `requirements.txt`):

```
requests==2.31.0          # HTTP requests for scraping
beautifulsoup4==4.12.2    # HTML parsing
dnspython==2.4.2          # DNS queries
openai==1.3.0             # AI enrichment
```

Install:
```bash
cd backend
pip install -r requirements.txt
```

---

## ⚙️ Configuration Summary

Add these to your `.env` file:

```env
# Lead Discovery
SERP_API_KEY=                  # Optional: For better search results
# Note: Uses existing GEMINI_API_KEY for company enrichment

# LinkedIn Enrichment
ENRICHMENT_PROVIDER=clearbit   # clearbit, apollo, or snov
ENRICHMENT_API_KEY=            # Required: Provider API key

# Existing configs (keep these)
DATABASE_URL=
REDIS_URL=
SECRET_KEY=
GEMINI_API_KEY=
ENCRYPTION_KEY=
```

---

## 🧪 Testing

### Test Lead Discovery

```bash
# Start discovery job
curl -X POST http://localhost:8000/api/lead-discovery/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"keywords": "AI software", "location": "India", "max_results": 5}'

# Check status
curl http://localhost:8000/api/lead-discovery/{JOB_ID} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test LinkedIn Enrichment

```bash
curl -X POST http://localhost:8000/api/leads/{LEAD_ID}/linkedin-enrich?linkedin_url=https://linkedin.com/in/username \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test DNS Checker

```bash
curl -X POST http://localhost:8000/api/deliverability/check-dns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"domain": "google.com"}'
```

---

## 🚀 Deployment Checklist

1. ✅ Update environment variables
2. ✅ Run database migrations
3. ✅ Install new dependencies
4. ✅ Restart backend server
5. ✅ Restart Celery workers
6. ✅ Rebuild frontend
7. ✅ Test all three features
8. ✅ Configure API keys (SERP, OpenAI, Enrichment)

---

## 📊 Architecture Diagram

```
┌─────────────────┐
│   Frontend      │
│  React + Vite   │
└────────┬────────┘
         │
         ├─→ /discover-leads → DiscoverLeadsPage
         ├─→ /leads → CreateLeadModal (LinkedIn fields)
         └─→ /deliverability-tools → DeliverabilityPage
         │
         ↓
┌─────────────────┐
│   Backend API   │
│    FastAPI      │
└────────┬────────┘
         │
         ├─→ /api/lead-discovery/* → lead_discovery.py
         ├─→ /api/leads/{id}/linkedin-enrich → leads.py
         └─→ /api/deliverability/* → deliverability.py
         │
         ↓
┌─────────────────┐     ┌─────────────────┐
│  Celery Worker  │────→│   Services      │
│ lead_discovery  │     │ - serp_scraper  │
└─────────────────┘     │ - domain_crawler│
                        │ - enrichment    │
                        │ - dns_checker   │
                        └─────────────────┘
                               ↓
                        ┌─────────────────┐
                        │  External APIs  │
                        │ - SerpAPI       │
                        │ - OpenAI        │
                        │ - Clearbit etc  │
                        └─────────────────┘
```

---

## 🔒 Security Considerations

### Lead Discovery
- Rate limiting applied to prevent abuse
- Respect robots.txt (crawler follows rules)
- User-agent identifies bot clearly
- No aggressive scraping

### LinkedIn Enrichment
- Uses official APIs only
- No direct LinkedIn scraping
- API keys stored securely in environment
- Rate limits respected per provider

### DNS Checker
- Read-only queries
- No modifications made
- Public DNS records only

---

## 📈 Performance Notes

### Lead Discovery
- ~3-5 seconds per domain crawl
- 20 domains = ~2-3 minutes total
- Runs in background (non-blocking)
- Progress updates every 3 seconds

### LinkedIn Enrichment
- ~1-2 seconds per profile
- Synchronous (user waits)
- Consider queueing for bulk operations

### DNS Checker
- ~1-2 seconds per domain
- Synchronous (instant results)
- Cached results recommended for production

---

## 🐛 Troubleshooting

### Lead Discovery Not Finding Domains

**Problem:** Job completes with 0 domains found

**Solutions:**
- Try broader keywords
- Remove location filter
- Check if SERP_API_KEY is set (recommended)
- Verify internet connectivity

### LinkedIn Enrichment Failing

**Problem:** Enrichment returns errors

**Solutions:**
- Verify ENRICHMENT_API_KEY is valid
- Check API quota/credits
- Ensure LinkedIn URL format is correct
- Try different provider

### DNS Checker Shows Low Score

**Problem:** Domain scores < 50

**Solutions:**
- Add SPF record: `v=spf1 include:_spf.google.com ~all`
- Configure DKIM with your email provider
- Add DMARC record: `v=DMARC1; p=quarantine; rua=mailto:admin@domain.com`
- Verify MX records exist

---

## 📝 Future Enhancements (Not in v1)

- [ ] Advanced proxy rotation
- [ ] LinkedIn scraping alternatives
- [ ] Tech stack detection
- [ ] Industry-specific scrapers
- [ ] Bulk LinkedIn enrichment
- [ ] Custom warmup schedules
- [ ] DKIM selector auto-detection
- [ ] Real-time deliverability scoring

---

## 📞 Support

For issues or questions:
1. Check logs: `docker-compose logs backend`
2. Review API docs: `http://localhost:8000/docs`
3. Test individual services separately
4. Verify all environment variables set

---

**Version:** 1.0.0  
**Last Updated:** December 16, 2025  
**Status:** Production Ready ✅
