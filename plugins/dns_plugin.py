import subprocess
import logging
import re
from typing import List
from core.plugin_base import PluginBase, SearchType, PluginResult


class DNSPlugin(PluginBase):
    """
    DNS lookup plugin for retrieving DNS records of domains.
    """
    
    @property
    def name(self) -> str:
        return "DNS Lookup"

    @property
    def description(self) -> str:
        return "DNS record enumeration (A, AAAA, MX, NS, TXT, CNAME)"

    @property
    def supported_search_types(self) -> List[SearchType]:
        return [SearchType.DOMAIN]

    def run_search(self, query: str, search_type: SearchType) -> PluginResult:
        if search_type != SearchType.DOMAIN:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Unsupported search type: {search_type.value}"
            )

        try:
            logging.info(f"Running DNS lookup for: {query}")
            
            dns_records = {
                'domain': query,
                'A': [],
                'AAAA': [],
                'MX': [],
                'NS': [],
                'TXT': [],
                'CNAME': []
            }
            
            record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME']
            
            for record_type in record_types:
                records = self._query_dns_record(query, record_type)
                if records:
                    dns_records[record_type] = records
            
            total_records = sum(len(records) for records in dns_records.values() if isinstance(records, list))
            
            if total_records == 0:
                return PluginResult(
                    plugin_name=self.name,
                    search_type=search_type,
                    query=query,
                    success=True,
                    data={
                        'domain': query,
                        'message': 'No DNS records found or domain does not exist'
                    }
                )
            
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=True,
                data=dns_records,
                metadata={
                    'total_records': total_records,
                    'record_types_found': [k for k, v in dns_records.items() if isinstance(v, list) and len(v) > 0]
                }
            )
            
        except Exception as e:
            logging.error(f"DNS lookup error: {e}")
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"DNS lookup failed: {str(e)}"
            )

    def _query_dns_record(self, domain: str, record_type: str) -> List[str]:
        """Query a specific DNS record type"""
        try:
            result = subprocess.run(
                ['dig', '+short', domain, record_type],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                records = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                return records
            
            return []
            
        except subprocess.TimeoutExpired:
            logging.warning(f"DNS query timeout for {domain} {record_type}")
            return []
        except FileNotFoundError:
            result = subprocess.run(
                ['nslookup', '-type=' + record_type, domain],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return self._parse_nslookup_output(result.stdout, record_type)
            
            return []
        except Exception as e:
            logging.error(f"Error querying {record_type} record: {e}")
            return []

    def _parse_nslookup_output(self, output: str, record_type: str) -> List[str]:
        """Parse nslookup output as fallback"""
        records = []
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if record_type == 'A' and re.match(r'^Address: \d+\.\d+\.\d+\.\d+$', line):
                records.append(line.split(': ')[1])
            elif record_type == 'MX' and 'mail exchanger' in line.lower():
                parts = line.split('=')
                if len(parts) > 1:
                    records.append(parts[1].strip())
            elif record_type == 'NS' and 'nameserver' in line.lower():
                parts = line.split('=')
                if len(parts) > 1:
                    records.append(parts[1].strip())
        
        return records
