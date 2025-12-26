import requests
import logging
from typing import List
from core.plugin_base import PluginBase, SearchType, PluginResult


class IPGeolocationPlugin(PluginBase):
    """
    IP Geolocation plugin using the free ip-api.com service.
    No API key required, but rate limited to 45 requests per minute.
    """
    
    def __init__(self):
        super().__init__()
        self.api_url = "http://ip-api.com/json"

    @property
    def name(self) -> str:
        return "IP Geolocation"

    @property
    def description(self) -> str:
        return "IP address geolocation and ISP information"

    @property
    def supported_search_types(self) -> List[SearchType]:
        return [SearchType.IP]

    def run_search(self, query: str, search_type: SearchType) -> PluginResult:
        if search_type != SearchType.IP:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Unsupported search type: {search_type.value}"
            )

        try:
            logging.info(f"Looking up IP geolocation for: {query}")
            
            url = f"{self.api_url}/{query}"
            params = {
                'fields': 'status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query'
            }
            
            response = requests.get(
                url,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    result_data = {
                        'ip': data.get('query', query),
                        'country': data.get('country'),
                        'country_code': data.get('countryCode'),
                        'region': data.get('regionName'),
                        'region_code': data.get('region'),
                        'city': data.get('city'),
                        'zip_code': data.get('zip'),
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon'),
                        'timezone': data.get('timezone'),
                        'isp': data.get('isp'),
                        'organization': data.get('org'),
                        'as_number': data.get('as')
                    }
                    
                    location_string = f"{result_data['city']}, {result_data['region']}, {result_data['country']}"
                    
                    return PluginResult(
                        plugin_name=self.name,
                        search_type=search_type,
                        query=query,
                        success=True,
                        data=result_data,
                        metadata={
                            'location': location_string,
                            'coordinates': f"{result_data['latitude']}, {result_data['longitude']}"
                        }
                    )
                else:
                    error_message = data.get('message', 'IP lookup failed')
                    return PluginResult(
                        plugin_name=self.name,
                        search_type=search_type,
                        query=query,
                        success=False,
                        error=f"IP lookup failed: {error_message}"
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
                error="Request timed out after 10 seconds"
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
            logging.error(f"IP geolocation error: {e}")
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
