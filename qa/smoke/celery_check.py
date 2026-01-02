#!/usr/bin/env python3
"""
Celery Worker Health Check - Validates workers are running and processing tasks
Usage: python celery_check.py
Exit Code: 0 = healthy, 1 = unhealthy
"""

import sys
import subprocess
import json
from typing import List, Dict

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

def run_command(cmd: List[str]) -> tuple[int, str]:
    """Run shell command and return exit code and output"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return 1, "Command timed out"
    except Exception as e:
        return 1, str(e)

def check_celery_workers() -> bool:
    """Check if Celery workers are running"""
    print("Checking Celery workers...", end=" ")
    
    # Try docker-compose version first
    exit_code, output = run_command([
        "docker-compose", "exec", "-T", "backend",
        "celery", "-A", "app.celery_app", "inspect", "active"
    ])
    
    if exit_code == 0:
        print(f"{Colors.GREEN}✓ Workers running{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}✗ Workers not responding{Colors.RESET}")
        print(f"   Error: {output[:200]}")
        return False

def check_celery_queues() -> bool:
    """Check Celery queue status"""
    print("Checking Celery queues...", end=" ")
    
    exit_code, output = run_command([
        "docker-compose", "exec", "-T", "backend",
        "celery", "-A", "app.celery_app", "inspect", "reserved"
    ])
    
    if exit_code == 0:
        print(f"{Colors.GREEN}✓ Queues accessible{Colors.RESET}")
        return True
    else:
        print(f"{Colors.YELLOW}⚠ Queue check failed{Colors.RESET}")
        return False

def check_celery_ping() -> bool:
    """Ping Celery workers"""
    print("Pinging Celery workers...", end=" ")
    
    exit_code, output = run_command([
        "docker-compose", "exec", "-T", "backend",
        "celery", "-A", "app.celery_app", "inspect", "ping"
    ])
    
    if exit_code == 0 and "pong" in output.lower():
        print(f"{Colors.GREEN}✓ Workers responding{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}✗ Workers not responding to ping{Colors.RESET}")
        return False

def get_worker_stats() -> Dict:
    """Get detailed worker statistics"""
    exit_code, output = run_command([
        "docker-compose", "exec", "-T", "backend",
        "celery", "-A", "app.celery_app", "inspect", "stats"
    ])
    
    if exit_code == 0:
        try:
            return json.loads(output)
        except:
            return {"raw": output}
    return {}

def main():
    print("=" * 60)
    print("🔧 Celery Worker Health Check")
    print("=" * 60)
    print()
    
    results = []
    
    # Run checks
    results.append(check_celery_workers())
    results.append(check_celery_ping())
    results.append(check_celery_queues())
    
    # Get stats if available
    print("\nFetching worker statistics...")
    stats = get_worker_stats()
    if stats:
        print(f"{Colors.GREEN}Worker Stats:{Colors.RESET}")
        print(json.dumps(stats, indent=2)[:500] + "...")
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed >= 2:  # At least 2 of 3 checks should pass
        print(f"{Colors.GREEN}✓ Celery workers healthy ({passed}/{total} checks passed){Colors.RESET}")
        print("=" * 60)
        return 0
    else:
        print(f"{Colors.RED}✗ Celery workers unhealthy ({passed}/{total} checks passed){Colors.RESET}")
        print("=" * 60)
        print(f"\n{Colors.YELLOW}Troubleshooting:{Colors.RESET}")
        print("  1. Check if backend container is running: docker-compose ps")
        print("  2. Check backend logs: docker-compose logs backend")
        print("  3. Restart workers: docker-compose restart backend")
        return 1

if __name__ == "__main__":
    sys.exit(main())
