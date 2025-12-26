import subprocess
import json
import tempfile
import logging
from pathlib import Path
from typing import List
from core.plugin_base import PluginBase, SearchType, PluginResult


class SherlockPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self._check_sherlock_installed()

    @property
    def name(self) -> str:
        return "Sherlock"

    @property
    def description(self) -> str:
        return "Username search across 300+ social networks"

    @property
    def supported_search_types(self) -> List[SearchType]:
        return [SearchType.USERNAME]

    def _check_sherlock_installed(self):
        try:
            result = subprocess.run(
                ['sherlock', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                logging.warning("Sherlock may not be properly installed")
        except FileNotFoundError:
            logging.warning("Sherlock command not found. Please install: pip install sherlock-project")
        except Exception as e:
            logging.error(f"Error checking Sherlock installation: {e}")

    def run_search(self, query: str, search_type: SearchType) -> PluginResult:
        if search_type != SearchType.USERNAME:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Unsupported search type: {search_type.value}"
            )

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = Path(tmpdir) / f"{query}.json"
                
                cmd = [
                    'sherlock',
                    query,
                    '--json',
                    str(output_file),
                    '--timeout',
                    '10'
                ]
                
                logging.info(f"Running Sherlock for username: {query}")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if output_file.exists():
                    with open(output_file, 'r') as f:
                        data = json.load(f)
                    
                    found_profiles = []
                    for site, info in data.items():
                        if isinstance(info, dict) and info.get('url_user'):
                            found_profiles.append({
                                'site': site,
                                'url': info['url_user'],
                                'status': info.get('status', {})
                            })
                    
                    return PluginResult(
                        plugin_name=self.name,
                        search_type=search_type,
                        query=query,
                        success=True,
                        data={
                            'username': query,
                            'profiles_found': len(found_profiles),
                            'profiles': found_profiles
                        },
                        metadata={
                            'total_sites_checked': len(data)
                        }
                    )
                else:
                    error_output = result.stderr if result.stderr else "No output file generated"
                    
                    if result.returncode == 0:
                        return PluginResult(
                            plugin_name=self.name,
                            search_type=search_type,
                            query=query,
                            success=True,
                            data={
                                'username': query,
                                'profiles_found': 0,
                                'profiles': []
                            }
                        )
                    
                    return PluginResult(
                        plugin_name=self.name,
                        search_type=search_type,
                        query=query,
                        success=False,
                        error=f"Sherlock execution failed: {error_output}"
                    )

        except subprocess.TimeoutExpired:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error="Search timed out after 60 seconds"
            )
        except FileNotFoundError:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error="Sherlock not found. Install with: pip install sherlock-project"
            )
        except Exception as e:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
