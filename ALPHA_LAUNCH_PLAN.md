# Alpha Launch Readiness Plan

**Goal**: Prepare for controlled alpha launch with focus on stability, safety, and user trust.

**NOT included**: Scaling, multi-tenant features, billing automation, growth features.

---

## 🟢 PART 1: Onboarding Flow Polishing

### Current State Audit
- ❌ No guided onboarding wizard
- ❌ Empty state screens missing
- ❌ Users land directly on Leads page with no guidance
- ❌ No warnings for missing email provider
- ❌ No warmup guidance on first use

### Required Improvements

#### 1.1 Onboarding Wizard Component
**Location**: `frontend/src/components/OnboardingWizard.jsx`

**Steps**:
1. **Welcome** - Brief intro, set expectations
2. **Connect Email Provider** - Guide to Settings → Email Provider
3. **Add First Lead** - Import CSV or manual add
4. **Create First Campaign** - Simple campaign creation
5. **Review & Safety** - Warmup guidance, daily limits

**Copy Suggestions**:
```
Step 1: Welcome to LeadGen
"We'll help you send personalized cold emails safely. This setup takes 3 minutes."

Step 2: Connect Your Email Provider
"Connect SendGrid or SMTP to send emails. Don't have one? We'll show you how to get started."
⚠️ Warning: "Never use your primary work email for cold outreach."

Step 3: Add Your First Leads
"Import a CSV or add leads manually. Start small - quality over quantity."
✅ Best practice: "10-20 highly relevant leads for your first campaign."

Step 4: Create Your First Campaign
"Our AI will help you write personalized emails. You can review and edit before sending."
🛡️ Safety: "We recommend starting with 5-10 emails per day during warmup."

Step 5: Warmup & Send Safely
"Email warmup protects your sender reputation. Day 1: send 10 emails, gradually increase."
📊 "Check the Deliverability page daily to monitor your email health."
```

#### 1.2 Empty State Screens

**Leads Page** (`frontend/src/pages/Leads.jsx`):
```jsx
{leads.length === 0 && (
  <EmptyState
    icon={<Users />}
    title="No leads yet"
    description="Add leads manually or import from CSV to start your first campaign."
    actions={[
      { label: "Import CSV", onClick: handleImportCSV, variant: "primary" },
      { label: "Add Manual Lead", onClick: handleAddLead, variant: "outline" }
    ]}
    helpText="💡 Tip: Start with 10-20 high-quality leads for best results."
  />
)}
```

**Campaigns Page** (`frontend/src/pages/Campaigns.jsx`):
```jsx
{campaigns.length === 0 && (
  <EmptyState
    icon={<Mail />}
    title="No campaigns yet"
    description="Create your first campaign to start sending personalized emails."
    actions={[
      { label: "Create Campaign", onClick: handleCreateCampaign, variant: "primary" }
    ]}
    helpText="⚠️ Make sure you've connected an email provider in Settings first."
    warning={!hasEmailProvider && "Email provider not configured"}
  />
)}
```

**Metrics Dashboard** (`frontend/src/pages/MetricsDashboard.jsx`):
```jsx
{!hasAnySends && (
  <EmptyState
    icon={<BarChart3 />}
    title="No metrics yet"
    description="Send your first campaign to see performance metrics here."
    helpText="📊 Metrics appear after you activate a campaign and send emails."
  />
)}
```

#### 1.3 Safety Warnings & Blockers

**Email Provider Missing Warning**:
```jsx
{!hasEmailProvider && (
  <Alert variant="destructive">
    <AlertTriangle className="h-4 w-4" />
    <AlertTitle>Email Provider Required</AlertTitle>
    <AlertDescription>
      You need to configure an email provider before sending campaigns.
      <Link to="/settings">Go to Settings →</Link>
    </AlertDescription>
  </Alert>
)}
```

**Warmup Incomplete Warning**:
```jsx
{warmupDay < 7 && (
  <Alert variant="warning">
    <Info className="h-4 w-4" />
    <AlertTitle>Warmup in Progress (Day {warmupDay}/21)</AlertTitle>
    <AlertDescription>
      Send {dailyLimit} emails today. Gradually increase over 21 days to protect your reputation.
    </AlertDescription>
  </Alert>
)}
```

**Research Notes Missing Warning** (in Campaign Editor):
```jsx
{!lead.research_notes && (
  <Alert variant="warning">
    <AlertDescription>
      No research notes for this lead. AI email quality will be lower without context.
      <Button size="sm" onClick={() => generateResearch(lead)}>Generate Research</Button>
    </AlertDescription>
  </Alert>
)}
```

### 1.4 Onboarding Checklist Component
**Location**: `frontend/src/components/OnboardingChecklist.jsx`

Shows progress in header/dashboard:
```
✅ Account created
✅ Email provider connected
⏳ Add first lead (0/1)
⏳ Create first campaign (0/1)
⏳ Send first test email
```

---

## 🟡 PART 2: UI Stability + UX Quality

### 2.1 Error States

