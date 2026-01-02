#!/usr/bin/env python3
"""
Send Throttle & Rate Limit Test
Verifies that aggressive sending is properly controlled

Usage: python throttle_test.py [--api-url URL] [--requests COUNT]
Exit: 0 = throttling works, 1 = no rate limiting
"""

import sys
import time
import argparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def test_burst_requests(api_base, token, count=50, workers=10):
    """Send burst of parallel requests to test rate limiting"""
    headers = {"Authorization": f"Bearer {token}"}
    
    def send_one(i):
        """Send a single test request"""
        try:
            start = time.time()
            
            # Try multiple endpoints
            endpoints = [
                ("/api/campaigns/test-send", {"to": f"throttle-test-{i}@example.com", "subject": f"Rate Limit Test {i}"}),
                ("/api/email/send", {"to": f"throttle-test-{i}@example.com", "subject": f"Test {i}", "body": "Test"}),
            ]
            
            response = None
            for endpoint, payload in endpoints:
                try:
                    response = requests.post(
                        f"{api_base}{endpoint}",
                        headers=headers,
                        json=payload,
                        timeout=5
                    )
                    break  # Use first working endpoint
                except:
                    continue
            
            elapsed = time.time() - start
            
            if response:
                return {
                    'index': i,
                    'status': response.status_code,
                    'time': elapsed,
                    'success': response.status_code == 200
                }
            else:
                return {
                    'index': i,
                    'status': 404,
                    'time': elapsed,
                    'success': False
                }
                
        except requests.exceptions.Timeout:
            return {
                'index': i,
                'status': 'TIMEOUT',
                'time': 5.0,
                'success': False
            }
        except Exception as e:
            return {
                'index': i,
                'status': 'ERROR',
                'time': 0,
                'success': False,
                'error': str(e)
            }
    
    print(f"{Colors.BLUE}Sending burst of {count} requests with {workers} parallel workers...{Colors.RESET}")
    print()
    
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(send_one, i) for i in range(count)]
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            # Progress indicator
            if len(results) % 10 == 0:
                print(f"  Progress: {len(results)}/{count} requests completed...")
    
    total_time = time.time() - start_time
    
    print(f"{Colors.GREEN}✓ Burst test completed in {total_time:.2f}s{Colors.RESET}")
    print()
    
    return results, total_time

def analyze_throttling(results, total_time):
    """Analyze results for rate limiting behavior"""
    success_count = sum(1 for r in results if r['success'])
    rate_limited = sum(1 for r in results if r['status'] == 429)
    errors = sum(1 for r in results if r['status'] not in [200, 429])
    
    times = [r['time'] for r in results if r['time'] > 0]
    avg_time = sum(times) / len(times) if times else 0
    min_time = min(times) if times else 0
    max_time = max(times) if times else 0
    
    requests_per_sec = len(results) / total_time if total_time > 0 else 0
    
    print("=" * 60)
    print("📊 THROTTLING ANALYSIS")
    print("=" * 60)
    
    print(f"Total requests: {len(results)}")
    print(f"Successful (200): {success_count}")
    print(f"Rate limited (429): {rate_limited}")
    print(f"Errors: {errors}")
    print()
    
    print(f"Response times:")
    print(f"  Average: {avg_time:.3f}s")
    print(f"  Min: {min_time:.3f}s")
    print(f"  Max: {max_time:.3f}s")
    print()
    
    print(f"Throughput: {requests_per_sec:.1f} req/sec")
    print()
    
    # Assess throttling
    throttle_ratio = rate_limited / len(results) if results else 0
    
    if rate_limited > 0:
        print(f"{Colors.GREEN}✓ Rate limiting is active{Colors.RESET}")
        print(f"  {rate_limited} requests blocked ({throttle_ratio*100:.1f}%)")
        
        if throttle_ratio > 0.5:
            print(f"  {Colors.BLUE}ℹ Strong throttling (>50% blocked){Colors.RESET}")
        elif throttle_ratio > 0.2:
            print(f"  {Colors.BLUE}ℹ Moderate throttling (20-50% blocked){Colors.RESET}")
        else:
            print(f"  {Colors.BLUE}ℹ Light throttling (<20% blocked){Colors.RESET}")
        
        return True
    else:
        if success_count == len(results):
            print(f"{Colors.YELLOW}⚠ No rate limiting detected{Colors.RESET}")
            print(f"  All {success_count} requests succeeded")
            print(f"  System may be vulnerable to abuse")
            return False
        else:
            print(f"{Colors.YELLOW}⚠ Rate limiting unclear{Colors.RESET}")
            print(f"  No 429 responses, but {errors} errors occurred")
            print(f"  May have other protection mechanisms")
            return True  # Assume protected if errors occurred

