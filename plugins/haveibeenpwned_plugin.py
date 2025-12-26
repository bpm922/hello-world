import requests
import logging
import time
from typing import List
from core.plugin_base import PluginBase, SearchType, PluginResult


class HaveIBeenPwnedPlugin(PluginBase):
    """
    Have I Been Pwned (HIBP) plugin for checking if an email has been in data breaches.
    Uses the public API (rate limited to 1 request per 1.5 seconds).
    """
    
    def __init__(self):
        super().__init__()
        self.api_base_url = "https://haveibeenpwned.com/api/v3"
        self.last_request_time = 0
        self.min_request_interval = 1.5

    @property
    def name(self) -> str:
        return "Have I Been Pwned"

    @property
    def description(self) -> str:
        return "Check if email addresses have been compromised in data breaches"

    @property
    def supported_search_types(self) -> List[SearchType]:
        return [SearchType.EMAIL]

    def _rate_limit(self):
        """Enforce rate limiting (1 request per 1.5 seconds)"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def run_search(self, query: str, search_type: SearchType) -> PluginResult:
        if search_type != SearchType.EMAIL:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Unsupported search type: {search_type.value}"
            )

        if '@' not in query:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error="Invalid email format"
            )

        try:
            logging.info(f"Checking HIBP for email: {query}")
            
            self._rate_limit()
            
            url = f"{self.api_base_url}/breachedaccount/{query}"
            
            headers = {
                'User-Agent': 'OSINT-Framework-Tool',
                'hibp-api-version': '3'
            }
            
            response = requests.get(
                url,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                breaches = response.json()
                
                breach_summary = []
                for breach in breaches:
                    breach_summary.append({
                        'name': breach.get('Name'),
                        'title': breach.get('Title'),
                        'domain': breach.get('Domain'),
                        'breach_date': breach.get('BreachDate'),
                        'added_date': breach.get('AddedDate'),
                        'pwn_count': breach.get('PwnCount'),
                        'description': breach.get('Description', '')[:200] + '...' if len(breach.get('Description', '')) > 200 else breach.get('Description', ''),
                        'data_classes': breach.get('DataClasses', []),
                        'is_verified': breach.get('IsVerified'),
                        'is_sensitive': breach.get('IsSensitive')
                    })
                
                return PluginResult(
                    plugin_name=self.name,
                    search_type=search_type,
                    query=query,
                    success=True,
                    data={
                        'email': query,
                        'breached': True,
                        'breach_count': len(breaches),
                        'breaches': breach_summary
                    },
                    metadata={
                        'total_breaches': len(breaches),
                        'warning': 'This email has been found in data breaches!'
                    }
                )
            
            elif response.status_code == 404:
                return PluginResult(
                    plugin_name=self.name,
                    search_type=search_type,
                    query=query,
                    success=True,
                    data={
                        'email': query,
                        'breached': False,
                        'breach_count': 0,
                        'message': 'Good news! No breaches found for this email address.'
                    }
                )
            
            elif response.status_code == 429:
                return PluginResult(
                    plugin_name=self.name,
                    search_type=search_type,
                    query=query,
                    success=False,
                    error="Rate limit exceeded. Please wait before trying again."
                )
            
            else:
                return PluginResult(
                    plugin_name=self.name,
                    search_type=search_type,
                    query=query,
                    success=False,
                    error=f"API returned status code: {response.status_code}"
                )
            
        except requests.exceptions.Timeout:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error="Request timed out after 15 seconds"
            )
        except requests.exceptions.RequestException as e:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Network error: {str(e)}"
            )
        except Exception as e:
            logging.error(f"HIBP error: {e}")
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
