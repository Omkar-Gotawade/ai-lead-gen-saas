"""DNS Checker service for email deliverability verification.

Checks DNS records for email authentication:
- SPF (Sender Policy Framework)
- DKIM (DomainKeys Identified Mail)
- DMARC (Domain-based Message Authentication)

These records are critical for email deliverability and avoiding spam filters.
"""
from typing import Dict
import logging
import dns.resolver

logger = logging.getLogger(__name__)


class DNSCheckerService:
    """Service for checking email-related DNS records."""
    
    def __init__(self):
        """Initialize DNS checker."""
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 5
        self.resolver.lifetime = 5
    
    def check_domain(self, domain: str) -> Dict[str, any]:
        """Check all email-related DNS records for a domain.
        
        Args:
            domain: Domain to check (e.g., "example.com")
            
        Returns:
            Dict with check results:
            {
                'domain': str,
                'spf': {
                    'exists': bool,
                    'record': str or None,
                    'valid': bool,
                    'issues': List[str]
                },
                'dkim': {
                    'exists': bool,
                    'record': str or None,
                    'note': str
                },
                'dmarc': {
                    'exists': bool,
                    'record': str or None,
                    'policy': str or None,
                    'valid': bool,
                    'issues': List[str]
                },
                'mx': {
                    'exists': bool,
                    'records': List[str]
                },
                'overall_score': int (0-100),
                'recommendations': List[str]
            }
        """
        result = {
            'domain': domain,
            'spf': self.check_spf(domain),
            'dkim': self.check_dkim(domain),
            'dmarc': self.check_dmarc(domain),
            'mx': self.check_mx(domain),
            'overall_score': 0,
            'recommendations': []
        }
        
        # Calculate overall score
        result['overall_score'] = self._calculate_score(result)
        
        # Generate recommendations
        result['recommendations'] = self._generate_recommendations(result)
        
        return result
    
    def check_spf(self, domain: str) -> Dict[str, any]:
        """Check SPF record for a domain.
        
        Args:
            domain: Domain to check
            
        Returns:
            SPF check result dict
        """
        result = {
            'exists': False,
            'record': None,
            'valid': False,
            'issues': []
        }
        
        try:
            # Query TXT records
            answers = self.resolver.resolve(domain, 'TXT')
            
            # Find SPF record
            for rdata in answers:
                txt_string = rdata.to_text().strip('"')
                
                if txt_string.startswith('v=spf1'):
                    result['exists'] = True
                    result['record'] = txt_string
                    
                    # Basic validation
                    if 'all' in txt_string:
                        result['valid'] = True
                    else:
                        result['issues'].append('SPF record should end with an "all" mechanism')
                    
                    # Check for common issues
                    if txt_string.count('include:') > 10:
                        result['issues'].append('Too many includes (DNS lookup limit)')
                    
                    if '~all' in txt_string:
                        result['issues'].append('Using softfail (~all) - consider -all for stricter policy')
                    
                    break
            
            if not result['exists']:
                result['issues'].append('No SPF record found')
                
        except dns.resolver.NXDOMAIN:
            result['issues'].append('Domain does not exist')
        except dns.resolver.NoAnswer:
            result['issues'].append('No TXT records found')
        except Exception as e:
            logger.error(f"SPF check failed for {domain}: {str(e)}")
            result['issues'].append(f'Query failed: {str(e)}')
        
        return result
    
    def check_dkim(self, domain: str, selector: str = 'default') -> Dict[str, any]:
        """Check DKIM record for a domain.
        
        Note: DKIM requires knowing the selector, which varies by provider.
        This checks for common selectors: default, google, dkim, mail
        
        Args:
            domain: Domain to check
            selector: DKIM selector to check
            
        Returns:
            DKIM check result dict
        """
        result = {
            'exists': False,
            'record': None,
            'note': 'DKIM requires selector (varies by email provider)'
        }
        
        # Common selectors to try
        selectors = ['default', 'google', 'dkim', 'mail', 's1', 's2', 'k1', 'selector1', 'selector2']
        
        for sel in selectors:
            try:
                # DKIM record format: selector._domainkey.domain.com
                dkim_domain = f'{sel}._domainkey.{domain}'
                answers = self.resolver.resolve(dkim_domain, 'TXT')
                
                for rdata in answers:
                    txt_string = rdata.to_text().strip('"')
                    
                    if 'v=DKIM1' in txt_string or 'p=' in txt_string:
                        result['exists'] = True
                        result['record'] = f'{sel}._domainkey: {txt_string[:100]}...'
                        result['note'] = f'Found DKIM record with selector: {sel}'
                        return result
                        
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                continue
            except Exception as e:
                logger.debug(f"DKIM check failed for {sel}._domainkey.{domain}: {str(e)}")
                continue
        
        result['note'] = 'No DKIM record found with common selectors. Check your email provider settings.'
        return result
    
    def check_dmarc(self, domain: str) -> Dict[str, any]:
        """Check DMARC record for a domain.
        
        Args:
            domain: Domain to check
            
        Returns:
            DMARC check result dict
        """
        result = {
            'exists': False,
            'record': None,
            'policy': None,
            'valid': False,
            'issues': []
        }
        
        try:
            # DMARC record is at _dmarc.domain.com
            dmarc_domain = f'_dmarc.{domain}'
            answers = self.resolver.resolve(dmarc_domain, 'TXT')
            
            for rdata in answers:
                txt_string = rdata.to_text().strip('"')
                
                if txt_string.startswith('v=DMARC1'):
                    result['exists'] = True
                    result['record'] = txt_string
                    result['valid'] = True
                    
                    # Extract policy
                    if 'p=none' in txt_string:
                        result['policy'] = 'none'
                        result['issues'].append('DMARC policy is "none" (monitoring only)')
                    elif 'p=quarantine' in txt_string:
                        result['policy'] = 'quarantine'
                    elif 'p=reject' in txt_string:
                        result['policy'] = 'reject'
                    else:
                        result['issues'].append('No policy specified in DMARC record')
                    
                    # Check for reporting
                    if 'rua=' not in txt_string:
                        result['issues'].append('No aggregate reporting email (rua=) configured')
                    
                    break
            
            if not result['exists']:
                result['issues'].append('No DMARC record found')
                
        except dns.resolver.NXDOMAIN:
            result['issues'].append('No DMARC record found')
        except dns.resolver.NoAnswer:
            result['issues'].append('No DMARC record found')
        except Exception as e:
            logger.error(f"DMARC check failed for {domain}: {str(e)}")
            result['issues'].append(f'Query failed: {str(e)}')
        
        return result
    
    def check_mx(self, domain: str) -> Dict[str, any]:
        """Check MX records for a domain.
        
        Args:
            domain: Domain to check
            
        Returns:
            MX check result dict
        """
        result = {
            'exists': False,
            'records': []
        }
        
        try:
            answers = self.resolver.resolve(domain, 'MX')
            
            for rdata in answers:
                result['records'].append(f'{rdata.preference} {rdata.exchange}')
            
            if result['records']:
                result['exists'] = True
                
        except Exception as e:
            logger.error(f"MX check failed for {domain}: {str(e)}")
        
        return result
    
    def _calculate_score(self, check_result: Dict) -> int:
        """Calculate overall deliverability score.
        
        Args:
            check_result: Full check result
            
        Returns:
            Score from 0-100
        """
        score = 0
        
        # SPF: 30 points
        if check_result['spf']['exists']:
            score += 20
            if check_result['spf']['valid']:
                score += 10
        
        # DKIM: 25 points
        if check_result['dkim']['exists']:
            score += 25
        
        # DMARC: 30 points
        if check_result['dmarc']['exists']:
            score += 20
            if check_result['dmarc']['valid']:
                score += 10
        
        # MX: 15 points
        if check_result['mx']['exists']:
            score += 15
        
        return score
    
    def _generate_recommendations(self, check_result: Dict) -> list:
        """Generate recommendations based on check results.
        
        Args:
            check_result: Full check result
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if not check_result['spf']['exists']:
            recommendations.append('Add an SPF record to authorize your email servers')
        elif not check_result['spf']['valid']:
            recommendations.append('Fix SPF record issues: ' + ', '.join(check_result['spf']['issues']))
        
        if not check_result['dkim']['exists']:
            recommendations.append('Configure DKIM signing with your email provider')
        
        if not check_result['dmarc']['exists']:
            recommendations.append('Add a DMARC record to improve deliverability and get reports')
        elif check_result['dmarc']['policy'] == 'none':
            recommendations.append('Consider strengthening DMARC policy to "quarantine" or "reject"')
        
        if not check_result['mx']['exists']:
            recommendations.append('Add MX records to receive email')
        
        if not recommendations:
            recommendations.append('All critical DNS records are configured!')
        
        return recommendations


# Convenience function
def check_domain_dns(domain: str) -> Dict[str, any]:
    """Convenience function to check domain DNS records.
    
    Args:
        domain: Domain to check
        
    Returns:
        DNS check result dict
    """
    checker = DNSCheckerService()
    return checker.check_domain(domain)