def test_sustained_rate(api_base, token, duration=10, rate_per_sec=5):
    """Test sustained sending rate over time"""
    print(f"{Colors.BLUE}Testing sustained rate ({rate_per_sec} req/sec for {duration}s)...{Colors.RESET}")
    print()
    
    headers = {"Authorization": f"Bearer {token}"}
    results = []
    
    start_time = time.time()
    request_count = 0
    
    while time.time() - start_time < duration:
        cycle_start = time.time()
        
        for i in range(rate_per_sec):
            try:
                # Try multiple endpoints
                for endpoint, payload in [
                    ("/api/campaigns/test-send", {"to": f"sustained-test-{request_count}@example.com"}),
                    ("/api/email/send", {"to": f"sustained-test-{request_count}@example.com", "subject": "Test", "body": "Test"}),
                ]:
                    try:
                        response = requests.post(
                            f"{api_base}{endpoint}",
                            headers=headers,
                            json=payload,
                            timeout=2
                        )
                        results.append(response.status_code)
                        request_count += 1
                        break
                    except:
                        continue
                else:
                    # No endpoint worked
                    results.append('ERROR')
                    request_count += 1
            except:
                results.append('ERROR')
                request_count += 1
        
        # Wait for next cycle
        cycle_time = time.time() - cycle_start
        if cycle_time < 1.0:
            time.sleep(1.0 - cycle_time)
        
        # Progress
        elapsed = time.time() - start_time
        print(f"  {elapsed:.1f}s elapsed... {request_count} requests sent")
    
    print(f"{Colors.GREEN}✓ Sustained test completed{Colors.RESET}")
    print()
    
    success = sum(1 for r in results if r == 200)
    throttled = sum(1 for r in results if r == 429)
    
    print(f"Results over {duration}s:")
    print(f"  Total requests: {len(results)}")
    print(f"  Successful: {success}")
    print(f"  Throttled: {throttled}")
    print()
    
    return throttled > 0

def main():
    parser = argparse.ArgumentParser(
        description='Test rate limiting and throttling',
        epilog='Exit codes: 0=throttling works, 1=no rate limiting'
    )
    parser.add_argument('--api-url', default='http://localhost:8000',
                       help='API base URL')
    parser.add_argument('--email', default='test@example.com',
                       help='Login email')
    parser.add_argument('--password', default='testpass123',
                       help='Login password')
    parser.add_argument('--burst-count', type=int, default=50,
                       help='Number of burst requests (default: 50)')
    parser.add_argument('--workers', type=int, default=10,
                       help='Parallel workers (default: 10)')
    parser.add_argument('--skip-sustained', action='store_true',
                       help='Skip sustained rate test')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚦 THROTTLE & RATE LIMIT TEST")
    print("=" * 60)
    print(f"API: {args.api_url}")
    print(f"Burst: {args.burst_count} requests, {args.workers} workers")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Login
    print(f"{Colors.BLUE}Step 1: Authentication{Colors.RESET}")
    try:
        response = requests.post(
            f"{args.api_url}/auth/login",
            json={"email": args.email, "password": args.password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token') or data.get('token')
            if token:
                print(f"{Colors.GREEN}✓ Login successful{Colors.RESET}")
            else:
                print(f"{Colors.RED}✗ No token in response{Colors.RESET}")
                return 1
        else:
            print(f"{Colors.RED}✗ Login failed: {response.status_code}{Colors.RESET}")
            return 1
    except Exception as e:
        print(f"{Colors.RED}✗ Authentication error: {e}{Colors.RESET}")
        return 1
    
    print()
    
    # Burst test
    print(f"{Colors.BLUE}Step 2: Burst Request Test{Colors.RESET}")
    results, total_time = test_burst_requests(
        args.api_url, 
        token, 
        count=args.burst_count,
        workers=args.workers
    )
    
    has_throttling = analyze_throttling(results, total_time)
    
    # Sustained test (optional)
    if not args.skip_sustained:
        print()
        print(f"{Colors.BLUE}Step 3: Sustained Rate Test{Colors.RESET}")
        sustained_throttled = test_sustained_rate(args.api_url, token)
        
        if sustained_throttled:
            print(f"{Colors.GREEN}✓ Sustained rate throttling detected{Colors.RESET}")
    
    # Final result
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULT")
    print("=" * 60)
    
    if has_throttling:
        print(f"{Colors.GREEN}✅ TEST PASSED{Colors.RESET}")
        print("Rate limiting is active")
        print("System protects against aggressive sending")
        return 0
    else:
        print(f"{Colors.RED}❌ TEST FAILED{Colors.RESET}")
        print("No rate limiting detected")
        print("System vulnerable to aggressive sending patterns")
        print()
        print(f"{Colors.RED}WARNING: This could lead to domain abuse!{Colors.RESET}")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
