#!/usr/bin/env python3
"""
Redis Health Check - Validates Redis is accessible and responsive
Usage: python redis_check.py
Exit Code: 0 = healthy, 1 = unhealthy
"""

import sys
import subprocess
from typing import List

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
            timeout=5
        )
        return result.returncode, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return 1, "Command timed out"
    except Exception as e:
        return 1, str(e)

def check_redis_container() -> bool:
    """Check if Redis container is running"""
    print("Checking Redis container...", end=" ")
    
    exit_code, output = run_command(["docker-compose", "ps", "redis"])
    
    if exit_code == 0 and "Up" in output:
        print(f"{Colors.GREEN}✓ Running{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}✗ Not running{Colors.RESET}")
        return False

def check_redis_ping() -> bool:
    """Ping Redis to verify it's responding"""
    print("Pinging Redis...", end=" ")
    
    exit_code, output = run_command([
        "docker-compose", "exec", "-T", "redis",
        "redis-cli", "PING"
    ])
    
    if exit_code == 0 and "PONG" in output:
        print(f"{Colors.GREEN}✓ PONG{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}✗ No response{Colors.RESET}")
        return False

def check_redis_memory() -> bool:
    """Check Redis memory usage"""
    print("Checking Redis memory...", end=" ")
    
    exit_code, output = run_command([
        "docker-compose", "exec", "-T", "redis",
        "redis-cli", "INFO", "memory"
    ])
    
    if exit_code == 0:
        # Parse used memory
        for line in output.split('\n'):
            if line.startswith('used_memory_human:'):
                memory = line.split(':')[1].strip()
                print(f"{Colors.GREEN}✓ {memory} used{Colors.RESET}")
                return True
        print(f"{Colors.YELLOW}⚠ Info retrieved{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}✗ Failed{Colors.RESET}")
        return False

def check_redis_keys() -> bool:
    """Check number of keys in Redis"""
    print("Checking Redis keys...", end=" ")
    
    exit_code, output = run_command([
        "docker-compose", "exec", "-T", "redis",
        "redis-cli", "DBSIZE"
    ])
    
    if exit_code == 0:
        key_count = output.strip()
        print(f"{Colors.GREEN}✓ {key_count} keys{Colors.RESET}")
        return True
    else:
        print(f"{Colors.YELLOW}⚠ Could not retrieve{Colors.RESET}")
        return False

def get_redis_info() -> str:
    """Get Redis server info"""
    exit_code, output = run_command([
        "docker-compose", "exec", "-T", "redis",
        "redis-cli", "INFO", "server"
    ])
    
    if exit_code == 0:
        info_lines = []
        for line in output.split('\n'):
            if any(key in line for key in ['redis_version', 'uptime_in_seconds', 'connected_clients']):
                info_lines.append(line)
        return '\n'.join(info_lines)
    return "Could not retrieve info"

def main():
    print("=" * 60)
    print("🗄️  Redis Health Check")
    print("=" * 60)
    print()
    
    results = []
    
    # Run checks
    results.append(check_redis_container())
    results.append(check_redis_ping())
    results.append(check_redis_memory())
    results.append(check_redis_keys())
    
    # Get server info
    print("\nRedis server info:")
    print(get_redis_info())
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed >= 3:  # At least 3 of 4 checks should pass
        print(f"{Colors.GREEN}✓ Redis healthy ({passed}/{total} checks passed){Colors.RESET}")
        print("=" * 60)
        return 0
    else:
        print(f"{Colors.RED}✗ Redis unhealthy ({passed}/{total} checks passed){Colors.RESET}")
        print("=" * 60)
        print(f"\n{Colors.YELLOW}Troubleshooting:{Colors.RESET}")
        print("  1. Check Redis logs: docker-compose logs redis")
        print("  2. Restart Redis: docker-compose restart redis")
        print("  3. Check Redis config: docker-compose exec redis redis-cli CONFIG GET '*'")
        return 1

if __name__ == "__main__":
    sys.exit(main())
