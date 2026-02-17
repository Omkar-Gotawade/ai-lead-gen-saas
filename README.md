# AI Lead Generation + Outreach SaaS

**⚠️ ALPHA RELEASE - Safety First**

This is an **ALPHA release** for controlled testing. Not recommended for production use.

> **🛡️ IMPORTANT**: This platform handles cold email outreach. Misuse can damage your sender reputation permanently. Follow all safety guidelines carefully.

## 📋 Quick Start (3 Minutes)

1. **Start the application**:
   ```bash
   docker-compose up -d
   ```

2. **Access the app**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

3. **Complete onboarding**:
   - Sign up at http://localhost:3000/signup
   - Configure email provider in Settings
   - Import leads from CSV
   - Create your first campaign

## ⚠️ Known Limitations (Alpha)

- **Warmup guidance is advisory only** - Not enforced by system
- **Daily send limits are recommendations** - You must self-monitor
- **Webhook events require manual SendGrid configuration**
- **Blacklist monitoring not implemented** - Use external tools (MXToolbox)
- **No billing integration** - Pricing is informational only
- **Bounce/spam tracking requires webhook setup** - See `SENDGRID_WEBHOOK_SETUP.md`

## 🛡️ Safe Usage Guidelines

### Critical Safety Rules
1. **Never use your primary work email** for cold outreach
2. **Start with 5-10 emails/day** for the first week
3. **Monitor deliverability page daily** - Watch bounce/spam rates
4. **Stop immediately if bounce rate > 5%** or spam rate > 0.1%
5. **Clean your lists** - Remove bounces immediately
6. **Personalize every email** - Generic blasts harm reputation

### Email Warmup (21 Days Recommended)
| Week | Daily Limit | Focus |
|------|-------------|-------|
| 1 | 10-20 emails | Establish baseline reputation |
| 2 | 30-50 emails | Gradual volume increase |
| 3 | 70-100 emails | Near-full capacity |

**⚠️ Exceeding warmup limits risks permanent reputation damage**

## 🚀 Features

### Week 0 - Project Setup
- ✅ FastAPI backend with modular architecture
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ Alembic migrations for database schema management
- ✅ Redis for caching and message broker
- ✅ Celery for background job processing
- ✅ React + Vite frontend with TailwindCSS
- ✅ Docker & Docker Compose for containerization
- ✅ JWT authentication

### Week 1 - Core Features
- ✅ **Authentication System**
  - User registration with email/password
  - JWT token-based authentication
  - Protected routes and API endpoints
  - Login/Signup pages

- ✅ **Lead Management (CRUD)**
  - Create, Read, Update, Delete leads
  - Paginated lead listing
  - Lead model with enrichment data support
  - Clean UI with TailwindCSS components

- ✅ **CSV Upload**
  - Bulk lead import via CSV
  - CSV validation and parsing
  - Error handling for malformed data

- ✅ **Background Jobs**
  - Celery worker for async tasks
  - Lead enrichment job (placeholder for API integration)
  - Job status tracking

### Week 2 - AI Generation + Email Sending
- ✅ **AI Email Generation**
  - OpenAI GPT-3.5-turbo integration
  - Generate personalized emails from lead data
  - Customizable tone (professional, friendly, casual)
  - Goal-oriented email copy (introduce, follow-up, meeting)
  - Email composer UI with preview and editing

- ✅ **Email Provider Integration**
  - SMTP support with encrypted credentials
  - SendGrid API integration
  - Provider configuration and testing
  - Secure credential storage with Fernet encryption

- ✅ **Automated Email Sending**
  - Celery-based background email sending
  - Send logs with delivery status tracking
  - Test email functionality
  - Template-based emails with placeholders

- ✅ **Campaign Management**
  - Multi-step email sequences
  - Configurable delays between steps
  - Campaign status management (draft, active, paused, completed)
  - Template placeholders: {{first_name}}, {{last_name}}, {{company}}, {{title}}
  - Bulk lead enrollment to campaigns
  - Automatic sequence execution via Celery
  - Campaign lead status tracking

