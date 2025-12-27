"""
Shodan Plugin - IP/Device Intelligence and Metadata

This plugin provides:
- IP and device intelligence
- Service and vulnerability detection
- Network infrastructure analysis
- Requires API key configuration
"""

import logging
import requests
import time
from typing import Dict, List, Any, Optional
from .base_plugin import BasePlugin, PluginResult


class ShodanPlugin(BasePlugin):
    """Plugin for IP and device intelligence using Shodan API"""
    
    SHODAN_API_URL = "https://api.shodan.io"
    
    @property
    def description(self) -> str:
        return "IP/device intelligence and metadata using Shodan API (requires API key)"
    
    @property
    def search_types(self) -> List[str]:
        return ['ip', 'domain', 'net']
    
    def search(self, query: str, search_type: str = 'ip', **kwargs) -> PluginResult:
        """
        Search Shodan for IP/domain information
        
        Args:
            query: IP address, domain, or network range
            search_type: Type of search ('ip', 'domain', 'net')
            **kwargs: Additional parameters (minify, history, timeout)
            
        Returns:
            PluginResult with Shodan data
        """
        start_time = time.time()
        
        try:
            # Get API key from config
            api_key = self._get_api_key()
            if not api_key:
                return PluginResult(
                    source=self.name,
                    search_type=search_type,
                    query=query,
                    data=[],
                    success=False,
                    error_message="Shodan API key not configured. Please add it to config/plugin_config.json",
                    execution_time=time.time() - start_time
                )
            
            # Get parameters
            timeout = kwargs.get('timeout', 10)
            minify = kwargs.get('minify', False)
            history = kwargs.get('history', False)
            
            self.log_info(f"Searching Shodan for {query} (type: {search_type})")
            
            # Normalize query
            query = query.strip()
            
            # Perform search based on type
            if search_type == 'ip':
                data = self._search_ip(query, api_key, timeout, minify, history)
            elif search_type == 'domain':
                data = self._search_domain(query, api_key, timeout)
            elif search_type == 'net':
                data = self._search_net(query, api_key, timeout)
            else:
                raise ValueError(f"Unsupported search type: {search_type}")
            
            execution_time = time.time() - start_time
            
            self.log_info(f"Shodan search completed successfully")
            
            return PluginResult(
                source=self.name,
                search_type=search_type,
                query=query,
                data=[data],
                metadata={'api_version': '1.0'},
                success=True,
                execution_time=execution_time
            )
            
        except requests.exceptions.RequestException as e:
            execution_time = time.time() - start_time
            self.log_error(f"Shodan API request failed: {str(e)}")
            return PluginResult(
                source=self.name,
                search_type=search_type,
                query=query,
                data=[],
                success=False,
                error_message=f"API request failed: {str(e)}",
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_error(f"Shodan search failed: {str(e)}")
            return PluginResult(
                source=self.name,
                search_type=search_type,
                query=query,
                data=[],
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _get_api_key(self) -> Optional[str]:
        """Get Shodan API key from config"""
        # Try to get from plugin config
        api_key = self.get_config_value('api_key')
        if api_key:
            return api_key
        
        # Try environment variable
        import os
        return os.environ.get('SHODAN_API_KEY')
    
    def _search_ip(self, ip: str, api_key: str, timeout: int, minify: bool, history: bool) -> Dict[str, Any]:
        """Search for a specific IP address"""
        url = f"{self.SHODAN_API_URL}/shodan/host/{ip}?key={api_key}"
        
        if minify:
            url += "&minify=true"
        if history:
            url += "&history=true"
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        result = response.json()
        
        # Structure the results
        data = {
            'query_type': 'ip',
            'query': ip,
            'ip': result.get('ip_str', ip),
            'hostnames': result.get('hostnames', []),
            'country_name': result.get('country_name', ''),
            'country_code': result.get('country_code', ''),
            'city': result.get('city', ''),
            'org': result.get('org', ''),
            'isp': result.get('isp', ''),
            'asn': result.get('asn', ''),
            'latitude': result.get('latitude', None),
            'longitude': result.get('longitude', None),
            'ports': result.get('ports', []),
            'vulns': result.get('vulns', []),
            'os': result.get('os', ''),
            'uptime': result.get('uptime', None),
            'last_update': result.get('last_update', ''),
            'services': result.get('data', [])
        }
        
        return data
    
    def _search_domain(self, domain: str, api_key: str, timeout: int) -> Dict[str, Any]:
        """Search for domain information"""
        # First, resolve the domain to IPs
        url = f"{self.SHODAN_API_URL}/dns/resolve?hostnames={domain}&key={api_key}"
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        resolve_result = response.json()
        ips = resolve_result.get(domain, [])
        
        if not ips:
            return {
                'query_type': 'domain',
                'query': domain,
                'ips': [],
                'message': 'No IPs found for domain'
            }
        
        # Get information for each IP
        services = []
        for ip in ips[:5]:  # Limit to first 5 IPs
            try:
                ip_info = self._search_ip(ip, api_key, timeout, minify=True, history=False)
                services.append(ip_info)
            except Exception as e:
                self.log_warning(f"Failed to get info for {ip}: {str(e)}")
        
        return {
            'query_type': 'domain',
            'query': domain,
            'ips': ips,
            'services': services
        }
    
    def _search_net(self, network: str, api_key: str, timeout: int) -> Dict[str, Any]:
        """Search for a network range"""
        # Search Shodan for hosts in the network
        url = f"{self.SHODAN_API_URL}/shodan/host/search?key={api_key}&facets=port,country"
        url += f"&query=net:{network}"
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        result = response.json()
        
        return {
            'query_type': 'net',
            'query': network,
            'total': result.get('total', 0),
            'matches': result.get('matches', []),
            'facets': result.get('facets', {})
        }
    
    def validate_config(self) -> bool:
        """Validate that API key is configured"""
        api_key = self._get_api_key()
        if not api_key:
            self.log_warning("Shodan API key not configured")
            return False
        return True
