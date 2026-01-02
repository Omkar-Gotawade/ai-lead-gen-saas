#!/usr/bin/env python3
"""
Run All Smoke Tests - Quick health check before deployments
Usage: python run_all_smoke_tests.py
Exit Code: 0 = all pass, 1 = any failure
"""

import sys
import subprocess
import os
from typing import List, Tuple

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def run_script(script_path: str) -> Tuple[int, str]:
    """Run a Python script and return exit code and output"""
    try:
        print(f"\n{Colors.BLUE}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}Running: {os.path.basename(script_path)}{Colors.RESET}")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")
        
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Print output
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode, result.stdout + result.stderr
        
    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}✗ Script timed out (60s){Colors.RESET}")
        return 1, "Timeout"
    except Exception as e:
        print(f"{Colors.RED}✗ Error running script: {e}{Colors.RESET}")
        return 1, str(e)

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("🚀 RUNNING ALL SMOKE TESTS")
    print("=" * 60)
    print(f"{Colors.RESET}")
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    smoke_dir = os.path.join(script_dir, "smoke")
    
    # Tests to run in order
    tests = [
        "health_check.py",
        "redis_check.py",
        "db_migration_check.py",
        "celery_check.py"
    ]
    
    results = []
    outputs = []
    
    for test in tests:
        test_path = os.path.join(smoke_dir, test)
        
        if not os.path.exists(test_path):
            print(f"{Colors.YELLOW}⚠ Test not found: {test}{Colors.RESET}")
            results.append(False)
            continue
        
        exit_code, output = run_script(test_path)
        results.append(exit_code == 0)
        outputs.append((test, exit_code, output))
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"{Colors.RESET}")
    
    passed = sum(results)
    total = len(results)
    
    for i, test in enumerate(tests):
        if i < len(results):
            status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if results[i] else f"{Colors.RED}✗ FAIL{Colors.RESET}"
            print(f"  {status}  {test}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}")
    
    # Final verdict
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL SMOKE TESTS PASSED{Colors.RESET}")
        print(f"{Colors.GREEN}System is healthy and ready for deployment{Colors.RESET}")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")
        return 0
    else:
        failed_count = total - passed
        print(f"{Colors.RED}{Colors.BOLD}✗ {failed_count} SMOKE TEST(S) FAILED{Colors.RESET}")
        print(f"{Colors.RED}Fix issues before proceeding with deployment{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Failed tests:{Colors.RESET}")
        
        for i, test in enumerate(tests):
            if i < len(results) and not results[i]:
                print(f"  - {test}")
        
        print(f"\n{Colors.YELLOW}Troubleshooting:{Colors.RESET}")
        print("  1. Check if all containers are running: docker-compose ps")
        print("  2. Check logs: docker-compose logs")
        print("  3. Restart services: docker-compose restart")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(130)
