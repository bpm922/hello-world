import subprocess
import logging
from typing import List
from core.plugin_base import PluginBase, SearchType, PluginResult


class WhoisPlugin(PluginBase):
    """
    WHOIS lookup plugin for domain registration and ownership information.
    """
    
    def __init__(self):
        super().__init__()
        self._check_whois_installed()

    @property
    def name(self) -> str:
        return "WHOIS"

    @property
    def description(self) -> str:
        return "Domain registration and ownership information lookup"

    @property
    def supported_search_types(self) -> List[SearchType]:
        return [SearchType.DOMAIN, SearchType.IP]

    def _check_whois_installed(self):
        try:
            result = subprocess.run(
                ['which', 'whois'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                logging.warning("WHOIS command not found. Install with: apt install whois")
        except Exception as e:
            logging.error(f"Error checking WHOIS installation: {e}")

    def run_search(self, query: str, search_type: SearchType) -> PluginResult:
        if search_type not in self.supported_search_types:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Unsupported search type: {search_type.value}"
            )

        try:
            logging.info(f"Running WHOIS lookup for: {query}")
            
            result = subprocess.run(
                ['whois', query],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return PluginResult(
                    plugin_name=self.name,
                    search_type=search_type,
                    query=query,
                    success=False,
                    error=result.stderr or "WHOIS lookup failed"
                )
            
            whois_output = result.stdout
            
            parsed_data = self._parse_whois_output(whois_output)
            
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=True,
                data=parsed_data,
                metadata={
                    'raw_output_length': len(whois_output),
                    'search_type': search_type.value
                }
            )
            
        except subprocess.TimeoutExpired:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error="WHOIS lookup timed out after 30 seconds"
            )
        except FileNotFoundError:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error="WHOIS command not found. Install with: apt install whois"
            )
        except Exception as e:
            logging.error(f"WHOIS error: {e}")
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Unexpected error: {str(e)}"
            )

    def _parse_whois_output(self, output: str) -> dict:
        """Parse WHOIS output to extract key information"""
        data = {
            'raw_output': output,
            'domain_name': None,
            'registrar': None,
            'creation_date': None,
            'expiration_date': None,
            'name_servers': [],
            'status': []
        }
        
        lines = output.lower().split('\n')
        
        for line in lines:
            line = line.strip()
            
            if 'domain name:' in line:
                data['domain_name'] = line.split(':', 1)[1].strip()
            elif 'registrar:' in line:
                data['registrar'] = line.split(':', 1)[1].strip()
            elif 'creation date:' in line or 'created:' in line:
                data['creation_date'] = line.split(':', 1)[1].strip()
            elif 'expiration date:' in line or 'expiry date:' in line:
                data['expiration_date'] = line.split(':', 1)[1].strip()
            elif 'name server:' in line or 'nserver:' in line:
                ns = line.split(':', 1)[1].strip()
                if ns and ns not in data['name_servers']:
                    data['name_servers'].append(ns)
            elif 'status:' in line:
                status = line.split(':', 1)[1].strip()
                if status and status not in data['status']:
                    data['status'].append(status)
        
        return data
