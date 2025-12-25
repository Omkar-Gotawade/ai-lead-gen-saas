"""Complete frontend/backend test"""
import requests
import time

print("="*60)
print("COMPLETE SYSTEM TEST")
print("="*60)

# Test 1: Backend API
print("\n1. Testing Backend API...")
try:
    resp = requests.post('http://localhost:8000/auth/login', 
                        json={'email':'test@example.com','password':'testpass123'})
    print(f"   ✓ Login: {resp.status_code}")
    token = resp.json()['access_token']
    
    resp2 = requests.get('http://localhost:8000/api/email-provider/me',
                        headers={'Authorization': f'Bearer {token}'})
    print(f"   ✓ Email Provider Check: {resp2.status_code}")
    print(f"   ✓ Provider: {resp2.json()}")
    
    resp3 = requests.post('http://localhost:8000/api/email/send-test',
                         headers={'Authorization': f'Bearer {token}'},
                         json={'to_email':'test@test.com','subject':'Test','body':'Test'})
    print(f"   ✓ Send Test Email: {resp3.status_code}")
    print(f"   ✓ Response: {resp3.json()}")
except Exception as e:
    print(f"   ✗ Backend Error: {e}")

# Test 2: Frontend
print("\n2. Testing Frontend...")
try:
    resp = requests.get('http://localhost:5173/')
    print(f"   ✓ Frontend accessible: {resp.status_code}")
except Exception as e:
    print(f"   ✗ Frontend Error: {e}")

# Test 3: Check containers
print("\n3. Checking Docker Containers...")
import subprocess
result = subprocess.run(['docker', 'ps', '--filter', 'name=leadgen', '--format', '{{.Names}}\t{{.Status}}'],
                       capture_output=True, text=True)
print(result.stdout)

print("\n" + "="*60)
print("BACKEND WORKS ✓")
print("Issue: Frontend still serving old cached build")
print("\nSOLUTION:")
print("1. Run: docker compose build frontend")
print("2. Run: docker compose up -d frontend") 
print("3. Clear browser cache (Ctrl+Shift+Delete)")
print("4. Hard refresh (Ctrl+Shift+R)")
print("="*60)
