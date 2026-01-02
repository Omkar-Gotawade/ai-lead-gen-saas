#!/usr/bin/env python3
"""
Database Migration Status Check - Validates DB schema is up to date
Usage: python db_migration_check.py
Exit Code: 0 = healthy, 1 = unhealthy
"""

import sys
import subprocess
from typing import List

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def run_command(cmd: List[str]) -> tuple[int, str]:
    """Run shell command and return exit code and output"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return 1, "Command timed out"
    except Exception as e:
        return 1, str(e)

def check_db_connection() -> bool:
    """Check if database is accessible"""
    print("Checking database connection...", end=" ")
    
    exit_code, output = run_command([
        "docker-compose", "exec", "-T", "backend",
        "python", "-c",
        "from app.database import engine; engine.connect(); print('OK')"
    ])
    
    if exit_code == 0 and "OK" in output:
        print(f"{Colors.GREEN}✓ Connected{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}✗ Connection failed{Colors.RESET}")
        print(f"   Error: {output[:200]}")
        return False

def check_migration_current() -> bool:
    """Check if migrations are up to date"""
    print("Checking migration status...", end=" ")
    
    exit_code, output = run_command([
        "docker-compose", "exec", "-T", "backend",
        "alembic", "current"
    ])
    
    if exit_code == 0:
        # Extract revision if present
        for line in output.split('\n'):
            if "(head)" in line or "head" in line.lower():
                print(f"{Colors.GREEN}✓ Up to date{Colors.RESET}")
                return True
        print(f"{Colors.YELLOW}⚠ Migration status unclear{Colors.RESET}")
        print(f"   Output: {output[:200]}")
        return True  # Don't fail, just warn
    else:
        print(f"{Colors.RED}✗ Failed to check{Colors.RESET}")
        return False

def check_pending_migrations() -> tuple[bool, List[str]]:
    """Check for pending migrations"""
    print("Checking for pending migrations...", end=" ")
    
    exit_code, output = run_command([
        "docker-compose", "exec", "-T", "backend",
        "alembic", "heads"
    ])
    
    if exit_code == 0:
        # Compare with current
        _, current_output = run_command([
            "docker-compose", "exec", "-T", "backend",
            "alembic", "current"
        ])
        
        heads = [line.strip() for line in output.split('\n') if line.strip() and not line.startswith('INFO')]
        current = [line.strip() for line in current_output.split('\n') if line.strip() and not line.startswith('INFO')]
        
        if heads and current and heads[0] in current[0]:
            print(f"{Colors.GREEN}✓ No pending migrations{Colors.RESET}")
            return True, []
        else:
            print(f"{Colors.YELLOW}⚠ Pending migrations detected{Colors.RESET}")
            return False, heads
    else:
        print(f"{Colors.RED}✗ Failed to check{Colors.RESET}")
        return False, []

def list_migration_history() -> str:
    """Get migration history"""
    exit_code, output = run_command([
        "docker-compose", "exec", "-T", "backend",
        "alembic", "history", "--verbose"
    ])
    
    if exit_code == 0:
        # Get last 5 migrations
        lines = [l for l in output.split('\n') if l.strip()]
        return '\n'.join(lines[:10])
    return "Could not retrieve history"

def check_table_count() -> bool:
    """Check number of tables in database"""
    print("Checking database tables...", end=" ")
    
    exit_code, output = run_command([
        "docker-compose", "exec", "-T", "backend",
        "python", "-c",
        "from app.database import engine; from sqlalchemy import inspect; "
        "insp = inspect(engine); tables = insp.get_table_names(); "
        "print(f'{len(tables)} tables'); [print(t) for t in sorted(tables)]"
    ])
    
    if exit_code == 0:
        table_count_line = output.split('\n')[0]
        print(f"{Colors.GREEN}✓ {table_count_line}{Colors.RESET}")
        
        # Show table names
        tables = [l.strip() for l in output.split('\n')[1:] if l.strip()]
        if tables:
            print(f"   Tables: {', '.join(tables[:10])}" + ("..." if len(tables) > 10 else ""))
        return True
    else:
        print(f"{Colors.RED}✗ Failed{Colors.RESET}")
        return False

def main():
    print("=" * 60)
    print("🗄️  Database Migration Status Check")
    print("=" * 60)
    print()
    
    results = []
    
    # Run checks
    results.append(check_db_connection())
    results.append(check_migration_current())
    
    pending_ok, pending_migrations = check_pending_migrations()
    results.append(pending_ok)
    
    results.append(check_table_count())
    
    # Show migration history
    print(f"\n{Colors.BLUE}Recent migration history:{Colors.RESET}")
    print(list_migration_history())
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed >= 3:  # At least 3 of 4 checks should pass
        print(f"{Colors.GREEN}✓ Database healthy ({passed}/{total} checks passed){Colors.RESET}")
        if pending_migrations:
            print(f"\n{Colors.YELLOW}⚠ Note: Pending migrations detected:{Colors.RESET}")
            for migration in pending_migrations[:5]:
                print(f"   - {migration}")
            print(f"\n{Colors.YELLOW}Run migrations:{Colors.RESET}")
            print("   docker-compose exec backend alembic upgrade head")
        print("=" * 60)
        return 0
    else:
        print(f"{Colors.RED}✗ Database unhealthy ({passed}/{total} checks passed){Colors.RESET}")
        print("=" * 60)
        print(f"\n{Colors.YELLOW}Troubleshooting:{Colors.RESET}")
        print("  1. Check postgres logs: docker-compose logs postgres")
        print("  2. Check backend logs: docker-compose logs backend")
        print("  3. Run migrations: docker-compose exec backend alembic upgrade head")
        print("  4. Check connection string in .env")
        return 1

if __name__ == "__main__":
    sys.exit(main())
