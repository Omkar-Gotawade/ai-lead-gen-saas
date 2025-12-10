# API Endpoints Reference

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

---

## Authentication Endpoints

### Register New User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "created_at": "2025-12-09T12:00:00"
}
```

**Errors:**
- `400`: Email already registered

---

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401`: Incorrect email or password

---

## Lead Endpoints (Protected)

All lead endpoints require authentication. Include JWT token in header:
```http
Authorization: Bearer <your_token>
```

### List Leads (Paginated)
```http
GET /leads?page=1&page_size=50
```

**Response (200 OK):**
```json
{
  "total": 150,
  "page": 1,
  "page_size": 50,
  "leads": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "org_id": null,
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "email": "john.doe@example.com",
      "company": "Acme Corp",
      "source": "manual",
      "enriched_data": null,
      "created_at": "2025-12-09T12:00:00"
    }
  ]
}
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 50)

---

### Create Lead
```http
POST /leads
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "company": "Acme Corp",
  "source": "manual"
}
```

**Response (201 Created):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "org_id": null,
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "company": "Acme Corp",
  "source": "manual",
  "enriched_data": null,
  "created_at": "2025-12-09T12:30:00"
}
```

**Required Fields:**
- `first_name` (string)
- `last_name` (string)
- `email` (string, valid email format)

**Optional Fields:**
- `company` (string)
- `source` (string, default: "manual")

---

### Get Single Lead
```http
GET /leads/{lead_id}
```

**Response (200 OK):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "org_id": null,
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "company": "Acme Corp",
  "source": "manual",
  "enriched_data": {
    "linkedin_url": "https://linkedin.com/in/john-doe",
    "title": "Software Engineer",
    "company_size": "51-200"
  },
  "created_at": "2025-12-09T12:30:00"
}
```

**Errors:**
- `404`: Lead not found

---

### Update Lead
```http
PUT /leads/{lead_id}
Content-Type: application/json

{
  "first_name": "Jane",
  "email": "jane.doe@example.com",
  "company": "New Corp"
}
```

**Response (200 OK):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "org_id": null,
  "first_name": "Jane",
  "last_name": "Doe",
  "full_name": "Jane Doe",
  "email": "jane.doe@example.com",
  "company": "New Corp",
  "source": "manual",
  "enriched_data": null,
  "created_at": "2025-12-09T12:30:00"
}
```

**Note:** Only include fields you want to update. Omitted fields remain unchanged.

**Errors:**
- `404`: Lead not found

---

### Delete Lead
```http
DELETE /leads/{lead_id}
```

**Response (204 No Content)**

**Errors:**
- `404`: Lead not found

---

### Upload CSV
```http
POST /leads/upload_csv
Content-Type: multipart/form-data

file: <csv_file>
```

**CSV Format:**
```csv
first_name,last_name,email,company
John,Doe,john.doe@example.com,Acme Corp
Jane,Smith,jane.smith@example.com,Tech Inc
```

**Required Columns:**
- `first_name`
- `last_name`
- `email`

**Optional Columns:**
- `company`

**Response (201 Created):**
```json
{
  "message": "CSV uploaded successfully",
  "leads_created": 25
}
```

**Errors:**
- `400`: File must be a CSV
- `400`: Error processing CSV (invalid format)

---

### Enrich Lead
```http
POST /leads/{lead_id}/enrich
```

**Response (202 Accepted):**
```json
{
  "message": "Lead enrichment job enqueued",
  "lead_id": "770e8400-e29b-41d4-a716-446655440002",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Note:** This is an asynchronous operation. The enrichment happens in the background via Celery worker.

**Errors:**
- `404`: Lead not found

---

## Error Response Format

All errors follow this structure:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `204`: No Content (successful deletion)
- `400`: Bad Request (validation error)
- `401`: Unauthorized (missing or invalid token)
- `404`: Not Found
- `500`: Internal Server Error

---

## Authentication Flow

```
1. User Registration
   POST /auth/register → User Created

2. User Login
   POST /auth/login → JWT Token Received

3. Subsequent Requests
   Include: Authorization: Bearer <token>
   
4. Token Expiry
   After 30 minutes (configurable) → 401 Unauthorized
   User must login again
```

---

## Examples Using cURL

### Register
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Create Lead (with auth)
```bash
curl -X POST http://localhost:8000/leads \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "first_name":"John",
    "last_name":"Doe",
    "email":"john@example.com",
    "company":"Acme"
  }'
```

### List Leads
```bash
curl -X GET "http://localhost:8000/leads?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Examples Using Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": "test@example.com",
    "password": "password123"
})

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "test@example.com",
    "password": "password123"
})
token = response.json()["access_token"]

# Create Lead
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(f"{BASE_URL}/leads", 
    headers=headers,
    json={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "company": "Acme"
    }
)

# List Leads
response = requests.get(f"{BASE_URL}/leads?page=1", headers=headers)
leads = response.json()
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production:
- Implement rate limiting middleware
- Suggested: 100 requests/minute per user
- Use Redis for rate limit tracking

---

## CORS Configuration

Allowed origins (configurable in backend/.env):
- `http://localhost:5173` (development)
- `http://localhost:3000` (alternative dev port)

For production, update `BACKEND_CORS_ORIGINS` environment variable.

---

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Use the interactive documentation to:
- Explore all endpoints
- Test API calls directly in browser
- See request/response schemas
- Try authentication flow
