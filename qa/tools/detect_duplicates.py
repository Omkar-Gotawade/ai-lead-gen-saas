#!/usr/bin/env python3
"""
Duplicate Lead Detector - Finds duplicate email addresses in leads table
Usage: python detect_duplicates.py [--fix]
Exit Code: 0 = no duplicates, 1 = duplicates found
"""

import sys
import subprocess
import argparse
from typing import List, Tuple

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

def run_query(query: str) -> Tuple[int, str]:
    """Run SQL query via docker-compose"""
    cmd = [
        "docker-compose", "exec", "-T", "backend",
        "python", "-c",
        f"from app.database import SessionLocal; "
        f"from sqlalchemy import text; "
        f"db = SessionLocal(); "
        f"result = db.execute(text('{query}')); "
        f"for row in result: print(row)"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout
    except Exception as e:
        return 1, str(e)

def find_duplicates() -> List[Tuple[str, int]]:
    """Find duplicate email addresses"""
    query = """
        SELECT email, COUNT(*) as count 
        FROM leads 
        GROUP BY email 
        HAVING COUNT(*) > 1 
        ORDER BY count DESC
    """
    
    exit_code, output = run_query(query)
    
    if exit_code != 0:
        print(f"{Colors.RED}✗ Query failed{Colors.RESET}")
        print(output)
        return []
    
    duplicates = []
    for line in output.split('\n'):
        if '@' in line and ',' in line:
            # Parse output like: ('email@example.com', 3)
            parts = line.strip('()').split(',')
            if len(parts) == 2:
                email = parts[0].strip().strip("'")
                count = int(parts[1].strip())
                duplicates.append((email, count))
    
    return duplicates

def get_duplicate_details(email: str) -> List[int]:
    """Get IDs of duplicate leads"""
    query = f"SELECT id FROM leads WHERE email = '{email}' ORDER BY created_at"
    
    exit_code, output = run_query(query)
    
    if exit_code != 0:
        return []
    
    ids = []
    for line in output.split('\n'):
        if line.strip().isdigit():
            ids.append(int(line.strip()))
    
    return ids

def delete_duplicates(email: str, keep_id: int) -> bool:
    """Delete duplicate leads, keeping the oldest one"""
    query = f"DELETE FROM leads WHERE email = '{email}' AND id != {keep_id}"
    
    exit_code, output = run_query(query)
    return exit_code == 0

def main():
    parser = argparse.ArgumentParser(description='Detect and optionally fix duplicate leads')
    parser.add_argument('--fix', action='store_true', help='Automatically delete duplicates (keeps oldest)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without deleting')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔍 Duplicate Lead Detector")
    print("=" * 60)
    print()
    
    print("Scanning for duplicate emails...")
    duplicates = find_duplicates()
    
    if not duplicates:
        print(f"{Colors.GREEN}✓ No duplicates found!{Colors.RESET}")
        print("=" * 60)
        return 0
    
    print(f"\n{Colors.YELLOW}⚠ Found {len(duplicates)} duplicate email(s):{Colors.RESET}\n")
    
    total_duplicates = 0
    for email, count in duplicates:
        total_duplicates += (count - 1)  # Don't count the one we keep
        print(f"  {Colors.RED}•{Colors.RESET} {email}: {count} occurrences")
        
        # Show IDs
        ids = get_duplicate_details(email)
        if ids:
            print(f"    IDs: {', '.join(map(str, ids))}")
            if args.fix or args.dry_run:
                keep_id = ids[0]  # Keep the oldest (first created)
                delete_ids = ids[1:]
                if args.dry_run:
                    print(f"    {Colors.YELLOW}[DRY RUN] Would keep ID {keep_id}, delete: {', '.join(map(str, delete_ids))}{Colors.RESET}")
                elif args.fix:
                    print(f"    Keeping ID {keep_id}, deleting {len(delete_ids)} duplicate(s)...", end=" ")
                    if delete_duplicates(email, keep_id):
                        print(f"{Colors.GREEN}✓{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}✗ Failed{Colors.RESET}")
        print()
    
    print("=" * 60)
    print(f"Total duplicate records: {total_duplicates}")
    
    if not args.fix and not args.dry_run:
        print(f"\n{Colors.YELLOW}To automatically fix duplicates, run:{Colors.RESET}")
        print(f"  python {sys.argv[0]} --dry-run  # Preview changes")
        print(f"  python {sys.argv[0]} --fix      # Apply fixes")
    
    print("=" * 60)
    return 1  # Return non-zero if duplicates found

if __name__ == "__main__":
    sys.exit(main())
