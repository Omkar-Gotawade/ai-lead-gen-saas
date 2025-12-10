# Google Gemini API Setup Guide

## Overview
The lead generation system now uses **Google Gemini** instead of OpenAI for AI-powered email generation.

## Package Changes
- **Removed**: `openai==1.3.0`
- **Added**: `google-generativeai==0.3.2`

## Configuration Changes

### Environment Variables
Replace OpenAI credentials with Gemini in `docker-compose.yml`:

```yaml
environment:
  - GEMINI_API_KEY=your-gemini-api-key-here
  - GEMINI_MODEL=gemini-pro
  - ENCRYPTION_KEY=qWU_C0llov5ZH0vuDMJ3YMpzjZAdkVBN-cLcseb0J5M=
```

### Getting a Gemini API Key
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and replace `your-gemini-api-key-here` in `docker-compose.yml`

## Code Changes

### app/config.py
```python
# Old
OPENAI_API_KEY: str = ""
OPENAI_MODEL: str = "gpt-3.5-turbo"

# New
GEMINI_API_KEY: str = ""
GEMINI_MODEL: str = "gemini-pro"
```

### app/services/ai_email_service.py
```python
# Old
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# New
import google.generativeai as genai
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)
```

## API Usage Differences

### OpenAI (Old)
```python
response = await client.chat.completions.create(
    model=settings.OPENAI_MODEL,
    messages=[
        {"role": "system", "content": "..."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=500
)
content = response.choices[0].message.content
```

### Gemini (New)
```python
response = model.generate_content(prompt)
content = response.text.strip()
```

## Testing

### Test Email Generation
1. Login to the system: http://localhost:5173
2. Navigate to "Leads" page
3. Click on any lead → "Generate Email"
4. Select tone and goal
5. Click "Generate" - should use Gemini API

### Expected Behavior
- Email subject and body generated using Gemini Pro model
- Response format: `SUBJECT: ... --- [email body]`
- Same quality as OpenAI but potentially faster/cheaper

## Cost Comparison

### OpenAI GPT-3.5-turbo
- $0.0005 per 1K input tokens
- $0.0015 per 1K output tokens

### Google Gemini Pro
- **FREE** up to 60 requests/minute
- No cost for standard usage
- Rate limits: 60 RPM, 1 million TPM (tokens per minute)

## Troubleshooting

### "GEMINI_API_KEY not configured"
- Verify the API key is set in `docker-compose.yml`
- Restart containers: `docker-compose restart backend celery-worker`

### Import Error
```bash
# Rebuild containers to install google-generativeai
docker-compose down
docker-compose up --build -d
```

### Rate Limit Exceeded
- Free tier: 60 requests/minute
- Wait 60 seconds or upgrade to paid tier
- Check quota: https://console.cloud.google.com/apis/dashboard

## Migration Checklist
- [x] Updated `requirements.txt` with `google-generativeai==0.3.2`
- [x] Modified `app/config.py` with Gemini settings
- [x] Rewrote `app/services/ai_email_service.py` for Gemini API
- [x] Updated `docker-compose.yml` environment variables
- [x] Rebuilt Docker containers
- [ ] Add your Gemini API key to `docker-compose.yml`
- [ ] Test email generation with real leads
- [ ] Monitor rate limits in production

## Next Steps
1. Get your Gemini API key from https://makersuite.google.com/app/apikey
2. Replace `your-gemini-api-key-here` in `docker-compose.yml`
3. Restart services: `docker-compose restart backend celery-worker`
4. Test email generation in the UI

## Support
- Gemini API Docs: https://ai.google.dev/docs
- Rate Limits: https://ai.google.dev/pricing
- API Key Management: https://makersuite.google.com/app/apikey