**Global Error Boundary**:
```jsx
// frontend/src/components/ErrorBoundary.jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null }
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Caught error:', error, errorInfo)
    // Log to monitoring service in production
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <Card>
            <CardHeader>
              <AlertTriangle className="w-12 h-12 text-red-500 mx-auto" />
              <CardTitle>Something went wrong</CardTitle>
            </CardHeader>
            <CardContent>
              <p>We've logged this error. Please refresh the page to continue.</p>
              <Button onClick={() => window.location.reload()}>Refresh Page</Button>
            </CardContent>
          </Card>
        </div>
      )
    }
    return this.props.children
  }
}
```

**API Error Handling** (in `frontend/src/api/axios.js`):
```javascript
axios.interceptors.response.use(
  response => response,
  error => {
    const message = error.response?.data?.detail || error.message || 'Something went wrong'
    
    // Show user-friendly error messages
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login'
    } else if (error.response?.status === 429) {
      toast.error('Too many requests. Please slow down.')
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again in a moment.')
    } else {
      toast.error(message)
    }
    
    return Promise.reject(error)
  }
)
```

### 2.2 Loading States

**Consistent Loading Patterns**:
```jsx
// Use LoadingSpinner for all async operations
{loading && <LoadingSpinner size="lg" text="Loading campaigns..." />}

// Skeleton loaders for lists
{loading ? (
  <SkeletonList count={5} />
) : (
  campaigns.map(campaign => <CampaignCard key={campaign.id} campaign={campaign} />)
)}

// Disable buttons during async operations
<Button isLoading={sending} disabled={sending || !canSend}>
  {sending ? 'Sending...' : 'Send Campaign'}
</Button>
```

### 2.3 Debounce & Duplicate Prevention

**Campaign Creation**:
```jsx
const [isCreating, setIsCreating] = useState(false)

const handleCreateCampaign = async () => {
  if (isCreating) return // Prevent double-click
  
  setIsCreating(true)
  try {
    await createCampaign(data)
  } finally {
    setIsCreating(false)
  }
}
```

**Search Inputs**:
```jsx
import { useDebouncedCallback } from 'use-debounce'

const debouncedSearch = useDebouncedCallback(
  (value) => fetchResults(value),
  500
)
```

### 2.4 Validation Messages

**Form Validation** (Campaign Editor):
```jsx
const validation = {
  name: {
    required: "Campaign name is required",
    minLength: { value: 3, message: "Name must be at least 3 characters" }
  },
  subject: {
    required: "Email subject is required",
    maxLength: { value: 78, message: "Subject should be under 78 characters" }
  },
  body: {
    required: "Email body is required",
    validate: (value) => {
      if (!value.includes('{{')) return "Add at least one personalization variable"
      if (value.length < 50) return "Email is too short - aim for 80-150 words"
      if (value.length > 2000) return "Email is too long - keep it concise"
      return true
    }
  }
}
```

### 2.5 Micro-Copy Improvements

**Button States**:
- ❌ "Save" → ✅ "Save Campaign"
- ❌ "Submit" → ✅ "Activate Campaign"
- ❌ "Delete" → ✅ "Delete Permanently"

**Confirmation Dialogs**:
```
"Delete this campaign?"
→ "Delete 'Q1 Outreach' campaign? This cannot be undone."

"Activate campaign?"
→ "Send to 50 leads starting today? Daily limit: 15 emails/day during warmup."
```

---

## 🧾 PART 3: Documentation Finalization

### 3.1 README Updates

**Add to README.md**:
```markdown
## ⚠️ Alpha Release - Safety First

This is an ALPHA release for controlled testing. Not recommended for production use yet.

### Known Limitations
- **Warmup guidance is advisory only** - Not enforced by system
- **Daily send limits are recommendations** - You must self-monitor
- **Webhook events require manual SendGrid configuration**
- **Blacklist monitoring not implemented** - Use external tools (MXToolbox)
- **No billing integration** - Pricing is informational only

### Safe Usage Guidelines
1. **Start small**: 5-10 emails/day for first week
2. **Monitor deliverability page daily** - Watch bounce/spam rates
3. **Never use personal email** - Use dedicated sending domain
4. **Clean your lists** - Remove bounces immediately
5. **Personalize every email** - Generic blasts harm reputation

### Quick Start (3 Minutes)
1. **Sign Up** - Create account at http://localhost:3000/signup
2. **Connect Email Provider** - Settings → Add SendGrid API key or SMTP
3. **Import Leads** - Upload CSV with email, name, company
4. **Create Campaign** - Let AI generate personalized emails
5. **Review & Send** - Check deliverability warnings before activating

### Troubleshooting
- **"Email provider not configured"** - Go to Settings → Email Provider
- **"No events in webhook page"** - Configure SendGrid webhooks (see SENDGRID_WEBHOOK_SETUP.md)
- **High bounce rate** - Stop sending, clean your list
- **Emails not sending** - Check backend logs: `docker logs leadgen_backend`
```

### 3.2 Quick Reference Card

