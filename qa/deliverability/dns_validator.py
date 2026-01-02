#!/usr/bin/env python3
"""
DNS Validation Test Runner
Validates SPF, DKIM, DMARC detection accuracy

Usage: python dns_validator.py --domain example.com
Exit: 0 = all pass, 1 = failures detected
"""

import sys
import argparse

try:
    import dns.resolver
except ImportError:
    print("ERROR: dnspython not installed. Run: pip install dnspython")
    sys.exit(1)

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def check_spf(domain):
    """Check if SPF record exists and is valid"""
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        spf_records = []
        
        for rdata in answers:
            txt = str(rdata).strip('"')
            if txt.startswith('v=spf1'):
                spf_records.append(txt)
        
        if len(spf_records) == 0:
            print(f"{Colors.RED}✗ SPF Not Found{Colors.RESET}")
            return False
        elif len(spf_records) > 1:
            print(f"{Colors.RED}✗ Multiple SPF Records Found ({len(spf_records)}) - RFC VIOLATION{Colors.RESET}")
            for i, spf in enumerate(spf_records, 1):
                print(f"   SPF #{i}: {spf[:60]}...")
            return False
        else:
            spf = spf_records[0]
            print(f"{Colors.GREEN}✓ SPF Found{Colors.RESET}")
            print(f"   {spf[:80]}{'...' if len(spf) > 80 else ''}")
            
            # Check for common issues
            if ' -all' in spf:
                print(f"   {Colors.BLUE}ℹ Policy: Hard Fail (-all){Colors.RESET}")
            elif ' ~all' in spf:
                print(f"   {Colors.BLUE}ℹ Policy: Soft Fail (~all){Colors.RESET}")
            elif ' ?all' in spf:
                print(f"   {Colors.YELLOW}⚠ Policy: Neutral (?all) - Consider hardening{Colors.RESET}")
            
            return True
            
    except dns.resolver.NXDOMAIN:
        print(f"{Colors.RED}✗ Domain does not exist{Colors.RESET}")
        return False
    except dns.resolver.NoAnswer:
        print(f"{Colors.RED}✗ No TXT records found{Colors.RESET}")
        return False
    except Exception as e:
        print(f"{Colors.RED}✗ SPF Check Failed: {e}{Colors.RESET}")
        return False

def check_dkim(domain, selector='default'):
    """Check if DKIM record exists"""
    try:
        dkim_domain = f"{selector}._domainkey.{domain}"
        answers = dns.resolver.resolve(dkim_domain, 'TXT')
        
        for rdata in answers:
            txt = str(rdata).strip('"')
            if 'v=DKIM1' in txt or 'k=rsa' in txt or 'p=' in txt:
                print(f"{Colors.GREEN}✓ DKIM Found (selector: {selector}){Colors.RESET}")
                print(f"   {txt[:80]}{'...' if len(txt) > 80 else ''}")
                return True
        
        print(f"{Colors.YELLOW}⚠ DKIM record found but appears invalid (selector: {selector}){Colors.RESET}")
        return False
        
    except dns.resolver.NXDOMAIN:
        print(f"{Colors.YELLOW}⚠ DKIM Not Found (selector: {selector}){Colors.RESET}")
        print(f"   Checked: {selector}._domainkey.{domain}")
        return False
    except dns.resolver.NoAnswer:
        print(f"{Colors.YELLOW}⚠ DKIM Not Found (selector: {selector}){Colors.RESET}")
        return False
    except Exception as e:
        print(f"{Colors.YELLOW}⚠ DKIM Check (selector: {selector}): {e}{Colors.RESET}")
        return False

def check_dmarc(domain):
    """Check if DMARC record exists"""
    try:
        dmarc_domain = f"_dmarc.{domain}"
        answers = dns.resolver.resolve(dmarc_domain, 'TXT')
        
        for rdata in answers:
            txt = str(rdata).strip('"')
            if txt.startswith('v=DMARC1'):
                print(f"{Colors.GREEN}✓ DMARC Found{Colors.RESET}")
                print(f"   {txt[:80]}{'...' if len(txt) > 80 else ''}")
                
                # Parse policy
                if 'p=reject' in txt:
                    print(f"   {Colors.BLUE}ℹ Policy: Reject (Strict){Colors.RESET}")
                elif 'p=quarantine' in txt:
                    print(f"   {Colors.BLUE}ℹ Policy: Quarantine (Moderate){Colors.RESET}")
                elif 'p=none' in txt:
                    print(f"   {Colors.YELLOW}⚠ Policy: None (Monitor Only){Colors.RESET}")
                
                return True
        
        print(f"{Colors.YELLOW}⚠ DMARC Not Found (Recommended){Colors.RESET}")
        return False
        
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        print(f"{Colors.YELLOW}⚠ DMARC Not Found (Recommended){Colors.RESET}")
        return False
    except Exception as e:
        print(f"{Colors.YELLOW}⚠ DMARC Check Failed: {e}{Colors.RESET}")
        return False

