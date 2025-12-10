# Quick Start Guide

## Prerequisites

1. **Docker Desktop** - Must be running before starting the application
2. **OpenAI API Key** - Get from https://platform.openai.com/api-keys
3. **SMTP or SendGrid credentials** - For sending emails
4. **Git** (optional) - For version control

## Initial Setup (First Time Only)

### 1. Configure Environment Variables

Edit `docker-compose.yml` and add these environment variables to both `backend` and `celery-worker` services:

```yaml
environment:
  # Required for Week 2 features
  - OPENAI_API_KEY=sk-your-actual-openai-api-key-here
  - OPENAI_MODEL=gpt-3.5-turbo
  - ENCRYPTION_KEY=your-encryption-key-here
```

**Generate Encryption Key:**
```powershell
docker run --rm python:3.10-slim python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Or if you have Python installed locally:
```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Starting the Application

### Option 1: PowerShell Script (Recommended)
```powershell
.\start.ps1
```

### Option 2: Manual Commands
```powershell
# 1. Start services
docker-compose up -d

# 2. Wait for services to be ready (30 seconds)
Start-Sleep -Seconds 30

# 3. Run database migrations
docker exec leadgen_backend alembic upgrade head

# 4. Check status
docker ps
```

## First-Time Usage

### 1. Create Account
1. Open http://localhost:5173
2. Click "Sign up"
3. Enter email and password
4. Click "Create Account"

### 2. Configure Email Provider

**For Gmail SMTP:**
1. Enable 2FA on your Google account
2. Create an App Password: https://myaccount.google.com/apppasswords
3. In the app, configure SMTP:
   - Host: smtp.gmail.com
   - Port: 587
   - Username: your-email@gmail.com
   - Password: your-app-password

**For SendGrid:**
1. Get API key from https://app.sendgrid.com/settings/api_keys
2. Configure in the app:
   - Provider: SendGrid
   - API Key: your-sendgrid-api-key
   - Sender Email: verified-sender@yourdomain.com

### 3. Upload Sample Leads
Use the provided `sample_leads.csv` or create your own:
```csv
first_name,last_name,email,company,title
John,Doe,john@example.com,Acme Corp,CEO
Jane,Smith,jane@example.com,Tech Inc,CTO
```

### 4. Test AI Email Generation
1. Click "Compose" on any lead
2. Select tone and goal
3. Enter product description
4. Click "Generate Email"
5. Review and edit if needed
6. Click "Send Test" to test

### 5. Create Your First Campaign
1. Go to "Campaigns" tab
2. Create a new campaign
3. Click "Edit Sequence"
4. Add 2-3 steps with delays
5. Go to "Leads" tab
6. Select leads with checkboxes
7. Click "Add to Campaign"
8. Watch emails send automatically!

## Accessing the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432 (postgres/postgres)
- **Redis**: localhost:6379

## Stopping the Application

```powershell
docker-compose down
```

## Troubleshooting

### Docker Desktop Not Running
**Error**: `request returned Internal Server Error`

**Solution**: 
1. Open Docker Desktop
2. Wait for it to fully start (whale icon in system tray should be steady)
3. Run `docker ps` to verify it's working
4. Try starting the application again

### Backend Container Crashing
**Symptoms**: Backend keeps restarting

**Solutions**:
1. Check environment variables are set:
   ```powershell
   docker exec leadgen_backend env | Select-String "OPENAI_API_KEY"
   ```
2. View error logs:
   ```powershell
   docker logs leadgen_backend --tail 50
   ```
3. Verify OPENAI_API_KEY is valid (starts with `sk-`)

### Celery Worker Not Processing Tasks
**Symptoms**: Emails not sending, campaigns not running

**Solutions**:
1. Check worker is running:
   ```powershell
   docker ps | Select-String "celery"
   ```
2. View worker logs:
   ```powershell
   docker logs leadgen_celery_worker --tail 30
   ```
3. Verify tasks are registered (should see: enrich_lead, send_email_task, run_sequence_step)
4. Restart worker:
   ```powershell
   docker restart leadgen_celery_worker
   ```

### Email Sending Fails
**Symptoms**: Status shows "failed" in sending logs

**Solutions**:
1. Test your email provider configuration
2. For Gmail: Ensure you're using an App Password, not your regular password
3. For SendGrid: Verify API key has "Mail Send" permission
4. Check sender email is verified with your provider

### Migration Errors
**Error**: `DuplicateTable` or migration conflicts

**Solutions**:
1. Check current migration:
   ```powershell
   docker exec leadgen_backend alembic current
   ```
2. If tables exist but migrations aren't tracked:
   ```powershell
   docker exec leadgen_backend alembic stamp head
   ```
3. Force rebuild if needed:
   ```powershell
   docker-compose down -v
   docker-compose up --build
   ```

### Frontend 404 Errors
**Error**: Can't access http://localhost:5173

**Solutions**:
1. Check frontend container is running:
   ```powershell
   docker ps | Select-String "frontend"
   ```
2. View frontend logs:
   ```powershell
   docker logs leadgen_frontend --tail 20
   ```
3. Restart frontend:
   ```powershell
   docker restart leadgen_frontend
   ```

### CORS Errors in Browser Console
**Error**: `Access to XMLHttpRequest... blocked by CORS policy`

**Solution**:
1. Verify CORS origins in docker-compose.yml include:
   ```yaml
   - BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
   ```
2. Restart backend:
   ```powershell
   docker restart leadgen_backend
   ```

## Useful Commands

### View All Container Status
```powershell
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### View Logs for All Services
```powershell
docker-compose logs -f
```

### Restart Specific Service
```powershell
docker restart leadgen_backend
docker restart leadgen_celery_worker
docker restart leadgen_frontend
```

### Access PostgreSQL Database
```powershell
docker exec -it leadgen_postgres psql -U postgres -d leadgen_db
```

### Check Redis Connection
```powershell
docker exec -it leadgen_redis redis-cli ping
# Should return: PONG
```

### Rebuild Everything from Scratch
```powershell
docker-compose down -v
docker-compose up --build
docker exec leadgen_backend alembic upgrade head
```

### Backend Import Errors
**Error**: `ImportError: attempted relative import with no known parent package`

**Solution**: Already fixed in Dockerfile - backend uses `app.main:app`

### Frontend Build Failures
**Error**: `Cannot find module @rollup/rollup-linux-x64-musl`

**Solution**: Already fixed - using production build with multi-stage Dockerfile

### Port Already in Use
**Error**: `Bind for 0.0.0.0:5173 failed: port is already allocated`

**Solution**:
```powershell
# Stop existing containers
docker-compose down

# Check for processes using the port
netstat -ano | findstr :5173
netstat -ano | findstr :8000

# Kill the process or change ports in docker-compose.yml
```

### Database Connection Issues
**Error**: `FATAL: database "leadgen_db" does not exist`

**Solution**:
```powershell
# Recreate database
docker-compose down -v
docker-compose up -d postgres
Start-Sleep -Seconds 5
docker-compose up -d
docker-compose exec -T backend alembic upgrade head
```

## Viewing Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f celery-worker
```

## Default Credentials

Create your first user through the API:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePass123!",
    "full_name": "Admin User"
  }'
```

## Next Steps

1. Read `IMPLEMENTATION_GUIDE.md` for feature details
2. Check `TESTING.md` for testing procedures
3. Review `API_DOCUMENTATION.md` for API reference
4. See `DEPLOYMENT.md` for production deployment
