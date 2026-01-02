#!/usr/bin/env python3
"""
Health Check Script - Validates API endpoints are responsive
Usage: python health_check.py
Exit Code: 0 = healthy, 1 = unhealthy
"""

import sys
import requests
import json
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 10  # seconds

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

def check_endpoint(name: str, url: str, expected_status: int = 200) -> bool:
    """Check if an endpoint is responding correctly"""
    try:
        print(f"Checking {name}...", end=" ")
        response = requests.get(url, timeout=TIMEOUT)
        
        if response.status_code == expected_status:
            print(f"{Colors.GREEN}✓ OK{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}✗ FAIL{Colors.RESET} (Status: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}✗ FAIL{Colors.RESET} (Connection refused)")
        return False
    except requests.exceptions.Timeout:
        print(f"{Colors.RED}✗ FAIL{Colors.RESET} (Timeout)")
        return False
    except Exception as e:
        print(f"{Colors.RED}✗ FAIL{Colors.RESET} ({str(e)})")
        return False

def check_health_endpoint(url: str) -> Dict[str, Any]:
    """Get detailed health check response"""
    try:
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def main():
    print("=" * 60)
    print("🏥 API Health Check")
    print("=" * 60)
    print(f"Target: {API_BASE_URL}\n")
    
    results = []
    
    # Check basic health endpoint
    health_check = check_health_endpoint(f"{API_BASE_URL}/health")
    if health_check:
        print(f"\n{Colors.GREEN}Health endpoint details:{Colors.RESET}")
        print(json.dumps(health_check, indent=2))
        print()
    
    # Check critical endpoints
    endpoints = [
        ("Health", "/health"),
        ("API Docs", "/docs"),
        ("API Root", "/api/"),
    ]
    
    for name, path in endpoints:
        url = f"{API_BASE_URL}{path}"
        results.append(check_endpoint(name, url))
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"{Colors.GREEN}✓ All checks passed ({passed}/{total}){Colors.RESET}")
        print("=" * 60)
        return 0
    else:
        print(f"{Colors.RED}✗ Some checks failed ({passed}/{total} passed){Colors.RESET}")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