**Create**: `ALPHA_QUICK_REFERENCE.md`
```markdown
# Alpha Quick Reference

## Daily Workflow
1. Check Deliverability page - Monitor bounce/spam rates
2. Review daily send limit - Don't exceed recommendation
3. Check campaign status - Ensure sends are succeeding
4. Monitor webhook events - Look for bounces/spam complaints

## Safety Checks Before Sending
- [ ] Email provider connected and tested
- [ ] Leads have valid email addresses
- [ ] Research notes added for personalization
- [ ] Subject line under 78 characters
- [ ] Email body 80-150 words
- [ ] Within daily send limit
- [ ] Deliverability score > 70

## When Things Go Wrong
| Problem | Solution |
|---------|----------|
| Bounce rate > 5% | STOP sending immediately, clean list |
| Spam rate > 0.1% | Review email content, improve relevance |
| Emails not sending | Check Settings → Email Provider credentials |
| Deliverability score < 60 | Review recommendations, pause campaigns |

## Support
- Documentation: See README.md
- Webhook setup: See SENDGRID_WEBHOOK_SETUP.md
- Test data: Use scripts/insert_test_events.sql
```

### 3.3 Honest Expectations Document

**Create**: `ALPHA_EXPECTATIONS.md`
```markdown
# Alpha Release Expectations

## What Works Well
✅ AI email generation with personalization
✅ Campaign management and scheduling
✅ CSV lead import
✅ SendGrid and SMTP integration
✅ Basic deliverability monitoring
✅ Webhook event tracking (with setup)

## What's Advisory Only
⚠️ Daily send limits (recommendations, not enforced)
⚠️ Warmup guidance (not automatically controlled)
⚠️ Bounce rate warnings (you must take action)

## What's Not Yet Implemented
❌ Automatic send throttling
❌ Blacklist monitoring (use MXToolbox)
❌ Billing/payments (pricing is mock only)
❌ Multi-user organizations
❌ Email open/click tracking
❌ A/B testing
❌ Automatic list cleaning

## Timeline
- **Alpha (Current)**: Controlled testing, safety focus
- **Beta (Next)**: Automatic enforcement, more automation
- **v1.0 (Future)**: Full feature set, public launch

## Your Responsibility
You are responsible for:
- Monitoring your sender reputation
- Respecting daily send limits
- Cleaning bounced emails from lists
- Checking deliverability metrics daily
- Following email marketing best practices
```

---

## 🐞 PART 4: Bug Cleanup + Crash Hardening

### 4.1 Backend Exception Handling

**Campaign Sending** (`backend/app/workers/campaign_worker.py`):
```python
@celery_app.task(bind=True, max_retries=3)
def send_campaign_emails(self, campaign_id: str):
    try:
        # ... existing code ...
    except EmailProviderError as e:
        logger.error(f"Email provider error for campaign {campaign_id}: {e}")
        # Don't retry provider errors - they need manual fix
        raise self.retry(exc=e, countdown=None, max_retries=0)
    except NetworkError as e:
        logger.warning(f"Network error for campaign {campaign_id}, retrying: {e}")
        # Retry network errors with backoff
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
    except Exception as e:
        logger.exception(f"Unexpected error in campaign {campaign_id}")
        # Log but don't crash - mark campaign as failed
        update_campaign_status(campaign_id, "failed", error_message=str(e))
        return {"status": "failed", "error": str(e)}
```

**AI Email Generation** (`backend/app/services/gemini_service.py`):
```python
def generate_email(self, lead_data: dict, campaign_context: str) -> dict:
    try:
        response = self.client.generate_content(...)
        
        if not response or not response.text:
            logger.warning("Empty response from Gemini API")
            return self._fallback_email_template(lead_data)
        
        return self._parse_response(response.text)
        
    except GoogleAPIError as e:
        logger.error(f"Gemini API error: {e}")
        # Return fallback instead of crashing
        return self._fallback_email_template(lead_data)
        
    except Exception as e:
        logger.exception("Unexpected error in AI generation")
        return self._fallback_email_template(lead_data)

def _fallback_email_template(self, lead_data: dict) -> dict:
    """Safe fallback when AI fails"""
    return {
        "subject": f"Question about {lead_data.get('company', 'your company')}",
        "body": f"Hi {lead_data.get('name', 'there')},\n\n[AI generation failed - please write manually]\n\nBest regards",
        "ai_failed": True
    }
```

### 4.2 Database Operations Safety

**Batch Operations with Error Handling**:
```python
def bulk_import_leads(db: Session, leads_data: List[dict], org_id: str) -> dict:
    """Import leads with partial failure tolerance"""
    results = {"success": 0, "failed": 0, "errors": []}
    
    for idx, lead_data in enumerate(leads_data):
        try:
            lead = Lead(**lead_data, org_id=org_id)
            db.add(lead)
            db.flush()  # Flush each lead individually
            results["success"] += 1
        except IntegrityError as e:
            db.rollback()
            results["failed"] += 1
            results["errors"].append(f"Row {idx + 1}: Duplicate email")
        except ValidationError as e:
            db.rollback()
            results["failed"] += 1
            results["errors"].append(f"Row {idx + 1}: {str(e)}")
        except Exception as e:
            db.rollback()
            results["failed"] += 1
            results["errors"].append(f"Row {idx + 1}: Unexpected error")
            logger.exception(f"Lead import error at row {idx + 1}")
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception("Failed to commit lead import")
        raise
    
    return results
```