def check_mx(domain):
    """Check if MX records exist"""
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        mx_records = [(r.preference, str(r.exchange)) for r in answers]
        mx_records.sort()
        
        print(f"{Colors.GREEN}✓ MX Records Found ({len(mx_records)}){Colors.RESET}")
        for pref, mx in mx_records[:3]:
            print(f"   Priority {pref}: {mx}")
        if len(mx_records) > 3:
            print(f"   ... and {len(mx_records) - 3} more")
        
        return True
        
    except Exception as e:
        print(f"{Colors.RED}✗ MX Records Not Found: {e}{Colors.RESET}")
        return False

def assess_risk(results):
    """Assess overall deliverability risk"""
    spf_ok = results.get('SPF', False)
    dkim_ok = results.get('DKIM', False)
    dmarc_ok = results.get('DMARC', False)
    mx_ok = results.get('MX', False)
    
    print("\n" + "=" * 60)
    print("📊 RISK ASSESSMENT")
    print("=" * 60)
    
    # Critical issues
    if not spf_ok:
        print(f"{Colors.RED}🚨 HIGH RISK: SPF Missing{Colors.RESET}")
        print("   → Emails will likely be marked as spam")
        print("   → Domain reputation at risk")
        print("   → DO NOT SEND until SPF is configured")
        return "HIGH"
    
    if not mx_ok:
        print(f"{Colors.RED}🚨 HIGH RISK: No MX Records{Colors.RESET}")
        print("   → Cannot receive emails")
        return "HIGH"
    
    # Medium risk
    if not dkim_ok:
        print(f"{Colors.YELLOW}⚠ MEDIUM RISK: DKIM Missing{Colors.RESET}")
        print("   → Deliverability will be impacted")
        print("   → Configure DKIM before sending")
        return "MEDIUM"
    
    # Low risk
    if not dmarc_ok:
        print(f"{Colors.YELLOW}⚠ LOW RISK: DMARC Missing{Colors.RESET}")
        print("   → Recommended for better protection")
        print("   → Can send, but improve when possible")
        return "LOW"
    
    # All good
    print(f"{Colors.GREEN}✓ LOW RISK: Domain Properly Configured{Colors.RESET}")
    print("   → SPF, DKIM, DMARC all present")
    print("   → Safe to send")
    return "LOW"

def main():
    parser = argparse.ArgumentParser(
        description='Validate DNS records for email deliverability',
        epilog='Exit codes: 0=success, 1=critical issues found'
    )
    parser.add_argument('--domain', required=True, help='Domain to check')
    parser.add_argument('--dkim-selector', default='default', 
                       help='DKIM selector (default: default)')
    parser.add_argument('--additional-selectors', nargs='*', 
                       help='Additional DKIM selectors to check')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"🔍 DNS VALIDATION TEST")
    print(f"Domain: {args.domain}")
    print("=" * 60)
    print()
    
    results = {}
    
    # Run checks
    print(f"{Colors.BLUE}Checking SPF...{Colors.RESET}")
    results['SPF'] = check_spf(args.domain)
    print()
    
    print(f"{Colors.BLUE}Checking DKIM (selector: {args.dkim_selector})...{Colors.RESET}")
    results['DKIM'] = check_dkim(args.domain, args.dkim_selector)
    
    # Try additional selectors
    if args.additional_selectors:
        for selector in args.additional_selectors:
            print(f"{Colors.BLUE}Checking DKIM (selector: {selector})...{Colors.RESET}")
            if check_dkim(args.domain, selector):
                results['DKIM'] = True
    
    # Try common selectors if primary failed
    if not results['DKIM']:
        for common_selector in ['google', 'k1', 's1', 'mail', 'smtp']:
            if common_selector != args.dkim_selector:
                print(f"{Colors.BLUE}Trying common selector: {common_selector}...{Colors.RESET}")
                if check_dkim(args.domain, common_selector):
                    results['DKIM'] = True
                    break
    print()
    
    print(f"{Colors.BLUE}Checking DMARC...{Colors.RESET}")
    results['DMARC'] = check_dmarc(args.domain)
    print()
    
    print(f"{Colors.BLUE}Checking MX Records...{Colors.RESET}")
    results['MX'] = check_mx(args.domain)
    print()
    
    # Risk assessment
    risk = assess_risk(results)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Checks passed: {passed}/{total}")
    print(f"Overall risk: {risk}")
    print()
    
    # Exit code
    if risk == "HIGH":
        print(f"{Colors.RED}❌ CRITICAL ISSUES - NOT READY FOR SENDING{Colors.RESET}")
        return 1
    elif risk == "MEDIUM":
        print(f"{Colors.YELLOW}⚠ ISSUES FOUND - IMPROVE BEFORE SENDING{Colors.RESET}")
        return 1
    else:
        print(f"{Colors.GREEN}✅ DOMAIN READY FOR SENDING{Colors.RESET}")
        return 0

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
