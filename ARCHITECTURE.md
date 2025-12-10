# 🏗️ System Architecture Diagram

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                          USER BROWSER                                 ┃
┃                     (Chrome, Firefox, Edge)                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                           │
                           │ HTTP Requests
                           │ Port 5173
                           ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                      FRONTEND (React + Vite)                          ┃
┃  ┌──────────────────────────────────────────────────────────────┐   ┃
┃  │  Pages                                                        │   ┃
┃  │  ├─ Login.jsx         (Authentication)                       │   ┃
┃  │  ├─ Signup.jsx        (User Registration)                    │   ┃
┃  │  └─ Leads.jsx         (Lead Management)                      │   ┃
┃  └──────────────────────────────────────────────────────────────┘   ┃
┃  ┌──────────────────────────────────────────────────────────────┐   ┃
┃  │  Components                                                   │   ┃
┃  │  ├─ Layout.jsx              (App Shell + Navbar)             │   ┃
┃  │  ├─ ProtectedRoute.jsx      (Route Guard)                    │   ┃
┃  │  ├─ CreateLeadModal.jsx     (Create UI)                      │   ┃
┃  │  ├─ EditLeadModal.jsx       (Update UI)                      │   ┃
┃  │  ├─ DeleteLeadModal.jsx     (Delete Confirm)                 │   ┃
┃  │  └─ CSVUploadModal.jsx      (Bulk Upload)                    │   ┃
┃  └──────────────────────────────────────────────────────────────┘   ┃
┃  ┌──────────────────────────────────────────────────────────────┐   ┃
┃  │  Context & State                                              │   ┃
┃  │  └─ AuthContext.jsx    (JWT Token, User State)               │   ┃
┃  └──────────────────────────────────────────────────────────────┘   ┃
┃  ┌──────────────────────────────────────────────────────────────┐   ┃
┃  │  API Client                                                   │   ┃
┃  │  ├─ axios.js           (HTTP Client + Interceptors)          │   ┃
┃  │  └─ index.js           (API Methods: auth, leads)            │   ┃
┃  └──────────────────────────────────────────────────────────────┘   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                           │
                           │ REST API Calls
                           │ Port 8000
                           ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                      BACKEND (FastAPI)                                ┃
┃  ┌──────────────────────────────────────────────────────────────┐   ┃
┃  │  Routes (API Endpoints)                                       │   ┃
┃  │  ├─ /auth/register         POST  (Create Account)            │   ┃
┃  │  ├─ /auth/login            POST  (Get JWT Token)             │   ┃
┃  │  ├─ /leads                 GET   (List Leads)                │   ┃
┃  │  ├─ /leads                 POST  (Create Lead)               │   ┃
┃  │  ├─ /leads/{id}            GET   (Get Single Lead)           │   ┃
┃  │  ├─ /leads/{id}            PUT   (Update Lead)               │   ┃
┃  │  ├─ /leads/{id}            DELETE (Delete Lead)              │   ┃
┃  │  ├─ /leads/upload_csv      POST  (Bulk Import)               │   ┃
┃  │  └─ /leads/{id}/enrich     POST  (Enqueue Job)               │   ┃
┃  └──────────────────────────────────────────────────────────────┘   ┃
┃                           │                                           ┃
┃  ┌──────────────────────────────────────────────────────────────┐   ┃
┃  │  Services (Business Logic)                                    │   ┃
┃  │  ├─ AuthService                                               │   ┃
┃  │  │  ├─ create_user()        (Hash password, save user)       │   ┃
┃  │  │  ├─ authenticate_user()  (Verify credentials)             │   ┃
┃  │  │  ├─ create_access_token() (Generate JWT)                  │   ┃
┃  │  │  └─ get_current_user()   (Validate token)                 │   ┃
┃  │  │                                                             │   ┃
┃  │  └─ LeadService                                               │   ┃
┃  │     ├─ create_lead()        (Save to DB)                      │   ┃
┃  │     ├─ get_leads()          (Paginated query)                 │   ┃
┃  │     ├─ update_lead()        (Modify record)                   │   ┃
┃  │     ├─ delete_lead()        (Remove from DB)                  │   ┃
┃  │     └─ create_from_csv()    (Bulk insert)                     │   ┃
┃  └──────────────────────────────────────────────────────────────┘   ┃
┃                           │                                           ┃
┃  ┌──────────────────────────────────────────────────────────────┐   ┃
┃  │  Models (Database Tables)                                     │   ┃
┃  │  ├─ User                                                       │   ┃
┃  │  │  ├─ id (UUID)                                              │   ┃
┃  │  │  ├─ email (String, Unique)                                 │   ┃
┃  │  │  ├─ hashed_password (String)                               │   ┃
┃  │  │  └─ created_at (DateTime)                                  │   ┃
┃  │  │                                                             │   ┃
┃  │  └─ Lead                                                       │   ┃
┃  │     ├─ id (UUID)                                              │   ┃
┃  │     ├─ first_name, last_name, full_name (Strings)            │   ┃
┃  │     ├─ email (String)                                         │   ┃
┃  │     ├─ company (String, Nullable)                             │   ┃
┃  │     ├─ source (String)                                        │   ┃
┃  │     ├─ enriched_data (JSONB)                                  │   ┃
┃  │     └─ created_at (DateTime)                                  │   ┃
┃  └──────────────────────────────────────────────────────────────┘   ┃
┗━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
             │                          │
             │ SQL Queries              │ Job Queue
             │ Port 5432                │ Port 6379
             ▼                          ▼
