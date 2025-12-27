"""
Whois/DNS Plugin - Domain Ownership and DNS Information

This plugin provides:
- Domain ownership information
- DNS records lookup (A, MX, NS, TXT, CNAME, AAAA)
- IP reverse lookup
- DNSSEC information
"""

import logging
import socket
import time
import dns.resolver
import dns.exception
from typing import Dict, List, Any, Optional
from .base_plugin import BasePlugin, PluginResult

try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False


class WhoisPlugin(BasePlugin):
    """Plugin for domain ownership and DNS information"""
    
    @property
    def description(self) -> str:
        return "Domain ownership and DNS records lookup (A, MX, NS, TXT, etc.)"
    
    @property
    def search_types(self) -> List[str]:
        return ['domain', 'ip']
    
    def search(self, query: str, search_type: str = 'domain', **kwargs) -> PluginResult:
        """
        Get whois and DNS information for a domain or IP
        
        Args:
            query: Domain name or IP address
            search_type: Type of search ('domain' or 'ip')
            **kwargs: Additional parameters (dns_servers, timeout, record_types)
            
        Returns:
            PluginResult with whois and DNS data
        """
        start_time = time.time()
        
        try:
            # Get parameters
            timeout = kwargs.get('timeout', 10)
            record_types = kwargs.get('record_types', ['A', 'MX', 'NS', 'TXT', 'CNAME', 'AAAA'])
            dns_servers = kwargs.get('dns_servers', None)
            
            self.log_info(f"Starting Whois/DNS lookup for {query} (type: {search_type})")
            
            # Normalize query
            query = query.strip()
            
            # Perform search based on type
            if search_type == 'domain':
                data = self._search_domain(query, timeout, record_types, dns_servers)
            elif search_type == 'ip':
                data = self._search_ip(query, timeout)
            else:
                raise ValueError(f"Unsupported search type: {search_type}")
            
            execution_time = time.time() - start_time
            
            self.log_info(f"Whois/DNS lookup completed successfully")
            
            return PluginResult(
                source=self.name,
                search_type=search_type,
                query=query,
                data=[data],
                metadata={'whois_available': WHOIS_AVAILABLE},
                success=True,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_error(f"Whois/DNS lookup failed: {str(e)}")
            return PluginResult(
                source=self.name,
                search_type=search_type,
                query=query,
                data=[],
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _search_domain(self, domain: str, timeout: int, record_types: List[str], 
                      dns_servers: Optional[List[str]]) -> Dict[str, Any]:
        """Search for domain information"""
        domain = domain.lower()
        
        # Get whois information
        whois_info = self._get_whois(domain)
        
        # Get DNS records
        dns_records = {}
        for record_type in record_types:
            try:
                records = self._get_dns_records(domain, record_type, dns_servers, timeout)
                if records:
                    dns_records[record_type] = records
            except Exception as e:
                self.log_warning(f"Failed to get {record_type} records: {str(e)}")
        
        # Get DNSSEC info
        dnssec_enabled = self._check_dnssec(domain, dns_servers)
        
        # Resolve IP addresses
        ip_addresses = self._resolve_ip_addresses(domain, dns_servers)
        
        # Get reverse DNS for IPs
        reverse_dns = {}
        for ip in ip_addresses[:5]:  # Limit to first 5 IPs
            reverse_dns[ip] = self._get_reverse_dns(ip, dns_servers)
        
        return {
            'query_type': 'domain',
            'query': domain,
            'whois': whois_info,
            'dns_records': dns_records,
            'ip_addresses': ip_addresses,
            'reverse_dns': reverse_dns,
            'dnssec_enabled': dnssec_enabled,
            'summary': {
                'registrar': whois_info.get('registrar', 'Unknown'),
                'creation_date': str(whois_info.get('creation_date', 'Unknown')),
                'expiration_date': str(whois_info.get('expiration_date', 'Unknown')),
                'nameservers': dns_records.get('NS', []),
                'mail_servers': dns_records.get('MX', [])
            }
        }
    
    def _search_ip(self, ip: str, timeout: int) -> Dict[str, Any]:
        """Search for IP information"""
        # Validate IP
        try:
            socket.inet_aton(ip)
        except socket.error:
            raise ValueError(f"Invalid IP address: {ip}")
        
        # Get reverse DNS
        reverse_dns = self._get_reverse_dns(ip)
        
        # Try to get whois for IP (if available)
        whois_info = {}
        if WHOIS_AVAILABLE:
            try:
                w = whois.whois(ip)
                whois_info = {
                    'org': w.org if w.org else '',
                    'netname': w.netname if w.netname else '',
                    'country': w.country if w.country else '',
                    'description': w.description if w.description else ''
                }
            except Exception as e:
                self.log_warning(f"Failed to get whois for IP {ip}: {str(e)}")
        
        return {
            'query_type': 'ip',
            'query': ip,
            'reverse_dns': reverse_dns,
            'whois': whois_info,
            'geolocation': self._get_geolocation(ip)
        }
    
    def _get_whois(self, domain: str) -> Dict[str, Any]:
        """Get whois information for a domain"""
        if not WHOIS_AVAILABLE:
            return {
                'error': 'python-whois module not installed',
                'note': 'Install with: pip install python-whois'
            }
        
        try:
            w = whois.whois(domain)
            
            # Handle different whois response formats
            def safe_get(attr):
                value = getattr(w, attr, None)
                if isinstance(value, list):
                    return value[0] if len(value) == 1 else value
                return value if value else ''
            
            return {
                'domain_name': safe_get('domain_name'),
                'registrar': safe_get('registrar'),
                'creation_date': str(safe_get('creation_date')) if safe_get('creation_date') else '',
                'expiration_date': str(safe_get('expiration_date')) if safe_get('expiration_date') else '',
                'updated_date': str(safe_get('last_updated')) if safe_get('last_updated') else '',
                'name_servers': safe_get('name_servers') or [],
                'status': safe_get('status') or [],
                'registrant_name': safe_get('registrant_name'),
                'registrant_org': safe_get('registrant_org'),
                'registrant_country': safe_get('registrant_country'),
                'admin_email': safe_get('admin_email'),
                'tech_email': safe_get('tech_email'),
                'dnssec': safe_get('dnssec')
            }
        except Exception as e:
            self.log_warning(f"Failed to get whois for {domain}: {str(e)}")
            return {'error': str(e)}
    
    def _get_dns_records(self, domain: str, record_type: str, 
                        dns_servers: Optional[List[str]], timeout: int) -> List[str]:
        """Get DNS records for a domain"""
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout
        
        if dns_servers:
            resolver.nameservers = dns_servers
        
        try:
            answers = resolver.resolve(domain, record_type)
            records = []
            
            for rdata in answers:
                if record_type == 'MX':
                    records.append(f"{rdata.preference} {rdata.exchange}")
                elif record_type == 'TXT':
                    records.append(rdata.to_text().strip('"'))
                elif record_type == 'SOA':
                    records.append(f"{rdata.mname} {rdata.rname}")
                else:
                    records.append(rdata.to_text())
            
            return records
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            return []
        except dns.exception.DNSException as e:
            self.log_warning(f"DNS query failed for {record_type}: {str(e)}")
            return []
    
    def _check_dnssec(self, domain: str, dns_servers: Optional[List[str]]) -> bool:
        """Check if DNSSEC is enabled for a domain"""
        resolver = dns.resolver.Resolver()
        
        if dns_servers:
            resolver.nameservers = dns_servers
        
        try:
            # Try to get DNSKEY records
            resolver.resolve(domain, 'DNSKEY')
            return True
        except:
            return False
    
    def _resolve_ip_addresses(self, domain: str, dns_servers: Optional[List[str]]) -> List[str]:
        """Resolve IP addresses for a domain"""
        resolver = dns.resolver.Resolver()
        
        if dns_servers:
            resolver.nameservers = dns_servers
        
        ips = []
        
        # Try A records (IPv4)
        try:
            answers = resolver.resolve(domain, 'A')
            for rdata in answers:
                ips.append(rdata.to_text())
        except:
            pass
        
        # Try AAAA records (IPv6)
        try:
            answers = resolver.resolve(domain, 'AAAA')
            for rdata in answers:
                ips.append(rdata.to_text())
        except:
            pass
        
        return ips
    
    def _get_reverse_dns(self, ip: str, dns_servers: Optional[List[str]] = None) -> str:
        """Get reverse DNS for an IP address"""
        resolver = dns.resolver.Resolver()
        
        if dns_servers:
            resolver.nameservers = dns_servers
        
        try:
            # Reverse the IP for PTR lookup
            reversed_ip = dns.reversename.from_address(ip)
            answers = resolver.resolve(reversed_ip, 'PTR')
            return str(answers[0])
        except:
            return ''
    
    def _get_geolocation(self, ip: str) -> Dict[str, Any]:
        """Get geolocation information for an IP (basic implementation)"""
        # This is a placeholder. For full functionality, you would use a geolocation API
        # like ipinfo.io, maxmind, or similar
        
        return {
            'note': 'Geolocation requires an external API service',
            'suggestion': 'Use Shodan plugin for IP geolocation'
        }
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        if not WHOIS_AVAILABLE:
            self.log_warning("python-whois module not installed. Whois functionality will be limited.")
            return False
        return True
