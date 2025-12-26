import re
import socket
import logging
from typing import List
from core.plugin_base import PluginBase, SearchType, PluginResult


class EmailValidatorPlugin(PluginBase):
    """
    Email validation and verification plugin.
    Checks email format, domain existence, and MX records.
    """
    
    @property
    def name(self) -> str:
        return "Email Validator"

    @property
    def description(self) -> str:
        return "Validate email format and check domain/MX records"

    @property
    def supported_search_types(self) -> List[SearchType]:
        return [SearchType.EMAIL]

    def run_search(self, query: str, search_type: SearchType) -> PluginResult:
        if search_type != SearchType.EMAIL:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Unsupported search type: {search_type.value}"
            )

        try:
            logging.info(f"Validating email: {query}")
            
            validation_results = {
                'email': query,
                'format_valid': False,
                'domain_exists': False,
                'has_mx_records': False,
                'mx_records': [],
                'domain': None,
                'local_part': None,
                'validation_passed': False
            }
            
            format_valid, local_part, domain = self._validate_format(query)
            validation_results['format_valid'] = format_valid
            validation_results['local_part'] = local_part
            validation_results['domain'] = domain
            
            if not format_valid:
                return PluginResult(
                    plugin_name=self.name,
                    search_type=search_type,
                    query=query,
                    success=True,
                    data=validation_results
                )
            
            domain_exists = self._check_domain_exists(domain)
            validation_results['domain_exists'] = domain_exists
            
            if domain_exists:
                mx_records = self._get_mx_records(domain)
                validation_results['has_mx_records'] = len(mx_records) > 0
                validation_results['mx_records'] = mx_records
            
            validation_results['validation_passed'] = (
                validation_results['format_valid'] and
                validation_results['domain_exists'] and
                validation_results['has_mx_records']
            )
            
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=True,
                data=validation_results,
                metadata={
                    'validation_score': self._calculate_validation_score(validation_results)
                }
            )
            
        except Exception as e:
            logging.error(f"Email validation error: {e}")
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Validation failed: {str(e)}"
            )

    def _validate_format(self, email: str) -> tuple:
        """Validate email format using regex"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(email_pattern, email):
            parts = email.split('@')
            if len(parts) == 2:
                return True, parts[0], parts[1]
        
        return False, None, None

    def _check_domain_exists(self, domain: str) -> bool:
        """Check if domain exists by attempting DNS lookup"""
        try:
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False
        except Exception as e:
            logging.warning(f"Domain check error: {e}")
            return False

    def _get_mx_records(self, domain: str) -> List[str]:
        """Get MX records for the domain"""
        try:
            import subprocess
            result = subprocess.run(
                ['dig', '+short', domain, 'MX'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                mx_records = []
                for line in result.stdout.strip().split('\n'):
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            mx_records.append(parts[1].rstrip('.'))
                        else:
                            mx_records.append(line)
                return mx_records
            
            return []
            
        except FileNotFoundError:
            try:
                result = subprocess.run(
                    ['nslookup', '-type=MX', domain],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                mx_records = []
                for line in result.stdout.split('\n'):
                    if 'mail exchanger' in line.lower():
                        parts = line.split('=')
                        if len(parts) > 1:
                            mx_records.append(parts[1].strip().rstrip('.'))
                
                return mx_records
            except:
                return []
        except Exception as e:
            logging.warning(f"MX record lookup error: {e}")
            return []

    def _calculate_validation_score(self, validation_results: dict) -> str:
        """Calculate a validation score"""
        score = 0
        
        if validation_results['format_valid']:
            score += 33
        if validation_results['domain_exists']:
            score += 33
        if validation_results['has_mx_records']:
            score += 34
        
        if score >= 90:
            return f"{score}% - Valid"
        elif score >= 66:
            return f"{score}% - Likely Valid"
        elif score >= 33:
            return f"{score}% - Questionable"
        else:
            return f"{score}% - Invalid"
