#!/usr/bin/env python3
"""
Kirwada OSINT Tool
An open-source intelligence gathering tool with multiple reconnaissance plugins.
"""

import sys
import logging
import json
import time
import importlib
import pkgutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from plugins.base_plugin import BasePlugin, PluginResult
from exporters.json_exporter import JsonExporter
from exporters.csv_exporter import CsvExporter
from exporters.txt_exporter import TxtExporter


class Kirwada:
    """Main Kirwada OSINT Tool class"""
    
    def __init__(self, config_path: str = "config/plugin_config.json"):
        """Initialize Kirwada with configuration"""
        self.config = self._load_config(config_path)
        self.plugins: Dict[str, BasePlugin] = {}
        self.setup_logging()
        self.load_plugins()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found. Using defaults.")
            return self._default_config()
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "plugins": {},
            "exporters": {
                "default_format": "json",
                "output_directory": "./results"
            },
            "logging": {
                "level": "INFO"
            },
            "settings": {
                "default_timeout": 10
            }
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO').upper())
        log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_file = log_config.get('file', 'kirwada.log')
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("Kirwada")
        self.logger.info("Kirwada OSINT Tool initialized")
    
    def load_plugins(self):
        """Auto-discover and load all plugins"""
        self.logger.info("Loading plugins...")
        
        try:
            # Import plugins package
            import plugins
            
            # Discover all modules in plugins package
            for _, module_name, _ in pkgutil.iter_modules(plugins.__path__):
                if module_name.endswith('_plugin') and module_name != 'base_plugin':
                    try:
                        # Import the plugin module
                        module = importlib.import_module(f'plugins.{module_name}')
                        
                        # Find plugin class in module
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and 
                                issubclass(attr, BasePlugin) and 
                                attr != BasePlugin):
                                
                                # Instantiate plugin
                                plugin_config = self.config.get('plugins', {}).get(attr_name.replace('_plugin', ''), {})
                                plugin = attr(plugin_config)
                                
                                # Store plugin
                                self.plugins[attr_name.replace('_plugin', '')] = plugin
                                self.logger.info(f"Loaded plugin: {plugin.name} - {plugin.description}")
                                break
                                
                    except Exception as e:
                        self.logger.error(f"Failed to load plugin {module_name}: {str(e)}")
        
        except ImportError as e:
            self.logger.error(f"Failed to import plugins package: {str(e)}")
        
        self.logger.info(f"Total plugins loaded: {len(self.plugins)}")
    
    def run_interactive(self):
        """Run interactive CLI menu"""
        while True:
            self._print_menu()
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == '1':
                self._search_single_tool()
            elif choice == '2':
                self._search_all_tools()
            elif choice == '3':
                self._list_plugins()
            elif choice == '4':
                self._export_results()
            elif choice == '5':
                self._view_results()
            elif choice == '6':
                self._configure_api_keys()
            elif choice == '7':
                self._show_help()
            elif choice == '8':
                print("\nThank you for using Kirwada OSINT Tool!")
                break
            elif choice == '9':
                self._show_about()
            else:
                print("\nInvalid choice. Please try again.")
            
            if choice != '8':
                input("\nPress Enter to continue...")
    
    def _print_menu(self):
        """Print the main menu"""
        print("\n" + "=" * 60)
        print(" " * 15 + "KIRWADA OSINT TOOL")
        print("=" * 60)
        print("1. Search with Single Tool")
        print("2. Search All Tools")
        print("3. List Available Plugins")
        print("4. Export Results")
        print("5. View Results")
        print("6. Configure API Keys")
        print("7. Help")
        print("8. Exit")
        print("9. About")
        print("=" * 60)
    
    def _select_plugin(self) -> Optional[BasePlugin]:
        """Let user select a plugin"""
        if not self.plugins:
            print("No plugins available.")
            return None
        
        print("\nAvailable Plugins:")
        plugins_list = sorted(self.plugins.items())
        
        for i, (name, plugin) in enumerate(plugins_list, 1):
            status = "✓" if plugin.validate_config() else "⚠"
            print(f"{i}. {plugin.name.upper()} ({status}) - {plugin.description}")
        
        choice = input(f"\nSelect plugin (1-{len(plugins_list)}): ").strip()
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(plugins_list):
                return plugins_list[index][1]
        except ValueError:
            pass
        
        print("Invalid selection.")
        return None
    
    def _search_single_tool(self):
        """Search using a single plugin"""
        plugin = self._select_plugin()
        if not plugin:
            return
        
        query = input(f"\nEnter search query for {plugin.name}: ").strip()
        if not query:
            print("Query cannot be empty.")
            return
        
        # Get search type
        search_types = plugin.search_types
        search_type = 'default'
        
        if len(search_types) > 1:
            print(f"\nAvailable search types: {', '.join(search_types)}")
            search_type = input(f"Enter search type (default: {search_types[0]}): ").strip()
            if not search_type:
                search_type = search_types[0]
        
        # Perform search
        print(f"\nSearching with {plugin.name}...")
        result = plugin.search(query, search_type=search_type)
        
        # Display results
        self._display_result(result)
        
        # Store result for later export
        self._store_result(result)
    
    def _search_all_tools(self):
        """Search using all enabled plugins"""
        query = input("\nEnter search query: ").strip()
        if not query:
            print("Query cannot be empty.")
            return
        
        print(f"\nSearching with all plugins...")
        print("-" * 60)
        
        results = []
        enabled_plugins = [
            p for p in self.plugins.values()
            if self.config.get('plugins', {}).get(p.name, {}).get('enabled', True)
        ]
        
        for i, plugin in enumerate(enabled_plugins, 1):
            print(f"[{i}/{len(enabled_plugins)}] Running {plugin.name}...", end=" ", flush=True)
            
            try:
                # Use appropriate search type
                search_type = plugin.search_types[0] if plugin.search_types else 'default'
                result = plugin.search(query, search_type=search_type)
                results.append(result)
                
                status = "✓" if result.success else "✗"
                print(status)
                
            except Exception as e:
                print(f"✗ (Error: {str(e)[:50]})")
        
        print("-" * 60)
        print(f"\nCompleted: {len(results)} searches")
        
        # Display summary
        self._display_results_summary(results)
        
        # Store results
        self._store_results(results)
        
        # Ask if user wants to export
        export = input("\nExport results? (y/n): ").strip().lower()
        if export == 'y':
            self._export_results_interactive(results)
    
    def _list_plugins(self):
        """List all available plugins with details"""
        print("\n" + "=" * 80)
        print("AVAILABLE PLUGINS")
        print("=" * 80)
        
        for name, plugin in sorted(self.plugins.items()):
            status = "✓ Enabled" if self.config.get('plugins', {}).get(name, {}).get('enabled', True) else "✗ Disabled"
            config_status = "Configured" if plugin.validate_config() else "⚠ Needs Config"
            
            print(f"\n{plugin.name.upper()}")
            print(f"  Description: {plugin.description}")
            print(f"  Status: {status}")
            print(f"  Configuration: {config_status}")
            print(f"  Search Types: {', '.join(plugin.search_types) if plugin.search_types else 'N/A'}")
    
    def _display_result(self, result: PluginResult):
        """Display a single result"""
        print("\n" + "=" * 80)
        print(f"RESULTS FROM: {result.source.upper()}")
        print("=" * 80)
        print(f"Query: {result.query}")
        print(f"Search Type: {result.search_type}")
        print(f"Success: {result.success}")
        
        if result.execution_time:
            print(f"Execution Time: {result.execution_time:.2f}s")
        
        if result.error_message:
            print(f"Error: {result.error_message}")
        
        print("-" * 80)
        
        if result.data:
            data = result.data[0] if isinstance(result.data, list) else result.data
            self._display_data(data)
    
    def _display_data(self, data: Any, indent: str = ""):
        """Display data in a readable format"""
        if isinstance(data, dict):
            for key, value in sorted(data.items()):
                if isinstance(value, dict):
                    print(f"{indent}{key}:")
                    self._display_data(value, indent + "  ")
                elif isinstance(value, list):
                    if value and len(value) > 0:
                        print(f"{indent}{key}:")
                        for item in value[:10]:  # Show first 10 items
                            if isinstance(item, dict):
                                print(f"{indent}  -")
                                self._display_data(item, indent + "    ")
                            else:
                                print(f"{indent}  - {str(item)[:100]}")
                        if len(value) > 10:
                            print(f"{indent}  ... ({len(value) - 10} more items)")
                    else:
                        print(f"{indent}{key}: []")
                else:
                    value_str = str(value) if value is not None else "N/A"
                    if len(value_str) > 200:
                        value_str = value_str[:200] + "..."
                    print(f"{indent}{key}: {value_str}")
        elif isinstance(data, (list, str)):
            print(f"{indent}{str(data)[:1000]}")
    
    def _display_results_summary(self, results: List[PluginResult]):
        """Display summary of multiple results"""
        print("\n" + "=" * 80)
        print("SEARCH SUMMARY")
        print("=" * 80)
        
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_time = sum(r.execution_time or 0 for r in results)
        
        print(f"Total searches: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total time: {total_time:.2f}s")
        if len(results) > 0:
            print(f"Average time: {total_time/len(results):.2f}s")
        else:
            print("Average time: N/A (no results)")
        
        print("\nResults by source:")
        for result in results:
            status = "✓" if result.success else "✗"
            time_str = f"{result.execution_time:.2f}s" if result.execution_time else "N/A"
            print(f"  {status} {result.source.upper():15s} - {time_str}")
    
    def _store_result(self, result: PluginResult):
        """Store a result in memory"""
        if not hasattr(self, '_results'):
            self._results = []
        self._results.append(result)
    
    def _store_results(self, results: List[PluginResult]):
        """Store multiple results in memory"""
        if not hasattr(self, '_results'):
            self._results = []
        self._results.extend(results)
    
    def _export_results(self):
        """Export stored results"""
        if not hasattr(self, '_results') or not self._results:
            print("No results to export.")
            return
        
        self._export_results_interactive(self._results)
    
    def _export_results_interactive(self, results: List[PluginResult]):
        """Export results interactively"""
        print("\nExport Formats:")
        print("1. JSON")
        print("2. CSV")
        print("3. TXT")
        
        choice = input("Select format (1-3): ").strip()
        
        format_map = {
            '1': 'json',
            '2': 'csv',
            '3': 'txt'
        }
        
        format_type = format_map.get(choice, 'json')
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self.config.get('exporters', {}).get('output_directory', './results')
        output_file = f"{output_dir}/kirwada_results_{timestamp}.{format_type}"
        
        # Get exporter
        exporters = {
            'json': JsonExporter(),
            'csv': CsvExporter(),
            'txt': TxtExporter()
        }
        
        exporter = exporters.get(format_type)
        if not exporter:
            print(f"Unsupported format: {format_type}")
            return
        
        # Convert PluginResult objects to dicts for export
        results_dicts = [
            {
                'source': r.source,
                'search_type': r.search_type,
                'query': r.query,
                'data': r.data,
                'metadata': r.metadata,
                'success': r.success,
                'error_message': r.error_message,
                'execution_time': r.execution_time
            }
            for r in results
        ]
        
        # Export
        if exporter.export(results_dicts, output_file):
            print(f"\n✓ Results exported to: {output_file}")
        else:
            print(f"\n✗ Failed to export results")
    
    def _view_results(self):
        """View stored results"""
        if not hasattr(self, '_results') or not self._results:
            print("No results stored.")
            return
        
        print(f"\nStored results: {len(self._results)}")
        print("\nSelect result to view:")
        
        for i, result in enumerate(self._results, 1):
            status = "✓" if result.success else "✗"
            print(f"{i}. {status} {result.source} - {result.query}")
        
        choice = input("\nEnter result number (or 'all'): ").strip()
        
        if choice.lower() == 'all':
            self._display_results_summary(self._results)
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(self._results):
                    self._display_result(self._results[index])
            except ValueError:
                print("Invalid selection.")
    
    def _configure_api_keys(self):
        """Configure API keys for plugins"""
        print("\nAPI Key Configuration")
        print("=" * 60)
        
        config = self.config.get('plugins', {})
        
        for plugin_name, plugin in sorted(self.plugins.items()):
            plugin_config = config.get(plugin_name, {})
            
            if plugin_config.get('requires_api_key'):
                current_key = plugin_config.get('api_key', '')
                masked_key = '*' * len(current_key) if current_key else 'Not set'
                
                print(f"\n{plugin.name.upper()}")
                print(f"  Current: {masked_key}")
                
                new_key = input(f"  Enter new API key (press Enter to keep current): ").strip()
                if new_key:
                    config[plugin_name]['api_key'] = new_key
                    print("  ✓ API key updated")
        
        # Save config
        if input("\nSave changes? (y/n): ").strip().lower() == 'y':
            try:
                with open('config/plugin_config.json', 'w') as f:
                    json.dump(self.config, f, indent=2)
                print("✓ Configuration saved")
            except Exception as e:
                print(f"✗ Failed to save configuration: {str(e)}")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
