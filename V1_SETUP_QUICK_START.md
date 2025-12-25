# v1 Quick Setup Guide

## Prerequisites

- Existing project running (Backend, Frontend, PostgreSQL, Redis, Celery)
- Python 3.9+
- Node.js 16+

## Step 1: Update Environment Variables

Add to your `.env` file in the `backend/` directory:

```env
# Lead Discovery & Enrichment
# Note: Uses existing GEMINI_API_KEY for company enrichment
SERP_API_KEY=                            # Optional: Better search results (serpapi.com)
ENRICHMENT_API_KEY=                      # Required for LinkedIn (clearbit.com/apollo.io)
ENRICHMENT_PROVIDER=clearbit             # Options: clearbit, apollo, snov
```

## Step 2: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New packages installed:
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `dnspython` - DNS queries
- `openai` - AI enrichment

## Step 3: Run Database Migrations

```bash
cd backend
alembic upgrade head
```

This creates:
- `lead_discovery_jobs` table
- `discovered_domains` table
- `email_warmup_domains` table
- Adds LinkedIn fields to `leads` table

## Step 4: Restart Services

```bash
# Using Docker Compose
docker-compose restart backend celery

# Or manually
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Celery Worker
cd backend
celery -A app.celery_app worker --loglevel=info
```

## Step 5: Verify Frontend Routes

Frontend should already include new pages:
- `/discover-leads` - Lead Discovery
- `/deliverability-tools` - DNS Checker & Warmup

Navigate to these URLs to test.

## Step 6: Test Features

### Test 1: Lead Discovery

1. Navigate to `/discover-leads`
2. Enter:
   - Keywords: "AI software"
   - Location: "USA"
   - Max Results: 5
3. Click "Discover Leads"
4. Wait for completion (~2-3 minutes)
5. Check `/leads` for new leads

### Test 2: LinkedIn Enrichment

1. Navigate to `/leads`
2. Click "Create Lead"
3. Fill in basic info + LinkedIn URL
4. Or edit existing lead and add LinkedIn URL
5. Click "Enrich from LinkedIn" (if available)

### Test 3: DNS Checker

1. Navigate to `/deliverability-tools`
2. Enter domain: `gmail.com`
3. Click "Check DNS"
4. View score and recommendations

### Test 4: Email Warmup

1. On `/deliverability-tools`
2. Enter your sending domain
3. Click "Add Domain"
4. View warmup schedule in table

## Troubleshooting

### Issue: Lead Discovery finds 0 domains

**Solution:** Set `SERP_API_KEY` for better results:
1. Sign up at serpapi.com
2. Get API key
3. Add to `.env`
4. Restart backend

**Note:** Ensure your `GEMINI_API_KEY` is set for company enrichment

### Issue: LinkedIn enrichment fails

**Solution:** Configure enrichment provider:
1. Choose provider: Clearbit (recommended), Apollo, or Snov
2. Sign up for API key
3. Add to `.env`:
   ```
   ENRICHMENT_PROVIDER=clearbit
   ENRICHMENT_API_KEY=your_key
   ```
4. Restart backend

### Issue: DNS checker not working

**Solution:** Install dnspython:
```bash
pip install dnspython==2.4.2
```

### Issue: Celery worker not picking up jobs

**Solution:** 
1. Check Redis is running: `docker-compose ps redis`
2. Restart Celery worker
3. Check logs: `docker-compose logs celery`

### Issue: Frontend routes not found

**Solution:**
1. Verify App.jsx has new routes
2. Check page files exist in `frontend/src/pages/`
3. Rebuild frontend: `npm run build`

## API Testing with cURL

### Start Lead Discovery
```bash
curl -X POST http://localhost:8000/api/lead-discovery/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "keywords": "AI software",
    "location": "India",
    "industry": "SaaS",
    "max_results": 10
  }'
```

### Check DNS Records
```bash
curl -X POST http://localhost:8000/api/deliverability/check-dns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"domain": "google.com"}'
```

### LinkedIn Enrich
```bash
curl -X POST "http://localhost:8000/api/leads/{LEAD_ID}/linkedin-enrich?linkedin_url=https://linkedin.com/in/username" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Verification Checklist

- [ ] Backend starts without errors
- [ ] Celery worker starts without errors
- [ ] Database migrations applied
- [ ] `/discover-leads` page loads
- [ ] `/deliverability-tools` page loads
- [ ] Can create lead with LinkedIn fields
- [ ] DNS checker returns results
- [ ] Lead discovery job can be started
- [ ] Warmup domain can be added

## Next Steps

1. Configure your API keys for production use
2. Test lead discovery with real keywords
3. Set up warmup for your sending domains
4. Check DNS records for your domains
5. Import or create leads with LinkedIn enrichment

## Getting API Keys

### Google Gemini (Already Configured)
Your existing `GEMINI_API_KEY` is automatically used for company enrichment.
No additional setup needed!

### SerpAPI (Optional, Recommended)
1. Visit: https://serpapi.com/
2. Sign up
3. Get API key from dashboard
4. Add to `.env` as `SERP_API_KEY`
5. Free tier: 100 searches/month

### Clearbit (Recommended for LinkedIn)
1. Visit: https://clearbit.com/
2. Sign up for free trial
3. Get API key
4. Add to `.env` as `ENRICHMENT_API_KEY`
5. Set `ENRICHMENT_PROVIDER=clearbit`

### Apollo.io (Alternative)
1. Visit: https://apollo.io/
2. Sign up
3. Get API key from settings
4. Add to `.env` as `ENRICHMENT_API_KEY`
5. Set `ENRICHMENT_PROVIDER=apollo`

## Success!

Your v1 features are now installed and ready to use! 🎉

Key features available:
✅ Automated lead discovery
✅ LinkedIn profile enrichment
✅ DNS record checking
✅ Email warm-up scheduling

For detailed documentation, see `V1_FEATURES_GUIDE.md`.
