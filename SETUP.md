# Week 0 + Week 1 Setup Guide

## Quick Start (Recommended)

1. **Start all services with Docker Compose:**
   ```powershell
   cd "d:\lead gen"
   docker-compose up --build
   ```

2. **Run database migrations** (in a new terminal):
   ```powershell
   docker-compose exec backend alembic upgrade head
   ```

3. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/docs

## Manual Setup (Alternative)

If you prefer to run services individually without Docker:

### Backend Setup

1. **Create virtual environment:**
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```powershell
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Start PostgreSQL and Redis** (using Docker or local installation)

5. **Run migrations:**
   ```powershell
   alembic upgrade head
   ```

6. **Start the backend server:**
   ```powershell
   uvicorn main:app --reload --port 8000
   ```

7. **Start Celery worker** (in another terminal):
   ```powershell
   celery -A app.celery_app worker --loglevel=info
   ```

### Frontend Setup

1. **Install dependencies:**
   ```powershell
   cd frontend
   npm install
   ```

2. **Set up environment variables:**
   ```powershell
   cp .env.example .env
   # Edit .env if needed
   ```

3. **Start development server:**
   ```powershell
   npm run dev
   ```

## Testing the Application

1. **Sign Up:**
   - Go to http://localhost:5173
   - Click "Sign up"
   - Enter email and password
   - Click "Sign up" button

2. **Login:**
   - Enter your credentials
   - You'll be redirected to the Leads page

3. **Test CSV Upload:**
   - Use the included `sample_leads.csv` file
   - Click "Upload CSV"
   - Select the file and upload
   - You should see 10 leads imported

4. **Test Lead Creation:**
   - Click "Add lead"
   - Fill in the form
   - Click "Create"

5. **Test Lead Enrichment:**
   - Click "Enrich" on any lead
   - Wait 3-5 seconds
   - The lead will be enriched with sample data

## Troubleshooting

**Backend won't start:**
- Check if PostgreSQL is running
- Verify database credentials in `.env`
- Make sure port 8000 is not in use

**Frontend won't start:**
- Delete `node_modules` and run `npm install` again
- Check if port 5173 is available

**Celery worker not processing jobs:**
- Verify Redis is running
- Check Redis connection in `.env`
- Restart the worker

**Database migration errors:**
- Delete the `alembic/versions` folder (except `__init__.py`)
- Drop and recreate the database
- Run `alembic upgrade head` again

## Development Tips

- Backend API docs: http://localhost:8000/docs
- Use the interactive API docs to test endpoints
- Frontend hot-reloads on file changes
- Backend reloads on file changes (with `--reload` flag)
- Check Docker logs: `docker-compose logs -f [service-name]`

## Architecture Overview

```
User Request → React Frontend (Port 5173)
    ↓
    API Call → FastAPI Backend (Port 8000)
    ↓
    Database Query → PostgreSQL (Port 5432)
    ↓
    Background Job → Celery Worker + Redis (Port 6379)
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/leadgen_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## Next Steps

After completing Week 0 + Week 1:
1. Test all features thoroughly
2. Review the code structure
3. Plan Week 2 features
4. Consider adding tests
5. Set up CI/CD pipeline