KIRWADA OSINT TOOL - HELP

Getting Started:
1. Use option 1 to search with a single tool
2. Use option 2 to search with all tools simultaneously
3. Use option 4 to export results to JSON, CSV, or TXT

Plugins:
- Photon: Website reconnaissance and data extraction
- TheHarvester: Email and subdomain discovery
- Spider: Web crawling and link discovery
- Shodan: IP/device intelligence (requires API key)
- HIBP: Breach data search
- Whois: Domain ownership and DNS information

Configuration:
- API keys can be configured from the main menu
- Edit config/plugin_config.json for advanced settings

Tips:
- Some plugins work better with specific query types
- Use "Search All" to get comprehensive results
- Export results for further analysis

For more information, visit: https://github.com/yourusername/kirwada
        """
        print(help_text)
    
    def _show_about(self):
        """Show about information"""
        about_text = """
KIRWADA OSINT TOOL
=================

An open-source intelligence gathering tool with multiple
reconnaissance plugins.

Features:
- Multi-plugin architecture
- Standardized result format
- Export to multiple formats (JSON, CSV, TXT)
- Comprehensive documentation
- Easy to extend

Version: 1.0.0
License: MIT License

Developed by: Kirwada Team
Contributors are welcome!

For bug reports and feature requests, please visit:
https://github.com/yourusername/kirwada/issues
        """
        print(about_text)
    
    def run_single_search(self, query: str, plugin_name: str = None, 
                          search_type: str = None) -> List[PluginResult]:
        """
        Run a single search programmatically
        
        Args:
            query: Search query
            plugin_name: Specific plugin to use (or None for all)
            search_type: Type of search to perform
            
        Returns:
            List of PluginResult objects
        """
        results = []
        
        if plugin_name and plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            result = plugin.search(query, search_type=search_type)
            results.append(result)
        else:
            # Search with all enabled plugins
            for plugin in self.plugins.values():
                if self.config.get('plugins', {}).get(plugin.name, {}).get('enabled', True):
                    st = search_type or (plugin.search_types[0] if plugin.search_types else 'default')
                    result = plugin.search(query, search_type=st)
                    results.append(result)
        
        return results


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     KIRWADA OSINT TOOL v1.0.0                             ║
║     Open-Source Intelligence Gathering                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    try:
        app = Kirwada()
        app.run_interactive()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
