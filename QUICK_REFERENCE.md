# ⚡ Quick Reference Card

## 🚀 Start & Stop

```powershell
# Quick Start
.\start.ps1

# Manual Start
docker-compose up --build

# Run Migrations
docker-compose exec backend alembic upgrade head

# Stop All
docker-compose down

# Stop & Remove Data
docker-compose down -v
```

## 🌐 URLs

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |

## 📊 Ports

| Service | Port |
|---------|------|
| Frontend | 5173 |
| Backend | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |

## 🔑 Default Credentials

```
First User: Register at /signup
Database:
  - User: postgres
  - Password: postgres
  - Database: leadgen_db
```

## 📁 Important Files

```
Configuration:
  - backend/.env              (Backend config)
  - frontend/.env             (Frontend config)
  - docker-compose.yml        (Services config)

Documentation:
  - START_HERE.md             (👈 Read first!)
  - README.md                 (Main docs)
  - SETUP.md                  (Setup guide)
  - API_REFERENCE.md          (API docs)
  - TESTING.md                (Test checklist)

Code:
  - backend/main.py           (Backend entry)
  - backend/app/routes/       (API endpoints)
  - frontend/src/App.jsx      (Frontend entry)
  - frontend/src/pages/       (React pages)
```

## 🛠️ Common Commands

### Docker
```powershell
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f celery-worker

# Restart service
docker-compose restart backend

# Check status
docker-compose ps

# Execute command in container
docker-compose exec backend bash
```

### Database
```powershell
# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Run migrations
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1

# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d leadgen_db
```

### Backend
```powershell
# Install new package
docker-compose exec backend pip install package-name

# Run Python shell
docker-compose exec backend python

# Run tests (when added)
docker-compose exec backend pytest
```

### Frontend
```powershell
# Install new package
docker-compose exec frontend npm install package-name

# Build for production
docker-compose exec frontend npm run build
```

## 🐛 Troubleshooting

### Backend won't start
```powershell
# Check logs
docker-compose logs backend

# Common fixes:
# 1. Check if port 8000 is free
# 2. Verify .env file exists
# 3. Wait for PostgreSQL to be ready
```

### Frontend won't start
```powershell
# Check logs
docker-compose logs frontend

# Common fixes:
# 1. Delete node_modules volume
docker-compose down -v
# 2. Rebuild
docker-compose up --build
```

### Database errors
```powershell
# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

### Celery not processing
```powershell
# Check worker logs
docker-compose logs -f celery-worker

# Restart worker
docker-compose restart celery-worker
```

## 📝 API Quick Reference

### Authentication
```bash
# Register
POST /auth/register
Body: {"email": "user@example.com", "password": "pass123"}

# Login
POST /auth/login
Body: {"email": "user@example.com", "password": "pass123"}
Response: {"access_token": "...", "token_type": "bearer"}
```

### Leads (Authenticated)
```bash
# All requests need: Authorization: Bearer <token>

# List leads
GET /leads?page=1&page_size=50

# Create lead
POST /leads
Body: {
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "company": "Acme"
}

# Get lead
GET /leads/{id}

# Update lead
PUT /leads/{id}
Body: {"first_name": "Jane"}

# Delete lead
DELETE /leads/{id}

# Upload CSV
POST /leads/upload_csv
Body: multipart/form-data with file

# Enrich lead
POST /leads/{id}/enrich
```

## 🧪 Quick Tests

### Test Backend
```bash
# Health check
curl http://localhost:8000/health

# Should return: {"status": "healthy"}
```

### Test Frontend
```
Open: http://localhost:5173
Should see: Login page
```

### Test Database
```powershell
docker-compose exec postgres psql -U postgres -c "\l"
# Should list: leadgen_db
```

### Test Redis
```powershell
docker-compose exec redis redis-cli ping
# Should return: PONG
```

## 📊 Status Check

```powershell
# All services should be "Up"
docker-compose ps

# Should show:
# - leadgen_postgres (Up)
# - leadgen_redis (Up)
# - leadgen_backend (Up)
# - leadgen_celery_worker (Up)
# - leadgen_frontend (Up)
```

## 🔄 Development Workflow

```
1. Make code changes
   ↓
2. Files auto-reload (hot reload enabled)
   ↓
3. Test in browser
   ↓
4. Check logs if issues
   ↓
5. Commit changes
```

## 📦 Project Structure (Quick View)

```
d:\lead gen\
├── backend/          (Python FastAPI)
│   ├── app/          (Application code)
│   ├── alembic/      (Migrations)
│   └── main.py       (Entry point)
│
├── frontend/         (React + Vite)
│   ├── src/          (Source code)
│   └── index.html    (HTML template)
│
└── docker-compose.yml (Services)
```

## 🎯 Feature Checklist

- [x] User registration
- [x] User login
- [x] JWT authentication
- [x] Create lead
- [x] List leads
- [x] Update lead
- [x] Delete lead
- [x] CSV upload
- [x] Background enrichment
- [x] Responsive UI
- [x] Error handling
- [x] API documentation

## 🔐 Security Checklist

- [x] Password hashing
- [x] JWT tokens
- [x] Token expiration
- [x] CORS protection
- [x] Input validation
- [x] SQL injection protection
- [x] Environment variables
- [x] Protected routes

## 📚 Documentation Files

1. **START_HERE.md** ← Start here!
2. **README.md** - Overview
3. **SETUP.md** - Setup guide
4. **API_REFERENCE.md** - API docs
5. **TESTING.md** - Test cases
6. **ARCHITECTURE.md** - System design
7. **QUICK_REFERENCE.md** - This file

## 🎓 Learning Resources

- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- SQLAlchemy: https://docs.sqlalchemy.org
- Celery: https://docs.celeryq.dev
- TailwindCSS: https://tailwindcss.com

## 💡 Tips

1. Always check logs first: `docker-compose logs -f`
2. Environment variables are in `.env` files
3. Database changes need migrations
4. JWT tokens expire after 30 minutes
5. Use sample_leads.csv for testing

## 🚨 Emergency Reset

```powershell
# Nuclear option - reset everything
docker-compose down -v
docker system prune -a
docker-compose up --build
docker-compose exec backend alembic upgrade head
```

---

**Happy Coding! 🎉**

For detailed information, see the full documentation files.