┏━━━━━━━━━━━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃    PostgreSQL 15      ┃  ┃           Redis 7                        ┃
┃  ┌─────────────────┐  ┃  ┃  ┌────────────────────────────────────┐ ┃
┃  │  Tables         │  ┃  ┃  │  Message Broker                    │ ┃
┃  │  ├─ users       │  ┃  ┃  │  - Task Queue                      │ ┃
┃  │  └─ leads       │  ┃  ┃  │  - Job Results                     │ ┃
┃  └─────────────────┘  ┃  ┃  │  - Cache (future use)              │ ┃
┃                       ┃  ┃  └────────────────────────────────────┘ ┃
┃  Volume: postgres_data┃  ┗━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┛
┗━━━━━━━━━━━━━━━━━━━━━━┛                  │
                                          │ Consume Jobs
                                          ▼
                          ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                          ┃      Celery Worker                       ┃
                          ┃  ┌────────────────────────────────────┐ ┃
                          ┃  │  Background Tasks                  │ ┃
                          ┃  │  └─ enrich_lead_task()             │ ┃
                          ┃  │     ├─ Fetch lead from DB          │ ┃
                          ┃  │     ├─ Call enrichment APIs        │ ┃
                          ┃  │     ├─ Update enriched_data        │ ┃
                          ┃  │     └─ Save to DB                  │ ┃
                          ┃  └────────────────────────────────────┘ ┃
                          ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


═══════════════════════════════════════════════════════════════════════
                           DATA FLOW EXAMPLES
═══════════════════════════════════════════════════════════════════════

1. USER REGISTRATION FLOW
   ────────────────────────
   Browser → Frontend (Signup Page)
      │
      ├─ User enters email + password
      │
      └─→ POST /auth/register
            │
            └─→ Backend (AuthService)
                  │
                  ├─ Hash password with bcrypt
                  ├─ Create User model
                  └─→ Save to PostgreSQL
                        │
                        └─→ Return User object
                              │
                              └─→ Frontend redirects to Login


2. LOGIN FLOW
   ───────────
   Browser → Frontend (Login Page)
      │
      ├─ User enters credentials
      │
      └─→ POST /auth/login
            │
            └─→ Backend (AuthService)
                  │
                  ├─ Verify password hash
                  ├─ Generate JWT token
                  └─→ Return token
                        │
                        └─→ Frontend stores in localStorage
                              │
                              └─→ Redirect to Leads page


3. CREATE LEAD FLOW
   ─────────────────
   Browser → Frontend (Leads Page)
      │
      ├─ Click "Add Lead"
      ├─ Fill form (first_name, last_name, email, company)
      │
      └─→ POST /leads + JWT token
            │
            └─→ Backend (LeadService)
                  │
                  ├─ Validate JWT (get_current_user)
                  ├─ Create Lead model
                  ├─ Set full_name = first + last
                  └─→ Save to PostgreSQL
                        │
                        └─→ Return Lead object
                              │
                              └─→ Frontend updates table