### 4.3 Celery Task Crash Protection

**Task Wrapper** (`backend/app/workers/__init__.py`):
```python
def safe_task(func):
    """Decorator to make Celery tasks crash-resistant"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SoftTimeLimitExceeded:
            logger.error(f"Task {func.__name__} exceeded time limit")
            return {"status": "timeout"}
        except Exception as e:
            logger.exception(f"Task {func.__name__} failed")
            return {"status": "error", "message": str(e)}
    return wrapper

@celery_app.task
@safe_task
def send_email_task(lead_id: str, campaign_id: str):
    # ... task logic ...
```

### 4.4 Logging Improvements

**Structured Logging** (`backend/app/config.py`):
```python
import logging
import json

class StructuredLogger(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🛡 PART 5: Reliability + Safety Tests

### 5.1 QA Checklist

**Create**: `QA_CHECKLIST.md`
```markdown
# Alpha Release QA Checklist

## Pre-Launch Smoke Tests

### Authentication
- [ ] Sign up with valid email
- [ ] Sign up with duplicate email (should fail gracefully)
- [ ] Login with correct credentials
- [ ] Login with wrong password (should show error)
- [ ] Logout and login again

### Email Provider Setup
- [ ] Add SendGrid API key
- [ ] Add invalid API key (should show error)
- [ ] Test connection with valid key
- [ ] Update existing provider settings

### Lead Management
- [ ] Import CSV with valid leads
- [ ] Import CSV with invalid emails (should report errors)
- [ ] Add single lead manually
- [ ] Edit existing lead
- [ ] Delete lead
- [ ] Search/filter leads

### Campaign Creation
- [ ] Create campaign without email provider (should block)
- [ ] Create campaign with valid settings
- [ ] Generate AI email for lead with research notes
- [ ] Generate AI email without research notes
- [ ] Edit generated email
- [ ] Save draft campaign
- [ ] Activate campaign

### Campaign Sending
- [ ] Send test email to single lead
- [ ] Activate campaign with 10 leads
- [ ] Monitor sending progress
- [ ] Check daily limit warnings
- [ ] Verify emails sent via provider dashboard
- [ ] Check sending_logs table for SENT status

### Deliverability Monitoring
- [ ] Check deliverability score on Day 1
- [ ] View warmup progress
- [ ] Run safety diagnostics
- [ ] Review recommendations
- [ ] Check bounce rate (with test data)
- [ ] Check spam rate (with test data)

### Webhook Events
- [ ] Configure SendGrid webhook (follow SENDGRID_WEBHOOK_SETUP.md)
- [ ] Send test email
- [ ] Verify delivery event appears in webhook page
- [ ] Check bounce event handling
- [ ] Verify spam complaint tracking

### Error Handling
- [ ] Submit form with missing required fields
- [ ] Upload invalid CSV format
- [ ] Try to send campaign while at daily limit
- [ ] Disconnect internet during operation
- [ ] Invalid API responses from email provider

### Safety Features
- [ ] Daily send limit warning appears correctly
- [ ] Warmup guidance shown to new users
- [ ] High bounce rate triggers warning
- [ ] High spam rate triggers critical alert
- [ ] Missing email provider blocks sending

## Regression Tests

### Data Integrity
- [ ] Campaign leads persisted correctly
- [ ] Sending logs recorded accurately
- [ ] Inbound events stored properly
- [ ] User settings saved correctly

### Performance
- [ ] Page loads complete within 2 seconds
- [ ] CSV import of 100 leads completes within 10 seconds
- [ ] AI email generation completes within 10 seconds
- [ ] Campaign activation response within 3 seconds

### Browser Compatibility
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

## Critical Path Tests

### Happy Path: First Campaign
1. Sign up → Email provider → Import leads → Create campaign → Activate → Monitor

### Safety Path: Warmup Compliance
1. New user → Check daily limit → Send within limit → Check next day limit

### Recovery Path: Fix Errors
1. High bounce rate → Stop campaign → Clean list → Resume sending

## Notes
- Document any bugs found
- Note performance issues
- Record user confusion points
- List feature requests separately
```

### 5.2 Automated Test Scenarios

**Create**: `backend/tests/test_campaign_safety.py`
```python
import pytest
from app.services.campaign_service import should_allow_sending

def test_blocks_sending_without_provider():
    """Sending should be blocked if no email provider configured"""
    user = create_test_user(has_provider=False)
    campaign = create_test_campaign(user_id=user.id)
    
    result = should_allow_sending(campaign, user)
    
    assert result["allowed"] == False
    assert "email provider" in result["reason"].lower()

def test_warns_during_warmup():
    """Should show warning during warmup period"""
    user = create_test_user(warmup_day=5)
    campaign = create_test_campaign(user_id=user.id, lead_count=50)
    
    result = should_allow_sending(campaign, user)
    
    assert "warmup" in result["warning"].lower()
    assert result["recommended_daily_sends"] == 30  # Day 5 limit

