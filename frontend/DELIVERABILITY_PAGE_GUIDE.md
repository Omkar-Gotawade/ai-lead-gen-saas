# 🛡️ Deliverability Page - User Guide

**Page Location:** Frontend → `/deliverability`  
**Purpose:** Monitor email health, check warmup status, and improve deliverability

---

## 📊 What You'll See

### 1. Overall Health Score (Left Card)
Shows your email deliverability health from 0-100:

- **80-100** = 🟢 Good (green)
- **60-79** = 🟡 Warning (yellow)
- **0-59** = 🔴 Critical (red)

**Below the score:**
- Daily send limit usage (progress bar)
- Current: 45/50 emails sent
- Next day's limit forecast

**Auto-Fix Button:** Attempts to automatically fix common issues

---

### 2. System Checks (Top Right)
Real-time checks of your email infrastructure:

#### ✅ Pass Status Checks:
- **Domain Auth** - SPF/DKIM/DMARC configured correctly
- **Blacklist** - Not on any spam blacklists

#### ⚠️ Warning Status:
- **Warmup** - "Day 5 of 14" - warmup in progress
- **Bounce Rate** - "4% bounce rate (target: <2%)"

#### ❌ Fail Status:
- Critical issues that need immediate attention

---

### 3. Recommendations (Bottom Left)
Actionable advice to improve deliverability:

- 📌 "Reduce sending speed to avoid spam triggers"
- 📌 "Clean 12 invalid email addresses from your list"
- 📌 "Avoid using spam trigger words in subject lines"

**These are prioritized actions you should take.**

---

### 4. Spam Triggers (Bottom Right)
Issues detected in your recent emails:

- 🔴 **High Severity**
  - "Used word 'free' 5 times"
  - "No unsubscribe link in 3 recent emails"

- 🟡 **Medium Severity**
  - "Short email body (< 50 words)"

**Fix these to improve inbox placement.**

---

## 🎯 How to Use This Page

### Daily Workflow

**1. Morning Check (5 minutes)**
```
✓ Check health score - aim for 80+
✓ Review daily limit usage
✓ Look for new warnings
```

**2. Before Launching Campaigns**
```
✓ Verify all checks are "pass" or "warning"
✓ Ensure you have remaining capacity
✓ Review any new spam triggers
✓ Fix critical issues first
```

**3. After Campaign Sends**
```
✓ Monitor bounce rate changes
✓ Check if limits were respected
✓ Review any new recommendations
```

---

## 🚀 Quick Actions

### Refresh Analysis
**Button:** Top right corner (🔄 icon)  
**When to use:** After making changes, before campaigns, or if data looks stale

### Auto-Fix Issues
**Button:** Bottom of health score card (⚡ icon)  
**What it does:**
- Removes invalid emails from lists
- Adjusts sending speed
- Fixes common configuration issues
- Updates warmup schedules

**When to use:**
- Health score drops below 70
- Multiple warnings appear
- Before important campaigns

---

## 📈 Understanding Your Status

### Health Score Breakdown

**Score Components:**
- Domain authentication (SPF/DKIM/DMARC): 30%
- Bounce rate: 25%
- Spam complaint rate: 20%
- Blacklist status: 15%
- Warmup progress: 10%

### Daily Limit Progression

**Example:**
```
Current:  45 / 50 sent today (90% used)
Status:   ⚠️ Approaching limit
Advice:   Pause campaigns or wait for tomorrow

Tomorrow: 55 limit (warmup day 6)
```

**Color Coding:**
- 🟢 0-70% used: Safe to send
- 🟡 70-90% used: Approaching limit
- 🔴 90-100% used: Stop sending
- ⛔ 100%+ used: Blocked (429 errors)

---

## ⚠️ Warning Signs

### 🔴 Critical Issues (Act Immediately)
- Health score below 60
- Multiple "fail" status checks
- Bounce rate above 5%
- Blacklist detection
- Daily limit exceeded

**Action:** Stop all campaigns, click Auto-Fix, review issues

### 🟡 Warning Issues (Fix Soon)
- Health score 60-79
- Single "warning" status check
- Bounce rate 2-5%
- Warmup behind schedule
- 90%+ of daily limit used

**Action:** Review recommendations, reduce send volume

### 🟢 Healthy Status
- Health score 80+
- All checks "pass"
- Bounce rate below 2%
- Within daily limits
- Warmup on track

**Action:** Continue normal operations

---

## 🛠️ Troubleshooting

### "Health score won't improve"
**Check:**
1. Have you implemented all recommendations?
2. Is your email list clean?
3. Are you respecting warmup limits?
4. Have you checked DNS records?

**Fix:** Click Auto-Fix, wait 24 hours, check again

### "Warmup stuck at same day"
**Reason:** Requires daily sending to progress  
**Fix:** Send emails consistently every day