4. CSV UPLOAD FLOW
   ────────────────
   Browser → Frontend (CSV Upload Modal)
      │
      ├─ Select CSV file
      │
      └─→ POST /leads/upload_csv + file + JWT
            │
            └─→ Backend (LeadService)
                  │
                  ├─ Parse CSV with pandas
                  ├─ Validate columns
                  ├─ Loop through rows
                  ├─ Create Lead for each row
                  └─→ Bulk insert to PostgreSQL
                        │
                        └─→ Return count
                              │
                              └─→ Frontend shows success


5. LEAD ENRICHMENT FLOW
   ─────────────────────
   Browser → Frontend (Leads Page)
      │
      ├─ Click "Enrich" button
      │
      └─→ POST /leads/{id}/enrich + JWT
            │
            └─→ Backend (LeadsRoute)
                  │
                  ├─ Verify lead exists
                  └─→ Enqueue Celery task
                        │
                        ├─→ Redis (job queue)
                        │     │
                        │     └─→ Celery Worker
                        │           │
                        │           ├─ Get lead from DB
                        │           ├─ Call APIs (simulated)
                        │           ├─ Update enriched_data
                        │           └─→ Save to PostgreSQL
                        │
                        └─→ Return task_id
                              │
                              └─→ Frontend shows "Enriching..."


═══════════════════════════════════════════════════════════════════════
                        SECURITY LAYERS
═══════════════════════════════════════════════════════════════════════

1. Password Security
   ─────────────────
   Plain Password → bcrypt hash → Database
   (Never stored in plain text)

2. Authentication
   ──────────────
   Login → JWT Token → localStorage
   Every API call includes: Authorization: Bearer <token>

3. Authorization
   ─────────────
   Protected Routes → get_current_user() → Validates JWT
   Invalid/Expired token → 401 Unauthorized

4. Input Validation
   ────────────────
   User Input → Pydantic Schema → Validated
   Invalid data → 422 Validation Error

5. SQL Injection Protection
   ────────────────────────
   All queries use SQLAlchemy ORM
   No raw SQL concatenation

6. CORS Protection
   ───────────────
   Only allowed origins can access API
   Configured in BACKEND_CORS_ORIGINS


═══════════════════════════════════════════════════════════════════════
                       SCALABILITY FEATURES
═══════════════════════════════════════════════════════════════════════

✅ Horizontal Scaling Ready
   - Stateless backend (JWT auth)
   - Can run multiple backend instances
   - Load balancer ready

✅ Database Optimization
   - Indexes on email, org_id
   - Connection pooling (10 + 20 overflow)
   - Pagination for large datasets

✅ Async Background Jobs
   - Non-blocking enrichment
   - Celery worker scalable
   - Can add more workers

✅ Caching Ready
   - Redis already integrated
   - Can cache frequent queries
   - Session storage possible

✅ API Design
   - RESTful endpoints
   - Versioning ready
   - Rate limiting ready


═══════════════════════════════════════════════════════════════════════
                         MONITORING POINTS
═══════════════════════════════════════════════════════════════════════

Backend Logs:
  docker-compose logs -f backend

Celery Worker Logs:
  docker-compose logs -f celery-worker

Database Logs:
  docker-compose logs -f postgres

All Services:
  docker-compose logs -f

Container Status:
  docker-compose ps
```

---

## 🎯 Architecture Highlights

### Clean Architecture
- **Separation of Concerns**: Routes → Services → Models
- **Dependency Injection**: Database sessions injected
- **Single Responsibility**: Each module has one job

### Scalability
- **Stateless API**: JWT tokens, no server sessions
- **Background Jobs**: Async processing with Celery
- **Database Pooling**: Efficient connection management
- **Pagination**: Handle millions of records

### Security
- **Password Hashing**: Bcrypt for passwords
- **Token-Based Auth**: JWT with expiration
- **CORS Protection**: Whitelist origins
- **Input Validation**: Pydantic schemas
- **SQL Safety**: ORM prevents injection

### Developer Experience
- **Hot Reload**: Frontend and backend
- **Auto Documentation**: Swagger + ReDoc
- **Type Safety**: Pydantic + Type hints
- **Error Messages**: Clear, actionable
- **Easy Setup**: One-command start

---

**This architecture is production-ready and designed to scale! 🚀**