def test_blocks_when_daily_limit_exceeded():
    """Should block sending when daily limit exceeded"""
    user = create_test_user(warmup_day=3, daily_limit=20)
    # User already sent 20 emails today
    create_sending_logs(user_id=user.id, count=20, date=today())
    campaign = create_test_campaign(user_id=user.id)
    
    result = should_allow_sending(campaign, user)
    
    assert result["allowed"] == False
    assert "daily limit" in result["reason"].lower()

def test_allows_sending_when_safe():
    """Should allow sending when all conditions met"""
    user = create_test_user(has_provider=True, warmup_day=10, daily_limit=50)
    create_sending_logs(user_id=user.id, count=10, date=today())  # 10/50 sent
    campaign = create_test_campaign(user_id=user.id, lead_count=20)
    
    result = should_allow_sending(campaign, user)
    
    assert result["allowed"] == True
    assert result["remaining_today"] == 40
```

### 5.3 Manual Test Flows

**Create**: `MANUAL_TEST_FLOWS.md`
```markdown
# Manual Test Flows

## Flow 1: Complete New User Journey (10 minutes)
**Goal**: Verify end-to-end experience for first-time user

1. Open http://localhost:3000/signup
2. Sign up with test email: alpha-test-1@example.com
3. Should redirect to /leads page
4. Expect: Empty state with "No leads yet" message
5. Click "Settings" in sidebar
6. Add SendGrid API key: [use test key]
7. Click "Test Connection"
8. Expect: Success message "Email provider connected"
9. Go back to Leads
10. Click "Import CSV"
11. Upload sample_leads.csv (10 leads)
12. Expect: Success message "10 leads imported"
13. Verify leads appear in table
14. Click "Campaigns" in sidebar
15. Click "Create Campaign"
16. Enter campaign name: "Alpha Test Campaign 1"
17. Select 5 leads from list
18. Click "Generate AI Emails"
19. Expect: Loading spinner, then emails appear
20. Review generated emails
21. Click "Save Draft"
22. Click "Activate Campaign"
23. Expect: Warning about warmup (Day 1, limit 10 emails)
24. Confirm activation
25. Go to Deliverability page
26. Verify health score shown (should be ~70-80)
27. Check warmup status: Day 1/21
28. Verify daily limit: 0/10 (or small number if sends completed)

**Success Criteria**:
- No errors at any step
- All pages load within 2 seconds
- Warnings display correctly
- Campaign activates successfully

## Flow 2: High Bounce Rate Scenario (5 minutes)
**Goal**: Test safety warnings when deliverability drops

1. Login as existing user
2. Use script to insert bounce events:
   ```sql
   -- Insert 20 bounce events
   INSERT INTO inbound_events (...)
   ```
3. Go to Deliverability page
4. Expect: Red alert "CRITICAL: Bounce rate is 40%"
5. Expect: Recommendation "URGENT: Stop sending immediately"
6. Health score should be < 50
7. Bounce rate check should show "FAIL" status

**Success Criteria**:
- Critical warnings displayed prominently
- Health score reflects severity
- Actionable recommendations provided

## Flow 3: Daily Limit Enforcement (5 minutes)
**Goal**: Test advisory limit warnings

1. Login as user on Day 5 of warmup
2. Daily limit should be 30 emails
3. Manually send 25 emails via campaign
4. Go to Deliverability page
5. Expect: Warning "Approaching daily send limit (25/30)"
6. Send 6 more emails (exceeds limit)
7. Expect: Critical warning "Exceeded daily limit (31/30)"
8. Try to activate new campaign
9. Should show warning but still allow (advisory only)

**Success Criteria**:
- Warnings display at 80% and 100% of limit
- System doesn't hard-block (advisory mode)
- User understands they've exceeded recommendation

## Flow 4: Error Recovery (5 minutes)
**Goal**: Test graceful error handling

1. Login as user
2. Create campaign
3. Disconnect internet
4. Try to generate AI email
5. Expect: Error message "Failed to generate email"
6. Reconnect internet
7. Try again
8. Expect: Successful generation
9. Submit form with empty required field
10. Expect: Validation error shown inline
11. Fix validation error
12. Submit successfully

**Success Criteria**:
- No page crashes
- Error messages user-friendly
- Recovery is simple and obvious
```

---

## 💵 PART 6: Pricing Mock (UI Only)

### 6.1 Pricing Page Component

**Create**: `frontend/src/pages/Pricing.jsx`
```jsx
import React from 'react'
import { Check, X, Info } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Alert, AlertDescription } from '../components/ui/Alert'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'