### "Daily limit not increasing"
**Reason:** Warmup schedule is conservative  
**Progression:**
- Days 1-7: Increase by 5/day
- Days 8+: Increase by 10/day
- Cap at 200/day

### "All checks failing after setup"
**Reason:** DNS records not propagated yet  
**Wait:** 24-48 hours for DNS propagation  
**Then:** Click "Refresh Analysis"

---

## 📋 Best Practices

### Daily Routine
1. **Morning:** Check health score and limits
2. **Before campaigns:** Verify status is green/yellow
3. **After sending:** Monitor for warnings
4. **Evening:** Review day's performance

### Warmup Phase (First 21 days)
- ✅ Send every day consistently
- ✅ Stay within daily limits
- ✅ Monitor bounce rates closely
- ✅ Avoid spam trigger words
- ❌ Don't skip days
- ❌ Don't exceed limits

### Maintenance Phase (After warmup)
- ✅ Check weekly (minimum)
- ✅ Address warnings within 24 hours
- ✅ Keep bounce rate below 2%
- ✅ Update DNS if domains change

---

## 🔧 Current API Endpoints

**Note:** As of Dec 29, 2025, the page uses mock data because the backend endpoint is not fully implemented.

### What Works:
- ✅ `GET /api/deliverability/warmup/status` - Returns quota info
- ✅ Overall page layout and UI
- ✅ Refresh button functionality
- ✅ Auto-fix button (UI only)

### What's Mock Data:
- ⏳ Health score calculation
- ⏳ System checks (domain auth, blacklist)
- ⏳ Recommendations engine
- ⏳ Spam trigger detection

### To Implement Full Functionality:
```javascript
// Backend needs:
GET /api/deliverability/health
Response: {
  score: 85,
  status: 'good',
  checks: {
    domain_auth: { status: 'pass', message: '...' },
    warmup: { status: 'warning', message: '...' },
    blacklist: { status: 'pass', message: '...' },
    bounce_rate: { status: 'warning', message: '...' }
  },
  daily_limit: { sent: 45, limit: 50, next_limit: 55 },
  recommendations: ['...'],
  spam_reasons: [{ reason: '...', severity: 'high' }]
}
```

---

## 🎨 UI Components

### Score Display
- Large circular badge with number
- Color-coded (green/yellow/red)
- Status badge below

### Progress Bars
- Visual representation of limit usage
- Updates in real-time
- Color changes at thresholds

### Check Status Icons
- ✅ Green checkmark = Pass
- ⚠️ Yellow warning = Warning
- ❌ Red X = Fail

### Action Buttons
- **Refresh:** Updates all data
- **Auto-Fix:** Runs automated fixes
- Both show loading states

---

## 📱 Responsive Design

**Desktop (>1024px):**
- 3-column layout
- All cards visible
- Full recommendations

**Tablet (768-1024px):**
- 2-column layout
- Stacked cards

**Mobile (<768px):**
- Single column
- Scrollable sections
- Condensed info

---

## 🔗 Related Pages

- **Settings** → Configure email providers (SMTP/SendGrid)
- **Campaigns** → View impact of deliverability on campaigns
- **Leads** → Clean list to improve health score
- **Webhooks Debug** → Monitor delivery events

---

## 💡 Pro Tips

1. **Check before big sends:** Always verify health score 80+ before launching important campaigns

2. **Monitor trends:** Visit daily during warmup phase, weekly after

3. **Act on warnings quickly:** Small issues become big problems if ignored

4. **Keep lists clean:** Remove bounces immediately to protect score

5. **Respect limits:** Better to send tomorrow than burn your domain today

6. **DNS first:** Fix domain authentication before anything else

7. **Warmup patience:** Don't rush - 21 days protects your reputation

8. **Document changes:** Note what you fix to track improvements

---

## ❓ FAQ

**Q: How often should I check this page?**  
A: Daily during warmup (21 days), 2-3x/week after

**Q: What's a good health score?**  
A: 80+ is excellent, 70-79 is acceptable, below 70 needs attention

**Q: Can I send if score is below 80?**  
A: Yes, but fix issues first and send cautiously

**Q: How long does Auto-Fix take?**  
A: 10-30 seconds, but improvements may take 24-48 hours to show

**Q: Why is my warmup progressing slowly?**  
A: By design - protects your domain reputation

**Q: What happens if I exceed daily limit?**  
A: Sends will be blocked (HTTP 429), resume tomorrow

**Q: Can I increase daily limit faster?**  
A: No - warmup schedule is optimized for deliverability

**Q: What if all checks fail?**  
A: Contact support, check DNS settings, verify email provider

---

**Version:** 1.0  
**Last Updated:** December 29, 2025  
**Status:** UI Complete, Backend Partially Implemented
