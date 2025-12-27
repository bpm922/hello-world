"""
Have I Been Pwned (HIBP) Plugin - Breach Data Search

This plugin provides:
- Email breach data search
- Username breach data search
- Compromised account detection
- Uses free HIBP API
"""

import logging
import hashlib
import requests
import time
from typing import Dict, List, Any
from .base_plugin import BasePlugin, PluginResult


class HIBPPlugin(BasePlugin):
    """Plugin for breach data search using Have I Been Pwned API"""
    
    HIBP_API_URL = "https://haveibeenpwned.com/api/v3"
    
    @property
    def description(self) -> str:
        return "Breach data search using Have I Been Pwned API (free tier)"
    
    @property
    def search_types(self) -> List[str]:
        return ['email', 'username']
    
    def search(self, query: str, search_type: str = 'email', **kwargs) -> PluginResult:
        """
        Search for breaches associated with an email or username
        
        Args:
            query: Email address or username
            search_type: Type of search ('email' or 'username')
            **kwargs: Additional parameters (truncate_response, domain, timeout)
            
        Returns:
            PluginResult with breach data
        """
        start_time = time.time()
        
        try:
            # Get API key (optional for basic email checks, but recommended)
            api_key = self._get_api_key()
            
            # Get parameters
            timeout = kwargs.get('timeout', 10)
            truncate_response = kwargs.get('truncate_response', False)
            domain = kwargs.get('domain', None)
            
            self.log_info(f"Searching HIBP for {query} (type: {search_type})")
            
            # Normalize query
            query = query.strip().lower()
            
            # Perform search based on type
            if search_type == 'email':
                data = self._search_email(query, api_key, timeout, truncate_response, domain)
            elif search_type == 'username':
                data = self._search_username(query, api_key, timeout)
            else:
                raise ValueError(f"Unsupported search type: {search_type}")
            
            execution_time = time.time() - start_time
            
            self.log_info(f"HIBP search completed. Breaches found: {data.get('breach_count', 0)}")
            
            return PluginResult(
                source=self.name,
                search_type=search_type,
                query=query,
                data=[data],
                metadata={'api_version': '3.0'},
                success=True,
                execution_time=execution_time
            )
            
        except requests.exceptions.RequestException as e:
            execution_time = time.time() - start_time
            self.log_error(f"HIBP API request failed: {str(e)}")
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
            self.log_error(f"HIBP search failed: {str(e)}")
            return PluginResult(
                source=self.name,
                search_type=search_type,
                query=query,
                data=[],
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _get_api_key(self) -> str:
        """Get HIBP API key from config"""
        # Try to get from plugin config
        api_key = self.get_config_value('api_key')
        if api_key:
            return api_key
        
        # Try environment variable
        import os
        return os.environ.get('HIBP_API_KEY', '')
    
    def _search_email(self, email: str, api_key: str, timeout: int, truncate: bool, domain: str) -> Dict[str, Any]:
        """Search for breaches associated with an email"""
        headers = {
            'User-Agent': 'Kirwada-OSINT-Tool',
            'hibp-api-key': api_key if api_key else ''
        }
        
        # Search for all breaches for the email
        url = f"{self.HIBP_API_URL}/breachedaccount/{email}"
        if truncate:
            url += "?truncateResponse=true"
        
        response = requests.get(url, headers=headers, timeout=timeout)
        
        # Handle 404 - no breaches found
        if response.status_code == 404:
            return {
                'query_type': 'email',
                'query': email,
                'breach_count': 0,
                'breaches': [],
                'pastes': [],
                'message': 'No breaches found for this email'
            }
        
        # Handle rate limiting
        if response.status_code == 429:
            raise Exception("Rate limit exceeded. Please try again later.")
        
        response.raise_for_status()
        
        breaches = response.json()
        
        # Search for pastes
        url = f"{self.HIBP_API_URL}/pasteaccount/{email}"
        response = requests.get(url, headers=headers, timeout=timeout)
        pastes = []
        if response.status_code == 200:
            pastes = response.json()
        
        # Structure the results
        return {
            'query_type': 'email',
            'query': email,
            'breach_count': len(breaches),
            'breaches': breaches,
            'paste_count': len(pastes),
            'pastes': pastes,
            'summary': self._generate_summary(breaches)
        }
    
    def _search_username(self, username: str, api_key: str, timeout: int) -> Dict[str, Any]:
        """Search for breaches associated with a username"""
        headers = {
            'User-Agent': 'Kirwada-OSINT-Tool',
            'hibp-api-key': api_key if api_key else ''
        }
        
        # HIBP API doesn't have a direct username search endpoint
        # We'll use the breached site search as a workaround
        # Note: This is a limitation of the free API
        
        self.log_info(f"Username search limited. API requires email for comprehensive breach data.")
        
        # Return information about available breach sources
        url = f"{self.HIBP_API_URL}/breaches"
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        all_breaches = response.json()
        
        return {
            'query_type': 'username',
            'query': username,
            'breach_count': 0,
            'note': 'Username search is limited. Use email for comprehensive breach data.',
            'available_breach_sources': len(all_breaches),
            'message': 'HIBP free API does not support username searches directly'
        }
    
    def _generate_summary(self, breaches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of breach data"""
        if not breaches:
            return {}
        
        # Extract unique data classes
        data_classes = set()
        compromised_sites = []
        
        for breach in breaches:
            data_classes.update(breach.get('DataClasses', []))
            compromised_sites.append({
                'name': breach.get('Name', ''),
                'title': breach.get('Title', ''),
                'date': breach.get('BreachDate', ''),
                'added_date': breach.get('AddedDate', ''),
                'pwn_count': breach.get('PwnCount', 0),
                'is_verified': breach.get('IsVerified', False),
                'is_sensitive': breach.get('IsSensitive', False),
                'is_retired': breach.get('IsRetired', False),
                'description': breach.get('Description', '')[:500]  # Truncate description
            })
        
        # Sort by date (newest first)
        compromised_sites.sort(key=lambda x: x['date'], reverse=True)
        
        return {
            'total_breaches': len(breaches),
            'data_classes_compromised': sorted(list(data_classes)),
            'sites': compromised_sites,
            'total_records_exposed': sum(b.get('PwnCount', 0) for b in breaches)
        }
    
    def check_password(self, password: str, timeout: int = 10) -> Dict[str, Any]:
        """
        Check if a password has been exposed in data breaches
        
        Note: This uses the k-anonymity model and doesn't send the full password
        """
        try:
            # Hash the password using SHA-1
            sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
            prefix = sha1_password[:5]
            suffix = sha1_password[5:]
            
            # Query the Pwned Passwords API
            url = f"https://api.pwnedpasswords.com/range/{prefix}"
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Check if our suffix is in the response
            hashes = response.text.split('\r\n')
            for hash_line in hashes:
                hash_suffix, count = hash_line.split(':')
                if hash_suffix == suffix:
                    return {
                        'found': True,
                        'occurrences': int(count),
                        'message': f'Password has been found {count} times in data breaches'
                    }
            
            return {
                'found': False,
                'occurrences': 0,
                'message': 'Password not found in data breaches'
            }
            
        except Exception as e:
            return {
                'found': False,
                'error': str(e),
                'message': f'Error checking password: {str(e)}'
            }
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        # API key is optional for basic functionality but recommended
        api_key = self._get_api_key()
        if not api_key:
            self.log_warning("HIBP API key not configured. Rate limits may apply.")
        return True