export default function Pricing() {
  const plans = [
    {
      name: "Starter",
      price: "$49",
      period: "/month",
      description: "Perfect for testing and small campaigns",
      badge: "ALPHA PRICING",
      features: [
        { name: "500 emails/month", included: true },
        { name: "1 sending domain", included: true },
        { name: "AI email generation", included: true },
        { name: "Basic deliverability monitoring", included: true },
        { name: "CSV lead import", included: true },
        { name: "Email support", included: true },
        { name: "Multi-user teams", included: false },
        { name: "Advanced analytics", included: false },
        { name: "API access", included: false }
      ],
      cta: "Current Plan",
      disabled: true
    },
    {
      name: "Growth",
      price: "$149",
      period: "/month",
      description: "Scale your outreach safely",
      badge: "MOST POPULAR",
      popular: true,
      features: [
        { name: "2,500 emails/month", included: true },
        { name: "3 sending domains", included: true },
        { name: "AI email generation", included: true },
        { name: "Advanced deliverability monitoring", included: true },
        { name: "CSV lead import", included: true },
        { name: "Priority email support", included: true },
        { name: "Multi-user teams (3 seats)", included: true },
        { name: "Advanced analytics", included: true },
        { name: "API access", included: false }
      ],
      cta: "Upgrade (Coming Soon)",
      disabled: true
    },
    {
      name: "Enterprise",
      price: "$499",
      period: "/month",
      description: "For high-volume sending teams",
      badge: "BEST VALUE",
      features: [
        { name: "10,000 emails/month", included: true },
        { name: "Unlimited sending domains", included: true },
        { name: "AI email generation", included: true },
        { name: "Advanced deliverability monitoring", included: true },
        { name: "CSV lead import", included: true },
        { name: "Priority phone & email support", included: true },
        { name: "Multi-user teams (unlimited)", included: true },
        { name: "Advanced analytics", included: true },
        { name: "API access", included: true },
        { name: "Custom integrations", included: true },
        { name: "Dedicated account manager", included: true }
      ],
      cta: "Contact Us",
      disabled: true
    }
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">
          Simple, Transparent Pricing
        </h1>
        <p className="text-xl text-slate-600 mb-6">
          Choose the plan that fits your needs. Upgrade or downgrade anytime.
        </p>
        
        {/* Alpha Warning */}
        <Alert variant="warning" className="max-w-3xl mx-auto">
          <Info className="h-4 w-4" />
          <AlertDescription>
            <strong>Alpha Pricing Notice:</strong> Billing is not active during alpha phase. 
            These prices are for evaluation purposes only and subject to change before public launch.
            All alpha users will receive special early-adopter pricing when billing goes live.
          </AlertDescription>
        </Alert>
      </div>

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
        {plans.map((plan, idx) => (
          <Card 
            key={idx}
            className={`relative ${plan.popular ? 'border-2 border-blue-500 shadow-xl' : ''}`}
          >
            {plan.badge && (
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <Badge variant={plan.popular ? "primary" : "secondary"}>
                  {plan.badge}
                </Badge>
              </div>
            )}
            
            <CardHeader className="text-center pt-8">
              <CardTitle className="text-2xl mb-2">{plan.name}</CardTitle>
              <div className="mb-4">
                <span className="text-4xl font-bold text-slate-900">{plan.price}</span>
                <span className="text-slate-600">{plan.period}</span>
              </div>
              <p className="text-sm text-slate-600">{plan.description}</p>
            </CardHeader>

            <CardContent>
              <ul className="space-y-3 mb-6">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2">
                    {feature.included ? (
                      <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    ) : (
                      <X className="w-5 h-5 text-slate-300 flex-shrink-0 mt-0.5" />
                    )}
                    <span className={feature.included ? 'text-slate-700' : 'text-slate-400'}>
                      {feature.name}
                    </span>
                  </li>
                ))}
              </ul>

              <Button 
                className="w-full" 
                variant={plan.popular ? "primary" : "outline"}
                disabled={plan.disabled}
              >
                {plan.cta}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* FAQ Section */}
      <div className="max-w-3xl mx-auto">
        <h2 className="text-2xl font-bold text-slate-900 mb-6 text-center">
          Frequently Asked Questions
        </h2>
        
        <div className="space-y-4">
          <Card>
            <CardContent className="pt-6">
              <h3 className="font-semibold text-slate-900 mb-2">
                When will billing be activated?
              </h3>
              <p className="text-slate-600">
                Billing will be enabled when we move from alpha to beta. All alpha testers 
                will receive at least 30 days notice and special early-adopter pricing.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <h3 className="font-semibold text-slate-900 mb-2">
                What happens if I exceed my email limit?
              </h3>
              <p className="text-slate-600">
                We'll send you a warning at 80% usage. If you exceed your limit, you can either 
                upgrade your plan or wait until next month. We'll never auto-charge you.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <h3 className="font-semibold text-slate-900 mb-2">
                Can I cancel anytime?
              </h3>
              <p className="text-slate-600">
                Yes, absolutely. You can cancel at any time and you'll retain access until the 
                end of your billing period. No long-term commitments required.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <h3 className="font-semibold text-slate-900 mb-2">
                Do you offer refunds?
              </h3>
              <p className="text-slate-600">
                Yes, we offer a 14-day money-back guarantee. If you're not satisfied, 
                contact us within 14 days of purchase for a full refund.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
```

**Update Routes** in `frontend/src/App.jsx`:
```jsx
import Pricing from './pages/Pricing'

// Add route:
<Route path="pricing" element={<Pricing />} />
```

**Add to Navigation** in `frontend/src/components/Layout.jsx`:
```jsx
{ name: 'Pricing', href: '/pricing', icon: DollarSign }
```

---

## 🧪 PART 7: Real-World Send-Limit Testing

### 7.1 Send-Limit Test Scenarios

**Create**: `SEND_LIMIT_TESTING.md`
```markdown
# Send-Limit Testing Guide

## Test Scenario 1: Warmup Day 1-7 (Conservative Phase)

### Setup
- New user account
- Email provider connected
- 50 test leads imported

### Test Schedule
| Day | Recommended Limit | Test Send Count | Expected Behavior |
|-----|-------------------|-----------------|-------------------|
| 1   | 10 emails         | 10 emails       | No warnings |
| 1   | 10 emails         | 15 emails       | ⚠️ "Exceeded daily limit" warning |
| 3   | 20 emails         | 16 emails       | ⚠️ "Approaching limit (16/20)" |
| 5   | 30 emails         | 25 emails       | No warnings |
| 7   | 40 emails         | 42 emails       | ⚠️ "Exceeded daily limit" warning |

### Validation Steps
1. Check deliverability page shows correct daily limit
2. Verify warning appears at 80% usage (e.g., 8/10, 16/20)
3. Confirm critical alert shows when exceeded (e.g., 11/10, 21/20)
4. Ensure next day limit updates correctly
5. Verify warmup progress updates (Day X/21)

### Expected Dashboard Guidance
```
Day 1: "Start slow - Send 10 emails today to establish reputation"
Day 3: "Increase gradually - Send up to 20 emails today"
Day 7: "Halfway through warmup - Send up to 40 emails today"
Day 14: "Almost done - Send up to 70 emails today"
Day 21: "Warmup complete - You can now send up to 200 emails/day"
```

## Test Scenario 2: Rapid Sending (Stress Test)

### Setup
- User on Day 5 of warmup (30 email limit)
- Campaign with 100 leads
- Campaign activated to send immediately

### Test Steps
1. Activate campaign
2. Monitor sending progress in real-time
3. Watch for warning at email #24 (80% of 30)
4. Observe behavior at email #31 (exceeded limit)

### Expected Behavior
- ✅ Advisory warning displays but doesn't block
- ✅ User can acknowledge and continue
- ✅ Dashboard shows "31/30 - Daily limit exceeded"
- ✅ Recommendations suggest pausing until tomorrow
- ❌ System does NOT hard-stop sending (advisory mode)

### Manual Verification
- Check backend logs for send attempts
- Verify all 100 sends attempted (not blocked)
- Confirm deliverability score decreases if bounces occur
- Ensure warning persists on next page load

## Test Scenario 3: Multi-Campaign Coordination

### Setup
- User on Day 10 of warmup (50 email limit)
- Campaign A: 20 leads
- Campaign B: 30 leads
- Both activated on same day

### Test Steps
1. Activate Campaign A at 9:00 AM (20 emails sent)
2. Wait 2 hours
3. Check deliverability page (should show 20/50 used)
4. Activate Campaign B at 11:00 AM (30 emails)
5. Total: 50 emails sent (at limit)

### Expected Behavior
- Both campaigns complete successfully
- After Campaign A: "20/50 emails sent today"
- After Campaign B: "50/50 emails sent today - Daily limit reached"
- Deliverability page shows warning
- New campaign activation shows "You've reached your daily limit"

## Test Scenario 4: Bounce Rate Impact on Limits

### Setup
- User on Day 15 of warmup (75 email limit)
- Inject 10 bounce events (10% bounce rate)

### Test Steps
1. Check initial health score (should be ~85)
2. Insert bounce events via SQL script
3. Refresh deliverability page
4. Observe health score drop (should be ~65-70)
5. Check if recommended daily limit decreases

### Expected Behavior
- Health score decreases
- Bounce rate check shows "FAIL" (10% > 5% threshold)
- Warning: "High bounce rate detected"
- Recommendation: "Stop sending, clean your list"
- Daily limit advisory might suggest lower sends

## Test Scenario 5: Recovery from High Bounce Rate

### Setup
- User with 15% bounce rate (critical)
- Health score ~45
- Multiple warning messages

### Recovery Steps
1. Stop all active campaigns
2. Review bounce reasons in webhook events
3. Remove bounced emails from leads list
4. Wait 24 hours
5. Run deliverability check again
6. Start with 5 test emails to verified addresses

### Expected Behavior
- Dashboard shows "Recovery mode" guidance
- Recommends very conservative sending (5-10/day)
- Health score gradually improves as no new bounces occur
- System allows sending but with strong warnings

## Test Scenario 6: New User Experience

### Test Flow
1. Sign up as brand new user
2. Skip email provider setup
3. Try to create campaign
4. Expect: ❌ "Email provider required" blocker
5. Add email provider
6. Create campaign with 50 leads
7. Try to activate
8. Expect: ⚠️ Warning "Day 1 of warmup - Recommended limit: 10 emails"
9. Acknowledge warning
10. Campaign activates but sends only 10 emails first day

### Success Criteria
- Hard blocker for missing provider
- Soft warning for warmup limits
- Clear guidance on safe practices
- User feels informed, not frustrated

## Automated Test Script

**File**: `scripts/test_send_limits.py`
```python
#!/usr/bin/env python3
"""
Test send limit advisory system
Run from project root: python scripts/test_send_limits.py
"""
import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
TOKEN = "your_test_token_here"

headers = {"Authorization": f"Bearer {TOKEN}"}

def test_daily_limit_tracking():
    """Test 1: Verify daily limit tracking"""
    print("\n=== Test 1: Daily Limit Tracking ===")
    
    # Get current warmup status
    response = requests.get(f"{BASE_URL}/api/deliverability/warmup/status", headers=headers)
    warmup = response.json()
    
    print(f"Warmup Day: {warmup['warmup_day']}/21")
    print(f"Daily Limit: {warmup['daily_limit']}")
    print(f"Used Today: {warmup['used_today']}/{warmup['daily_limit']}")
    print(f"Status: {warmup['status']}")
    
    assert warmup['usage_percentage'] >= 0
    assert warmup['usage_percentage'] <= 100
    print("✅ Daily limit tracking works")

def test_warning_thresholds():
    """Test 2: Verify warning thresholds"""
    print("\n=== Test 2: Warning Thresholds ===")
    
    response = requests.get(f"{BASE_URL}/api/deliverability/health", headers=headers)
    health = response.json()
    
    daily_limit = health['daily_limit']
    used = daily_limit['sent']
    limit = daily_limit['limit']
    usage_pct = (used / limit * 100) if limit > 0 else 0
    
    print(f"Usage: {used}/{limit} ({usage_pct:.1f}%)")
    
    if usage_pct >= 95:
        assert len(health['warnings']) > 0, "Should have warnings at >95%"
        print("✅ Critical warning shown at >95%")
    elif usage_pct >= 80:
        assert len(health['warnings']) > 0, "Should have warnings at >80%"
        print("✅ Warning shown at >80%")
    else:
        print("✅ No warnings (usage below 80%)")

def test_health_score_accuracy():
    """Test 3: Verify health score calculation"""
    print("\n=== Test 3: Health Score Accuracy ===")
    
    response = requests.get(f"{BASE_URL}/api/deliverability/health", headers=headers)
    health = response.json()
    
    score = health['score']
    confidence = health['score_confidence']
    
    print(f"Health Score: {score}/100")
    print(f"Confidence: {confidence}")
    print(f"Status: {health['status']}")
    
    assert 0 <= score <= 100, "Score should be 0-100"
    assert health['status'] in ['good', 'warning', 'critical']
    
    if score >= 85:
        assert health['status'] == 'good'
    elif score >= 70:
        assert health['status'] == 'warning'
    else:
        assert health['status'] == 'critical'
    
    print("✅ Health score calculation accurate")

if __name__ == "__main__":
    try:
        test_daily_limit_tracking()
        test_warning_thresholds()
        test_health_score_accuracy()
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except requests.RequestException as e:
        print(f"\n❌ API error: {e}")
```

## Dashboard Messaging Examples

### Warning Messages by Scenario

**Approaching Limit (80-95%)**:
```
⚠️ Daily Limit Warning
You've sent 24 of 30 recommended emails today (80%).
Consider pausing sends until tomorrow to maintain healthy reputation.
```

**Exceeded Limit (>100%)**:
```
🚨 Daily Limit Exceeded
You've sent 35 of 30 recommended emails today (117%).
STOP sending now. Resume tomorrow with normal limit.
This is an advisory warning - sending is not blocked but strongly discouraged.
```

**First Day Guidance**:
```
👋 Welcome! You're on Day 1 of email warmup.
Start slow: Send maximum 10 emails today.
This builds trust with email providers and protects your sender reputation.
```

**High Bounce Rate**:
```
🚨 CRITICAL: High Bounce Rate Detected
15% of your emails bounced (should be <2%).
ACTION REQUIRED:
1. Stop all active campaigns immediately
2. Review bounced emails in Webhook Events
3. Remove invalid addresses from your list
4. Test with 5 verified emails before resuming
```
```

---

## Implementation Priority

### Week 1: Critical Safety Features
1. ✅ Error boundary component
2. ✅ Empty state screens
3. ✅ Email provider validation
4. ✅ Backend exception handling
5. ✅ Loading states standardization

### Week 2: Onboarding & UX Polish
1. ⏳ Onboarding wizard
2. ⏳ Validation improvements
3. ⏳ Micro-copy updates
4. ⏳ Debounce & duplicate prevention

### Week 3: Documentation & Testing
1. ⏳ README updates
2. ⏳ QA checklist
3. ⏳ Manual test flows
4. ⏳ Automated test scripts

### Week 4: Final Polish
1. ⏳ Pricing page
2. ⏳ Send-limit testing
3. ⏳ Bug fixes from testing
4. ⏳ Alpha release candidate

---

## Success Metrics

### Alpha Launch is Ready When:
- [ ] New user can complete onboarding in <5 minutes
- [ ] No crashes during normal usage for 7 days
- [ ] All critical warnings display correctly
- [ ] Deliverability monitoring shows accurate data
- [ ] Documentation is complete and honest
- [ ] QA checklist 100% passed
- [ ] 5+ alpha testers complete full workflow successfully

### NOT Required for Alpha:
- ❌ Billing integration
- ❌ Multi-tenant features
- ❌ Performance optimization
- ❌ Scalability testing
- ❌ Marketing website
- ❌ Customer support system