## 📁 Project Structure

```
lead gen/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── workers/         # Celery tasks
│   │   ├── config.py        # App configuration
│   │   └── database.py      # Database setup
│   ├── alembic/             # Database migrations
│   ├── main.py              # FastAPI app entry point
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/             # API client
│   │   ├── components/      # React components
│   │   ├── context/         # React context (Auth)
│   │   ├── pages/           # Page components
│   │   ├── App.jsx          # Main App component
│   │   └── main.jsx         # Entry point
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migration tool
- **Redis** - In-memory data store
- **Celery** - Distributed task queue
- **Pydantic** - Data validation
- **PyJWT** - JWT token handling
- **Passlib** - Password hashing
- **OpenAI** - GPT-3.5-turbo for email generation
- **SendGrid** - Email delivery service
- **Cryptography** - Secure credential encryption

### Frontend
- **React 18** - UI library
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## 🚀 Getting Started

### Prerequisites
- Docker Desktop installed
- Git
- OpenAI API key (for AI email generation)
- SMTP credentials OR SendGrid API key (for email sending)

### Installation & Setup

1. **Clone or navigate to the project directory**
   ```powershell
   cd "d:\lead gen"
   ```

2. **Configure environment variables**
   
   The application requires several environment variables. Edit `docker-compose.yml` and add these to the `backend` service:
   
   ```yaml
   environment:
     # Existing variables
     - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/leadgen_db
     - REDIS_URL=redis://redis:6379/0
     - SECRET_KEY=your-secret-key-change-this-in-production
     - ALGORITHM=HS256
     - ACCESS_TOKEN_EXPIRE_MINUTES=30
     - BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
     
     # Week 2: AI & Email Configuration
     - OPENAI_API_KEY=sk-your-openai-api-key-here
     - OPENAI_MODEL=gpt-3.5-turbo
     - ENCRYPTION_KEY=your-32-byte-base64-encryption-key
   ```
   
   **Important:** Also add these same environment variables to the `celery-worker` service in `docker-compose.yml`

   **Getting your keys:**
   - **OpenAI API Key**: Get from https://platform.openai.com/api-keys
   - **Encryption Key**: Generate with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
   - **SendGrid API Key** (optional): Get from https://app.sendgrid.com/settings/api_keys

3. **Build and start all services**
   ```powershell
   docker-compose up --build
   ```

   This will start:
   - PostgreSQL (port 5432)
   - Redis (port 6379)
   - Backend API (port 8000)
   - Celery Worker
   - Frontend (port 5173)

4. **Run database migrations**
   
   In a new terminal:
   ```powershell
   docker exec leadgen_backend alembic upgrade head
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📝 Usage

### 1. Create an Account
- Navigate to http://localhost:5173
- Click "Sign up" and create an account
- Login with your credentials

### 2. Configure Email Provider (Required for sending emails)

**Option A: SMTP Configuration**
1. Navigate to the "Settings" or use the email composer
2. Choose "SMTP" as provider
3. Enter your SMTP details:
   - Host: e.g., smtp.gmail.com
   - Port: 587 (TLS) or 465 (SSL)
   - Username: your email address
   - Password: your email password or app-specific password
4. Click "Test Connection" to verify

**Option B: SendGrid Configuration**
1. Get your SendGrid API key from https://app.sendgrid.com
2. Choose "SendGrid" as provider
3. Enter your API key and sender email
4. Click "Test Connection" to verify

### 3. Manage Leads

**Create a Lead Manually:**
- Click "Add lead" button
- Fill in the form (first name, last name, email, company, title)
- Click "Create"

**Upload CSV:**
- Click "Upload CSV" button
- Select a CSV file with columns: `first_name`, `last_name`, `email`, `company`, `title`
- The leads will be bulk imported

**Edit/Delete Leads:**
- Click "Edit" or "Delete" on any lead row

**Enrich a Lead:**
- Click "Enrich" on any lead row
- The enrichment job will run in the background

### 4. AI Email Generation

