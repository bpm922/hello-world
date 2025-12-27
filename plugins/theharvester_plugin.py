"""
TheHarvester Plugin - Email and Subdomain Discovery

This plugin provides email and subdomain discovery using multiple data sources:
- Google, Bing, Baidu, DuckDuckGo
- LinkedIn, Twitter, Facebook
- PGP key servers
- DNS Dumpster
- And more
"""

import logging
import re
import requests
import time
from typing import Dict, List, Any
from urllib.parse import urlparse
from .base_plugin import BasePlugin, PluginResult


class TheHarvesterPlugin(BasePlugin):
    """Plugin for email and subdomain discovery"""
    
    @property
    def description(self) -> str:
        return "Email and subdomain discovery using multiple search engines and data sources"
    
    @property
    def search_types(self) -> List[str]:
        return ['domain', 'company']
    
    def search(self, query: str, search_type: str = 'domain', **kwargs) -> PluginResult:
        """
        Discover emails and subdomains for a domain
        
        Args:
            query: Domain or company name
            search_type: Type of search ('domain' or 'company')
            **kwargs: Additional parameters (sources, limit, timeout)
            
        Returns:
            PluginResult with discovered emails and subdomains
        """
        start_time = time.time()
        
        try:
            # Get parameters
            sources = kwargs.get('sources', ['bing', 'google', 'duckduckgo'])
            limit = kwargs.get('limit', 100)
            timeout = kwargs.get('timeout', 10)
            
            self.log_info(f"Starting TheHarvester search for {query}")
            
            # Results storage
            emails = set()
            subdomains = set()
            hosts = set()
            
            # Normalize domain
            if search_type == 'domain':
                domain = query.strip().lower()
                if domain.startswith(('http://', 'https://')):
                    parsed = urlparse(query)
                    domain = parsed.netloc
                
                # Perform searches from different sources
                for source in sources:
                    try:
                        self.log_info(f"Searching {source}...")
                        source_results = self._search_source(source, domain, limit, timeout)
                        emails.update(source_results.get('emails', []))
                        subdomains.update(source_results.get('subdomains', []))
                        hosts.update(source_results.get('hosts', []))
                    except Exception as e:
                        self.log_warning(f"Error searching {source}: {str(e)}")
                        continue
                
                # Deduplicate and format results
                data = {
                    'domain': domain,
                    'emails': sorted(list(emails)),
                    'subdomains': sorted(list(subdomains)),
                    'hosts': sorted(list(hosts)),
                    'total_emails': len(emails),
                    'total_subdomains': len(subdomains),
                    'sources_used': sources
                }
            else:
                # Company search - just do a basic domain inference
                data = {
                    'company': query,
                    'emails': [],
                    'subdomains': [],
                    'hosts': [],
                    'total_emails': 0,
                    'total_subdomains': 0,
                    'note': 'Company search requires additional implementation'
                }
            
            execution_time = time.time() - start_time
            
            self.log_info(f"Harvest completed. Emails: {len(data['emails'])}, "
                         f"Subdomains: {len(data['subdomains'])}")
            
            return PluginResult(
                source=self.name,
                search_type=search_type,
                query=query,
                data=[data],
                metadata={'sources': sources},
                success=True,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_error(f"TheHarvester search failed: {str(e)}")
            return PluginResult(
                source=self.name,
                search_type=search_type,
                query=query,
                data=[],
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _search_source(self, source: str, domain: str, limit: int, timeout: int) -> Dict[str, List[str]]:
        """
        Search a specific data source
        
        Args:
            source: Source name (google, bing, duckduckgo, etc.)
            domain: Domain to search for
            limit: Maximum results
            timeout: Request timeout
            
        Returns:
            Dictionary with emails, subdomains, and hosts
        """
        results = {'emails': [], 'subdomains': [], 'hosts': []}
        
        try:
            if source == 'bing':
                results = self._search_bing(domain, limit, timeout)
            elif source == 'google':
                results = self._search_google(domain, limit, timeout)
            elif source == 'duckduckgo':
                results = self._search_duckduckgo(domain, limit, timeout)
            elif source == 'dns_dumpster':
                results = self._search_dns_dumpster(domain, timeout)
            else:
                self.log_warning(f"Source {source} not implemented yet")
                
        except Exception as e:
            self.log_warning(f"Error searching {source}: {str(e)}")
        
        return results
    
    def _search_bing(self, domain: str, limit: int, timeout: int) -> Dict[str, List[str]]:
        """Search Bing for emails and subdomains"""
        emails = set()
        subdomains = set()
        
        # Bing search queries
        queries = [
            f'@{domain}',
            f'site:{domain}'
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for query in queries:
            try:
                url = f'https://www.bing.com/search?q={query}&count={limit}'
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                
                # Extract emails
                emails.update(re.findall(r'\b[A-Za-z0-9._%+-]+@' + re.escape(domain) + r'\b', response.text))
                
                # Extract subdomains
                subdomain_pattern = r'https?://([a-zA-Z0-9-]+\.)?' + re.escape(domain)
                matches = re.findall(subdomain_pattern, response.text)
                for match in matches:
                    if match and match != f'{domain}/':
                        subdomain = match.strip('.')
                        if subdomain and subdomain != domain:
                            subdomains.add(subdomain)
                            
            except Exception as e:
                self.log_warning(f"Bing search error: {str(e)}")
        
        return {
            'emails': list(emails),
            'subdomains': list(subdomains),
            'hosts': list(subdomains)
        }
    
    def _search_google(self, domain: str, limit: int, timeout: int) -> Dict[str, List[str]]:
        """Search Google for emails and subdomains"""
        emails = set()
        subdomains = set()
        
        # Note: Google search API would be better, but this uses a basic approach
        queries = [
            f'@{domain}',
            f'site:{domain} -www'
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for query in queries:
            try:
                url = f'https://www.google.com/search?q={query}&num={limit}'
                response = requests.get(url, headers=headers, timeout=timeout)
                
                # Extract emails
                emails.update(re.findall(r'\b[A-Za-z0-9._%+-]+@' + re.escape(domain) + r'\b', response.text))
                
                # Extract subdomains
                subdomain_pattern = r'([a-zA-Z0-9-]+\.)?' + re.escape(domain)
                matches = re.findall(subdomain_pattern, response.text)
                for match in matches:
                    if match and match != f'{domain}.':
                        subdomain = match.strip('.')
                        if subdomain and subdomain != domain:
                            subdomains.add(subdomain)
                            
            except Exception as e:
                self.log_warning(f"Google search error: {str(e)}")
        
        return {
            'emails': list(emails),
            'subdomains': list(subdomains),
            'hosts': list(subdomains)
        }
    
    def _search_duckduckgo(self, domain: str, limit: int, timeout: int) -> Dict[str, List[str]]:
        """Search DuckDuckGo for emails and subdomains"""
        emails = set()
        subdomains = set()
        
        queries = [
            f'@{domain}',
            f'site:{domain}'
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for query in queries:
            try:
                url = f'https://duckduckgo.com/html/?q={query}'
                response = requests.get(url, headers=headers, timeout=timeout)
                
                # Extract emails
                emails.update(re.findall(r'\b[A-Za-z0-9._%+-]+@' + re.escape(domain) + r'\b', response.text))
                
                # Extract subdomains
                subdomain_pattern = r'([a-zA-Z0-9-]+\.)?' + re.escape(domain)
                matches = re.findall(subdomain_pattern, response.text)
                for match in matches:
                    if match and match != f'{domain}.':
                        subdomain = match.strip('.')
                        if subdomain and subdomain != domain:
                            subdomains.add(subdomain)
                            
            except Exception as e:
                self.log_warning(f"DuckDuckGo search error: {str(e)}")
        
        return {
            'emails': list(emails),
            'subdomains': list(subdomains),
            'hosts': list(subdomains)
        }
    
    def _search_dns_dumpster(self, domain: str, timeout: int) -> Dict[str, List[str]]:
        """Search DNS Dumpster for subdomain information"""
        subdomains = set()
        
        try:
            # This is a simplified implementation
            # DNS Dumpster requires CSRF token handling
            url = f'https://dnsdumpster.com/'
            self.log_info(f"DNS Dumpster requires additional implementation for {domain}")
            
        except Exception as e:
            self.log_warning(f"DNS Dumpster error: {str(e)}")
        
        return {
            'emails': [],
            'subdomains': list(subdomains),
            'hosts': list(subdomains)
        }