**Compose Email for a Single Lead:**
1. Click "Compose" on any lead row
2. Select tone (professional, friendly, casual)
3. Select goal (introduce, follow-up, meeting)
4. Enter your product/service description
5. Click "Generate Email" - AI will create personalized copy
6. Edit the subject and body if needed
7. Click "Send Test" to send to yourself, or use it in a campaign

### 5. Create Email Campaigns

**Set up a Multi-Step Sequence:**
1. Go to "Campaigns" page
2. Click "Create New Campaign"
3. Enter campaign name and description
4. Click "Create Campaign"
5. Click "Edit Sequence" on the campaign

**Add Sequence Steps:**
1. Click "Add Step"
2. Configure step details:
   - Step Index: Order of the email (1, 2, 3...)
   - Delay: Days to wait after previous step (0 = immediate)
   - Subject Template: Email subject (use {{placeholders}})
   - Body Template: Email body (use {{placeholders}})
3. Available placeholders:
   - `{{first_name}}` - Lead's first name
   - `{{last_name}}` - Lead's last name
   - `{{company}}` - Lead's company
   - `{{title}}` - Lead's job title
4. Click "Add Step" to save

**Example 3-Step Sequence:**
- **Step 1** (Delay: 0 days): Introduction email
- **Step 2** (Delay: 3 days): Follow-up with value proposition
- **Step 3** (Delay: 7 days): Meeting request

### 6. Enroll Leads in Campaign

1. Go to "Leads" page
2. Use checkboxes to select leads
3. Click "Add X to Campaign" button
4. Select your campaign from the dropdown
5. Click "Add to Campaign"
6. The first email will be sent immediately (or after configured delay)
7. Subsequent emails will be sent automatically after the specified delays

### 7. Monitor Campaign Progress

- Campaign leads are tracked with statuses: `queued`, `in_progress`, `completed`, `stopped`
- Check sending logs for delivery status
- Change campaign status to pause/resume sequences

### 3. CSV Format

Create a CSV file with the following format:

```csv
first_name,last_name,email,company,title
John,Doe,john.doe@example.com,Acme Corp,CEO
Jane,Smith,jane.smith@example.com,Tech Inc,CTO
Bob,Johnson,bob@startup.io,Startup Inc,Founder
```

**Note:** The `title` field is optional but recommended for better email personalization.

## 🔧 Development

### Backend Development

**Run backend without Docker:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

**Run Celery worker:**
```powershell
celery -A app.celery_app worker --loglevel=info
```

**Create new migration:**
```powershell
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Frontend Development

**Run frontend without Docker:**
```powershell
cd frontend
npm install
npm run dev
```

## 🧪 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### Leads
- `GET /api/leads` - List all leads (paginated)
- `POST /api/leads` - Create new lead
- `GET /api/leads/{id}` - Get single lead
- `PUT /api/leads/{id}` - Update lead
- `DELETE /api/leads/{id}` - Delete lead
- `POST /api/leads/upload-csv` - Upload CSV file
- `POST /api/leads/{id}/enrich` - Enqueue enrichment job

### AI Email Generation
- `POST /api/generate-email` - Generate AI email for a lead
  - Body: `{ "lead_id": "uuid", "tone": "professional", "goal": "introduce", "product_description": "..." }`

### Email Provider
- `POST /api/email-provider/connect` - Configure SMTP or SendGrid
- `POST /api/email-provider/test` - Test email provider connection
- `GET /api/email-provider/settings` - Get current provider settings

### Email Sending
- `POST /api/send-email` - Send email to a lead
- `GET /api/sending-logs` - Get sending history with status

### Campaigns
- `GET /api/campaigns` - List all campaigns
- `POST /api/campaigns` - Create new campaign
- `GET /api/campaigns/{id}` - Get campaign details
- `PUT /api/campaigns/{id}` - Update campaign
- `DELETE /api/campaigns/{id}` - Delete campaign
- `POST /api/campaigns/{id}/enqueue` - Enroll leads in campaign sequence

### Sequence Steps
- `GET /api/sequence-steps/{campaign_id}` - Get all steps for a campaign
- `POST /api/sequence-steps` - Create new sequence step
- `PUT /api/sequence-steps/{id}` - Update sequence step
- `DELETE /api/sequence-steps/{id}` - Delete sequence step

## 📦 Database Schema

### Users Table
- `id` (UUID) - Primary key
- `email` (String) - Unique email address
- `hashed_password` (String) - Bcrypt hashed password
- `created_at` (DateTime) - Account creation timestamp

### Leads Table
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to users
- `first_name` (String) - Lead's first name
- `last_name` (String) - Lead's last name
- `full_name` (String) - Computed full name
- `email` (String) - Lead's email address
- `company` (String) - Lead's company
- `title` (String) - Lead's job title
- `source` (String) - Lead source (manual, csv_upload, api)
- `enriched_data` (JSONB) - Enrichment data from external APIs
- `created_at` (DateTime) - Lead creation timestamp

### Email Provider Settings Table
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to users
- `provider_type` (String) - 'smtp' or 'sendgrid'
- `smtp_host` (String) - SMTP server host
- `smtp_port` (Integer) - SMTP server port
- `smtp_username` (String) - SMTP username
- `smtp_password_encrypted` (String) - Encrypted SMTP password
- `sendgrid_api_key_encrypted` (String) - Encrypted SendGrid API key
- `sender_email` (String) - From email address
- `sender_name` (String) - From name
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Sending Logs Table
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to users
- `lead_id` (UUID) - Foreign key to leads
- `recipient_email` (String) - Email recipient
- `subject` (String) - Email subject
- `body` (Text) - Email body
- `status` (String) - 'sent', 'failed', 'pending'
- `error_message` (String) - Error details if failed
- `sent_at` (DateTime) - When email was sent

### Campaigns Table
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to users
- `name` (String) - Campaign name
- `description` (String) - Campaign description
- `status` (String) - 'draft', 'active', 'paused', 'completed'
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Sequence Steps Table
- `id` (UUID) - Primary key
- `campaign_id` (UUID) - Foreign key to campaigns
- `step_index` (Integer) - Order of step in sequence
- `subject_template` (String) - Email subject with placeholders
- `body_template` (Text) - Email body with placeholders
- `delay_days` (Integer) - Days to wait after previous step
- `created_at` (DateTime)

### Campaign Leads Table
- `id` (UUID) - Primary key
- `campaign_id` (UUID) - Foreign key to campaigns
- `lead_id` (UUID) - Foreign key to leads
- `status` (String) - 'queued', 'in_progress', 'completed', 'stopped'
- `last_step_index` (Integer) - Last completed step
- `created_at` (DateTime)
- `updated_at` (DateTime)

## 🔐 Security

- Passwords are hashed using bcrypt
- JWT tokens for stateless authentication
- CORS configured for frontend origin
- Email provider credentials encrypted with Fernet (symmetric encryption)
- Environment variables for sensitive data (API keys, secrets)
- Protected API routes require valid JWT token
- SQL injection protection via SQLAlchemy ORM

## 🐛 Troubleshooting

### "Email provider not configured"
**Problem**: Cannot create campaigns  
**Solution**:
1. Go to Settings → Email Provider
2. Add your SendGrid API key or SMTP credentials
3. Click "Test Connection" to verify
4. Try creating campaign again

### High bounce rate (> 5%)
**Problem**: Deliverability page shows red alert  
**Solution**:
1. **STOP all active campaigns immediately**
2. Go to Webhook Events page
3. Review bounce reasons
4. Remove bounced email addresses from your leads list
5. Use email verification service before next send
6. Resume with 5-10 verified emails per day

### "No events in webhook page"
**Problem**: Webhook events showing zero  
**Solution**:
1. Follow `SENDGRID_WEBHOOK_SETUP.md` guide
2. Use ngrok to expose local server: `ngrok http 8000`
3. Configure webhook URL in SendGrid dashboard
4. Send test email to trigger events

### Backend won't start
- Check if `OPENAI_API_KEY` or `GEMINI_API_KEY` is set in docker-compose.yml
- Verify `ENCRYPTION_KEY` is set
- Run `docker-compose logs backend` to see error messages
- Ensure PostgreSQL is running: `docker ps | grep postgres`

### Celery worker errors
- Ensure celery-worker has the same environment variables as backend
- Check logs: `docker logs leadgen_celery_worker`
- Verify Redis is running: `docker ps | grep redis`
- Restart worker: `docker-compose restart celery-worker`

### Email sending fails
- Test credentials using "Test Connection" button in Settings
- Check sending logs: `docker exec leadgen_postgres psql -U postgres -d leadgen_db -c "SELECT * FROM sending_logs ORDER BY created_at DESC LIMIT 10"`
- Verify sender email is authorized in your email provider
- Check daily send limits haven't been exceeded

### Migrations fail
- Check current version: `docker exec leadgen_backend alembic current`
- View migration history: `docker exec leadgen_backend alembic history`
- Apply pending migrations: `docker exec leadgen_backend alembic upgrade head`
- If corrupted, stamp and retry: `docker exec leadgen_backend alembic stamp head`

### Frontend can't connect to backend
- Verify backend is running: `docker ps`
- Check backend health: http://localhost:8000/docs
- Check CORS origins in docker-compose.yml include `http://localhost:3000`
- Clear browser cache (Ctrl+Shift+R)
- Check browser console for errors (F12)

### Campaign not sending emails
- Check campaign status is "active"
- Verify daily limit not exceeded (Deliverability page)
- Check Celery worker is running: `docker ps | grep celery`
- View worker logs: `docker logs leadgen_celery_worker --tail 50`
- Ensure leads have valid email addresses

### Docker containers won't start
- Check port conflicts: `netstat -ano | findstr :8000`
- Remove old containers: `docker-compose down -v`
- Rebuild: `docker-compose up --build`
- Check disk space: `docker system df`
- Prune unused data: `docker system prune`

## 📚 Additional Documentation

- **`SENDGRID_WEBHOOK_SETUP.md`** - Configure webhooks for bounce/spam tracking
- **`ALPHA_LAUNCH_PLAN.md`** - Complete alpha launch readiness plan
- **`QA_CHECKLIST.md`** - Testing procedures and validation
- **`COMPLETION_REPORT.md`** - Feature completion status
- **`API_REFERENCE.md`** - Detailed API endpoint documentation

## ⚠️ Alpha Testing Guidelines

### What to Test
- ✅ Complete new user onboarding flow
- ✅ Import leads and create campaigns
- ✅ AI email generation quality
- ✅ Email sending with small volumes (5-10/day)
- ✅ Deliverability monitoring accuracy
- ✅ Warmup limit warnings

### What NOT to Test
- ❌ High-volume sending (>100 emails/day)
- ❌ Production email lists
- ❌ Real customer outreach (use test accounts)
- ❌ Billing/payment flows (not implemented)

### Reporting Issues
When you find a bug, include:
1. Steps to reproduce
2. Expected vs actual behavior
3. Browser console errors (F12)
4. Backend logs if applicable
5. Screenshots/recordings if helpful

## 🎯 Roadmap

### Beta Phase (Next)
- ✅ Automatic send throttling
- ✅ Enhanced blacklist monitoring
- ✅ Email open/click tracking
- ✅ A/B testing for subject lines
- ✅ Automatic list cleaning

### v1.0 (Future)
- Multi-user organizations
- Billing integration
- Advanced analytics
- Zapier/webhook integrations
- Mobile app

## 🔐 Security

- Passwords hashed using bcrypt
- JWT tokens for stateless authentication
- CORS configured for frontend origin
- Email provider credentials encrypted with Fernet
- Environment variables for sensitive data
- Protected API routes require valid JWT
- SQL injection protection via SQLAlchemy ORM
- Rate limiting on authentication endpoints

**⚠️ Security Note**: This is an alpha release. Do not use in production without additional security hardening.
