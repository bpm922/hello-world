from typing import List, Optional, Dict, Any
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.plugin_base import PluginBase, SearchType, PluginResult
from core.result_handler import ResultAggregator
from config.settings import get_settings


class OSINTEngine:
    def __init__(self):
        self.plugins: Dict[str, PluginBase] = {}
        self.settings = get_settings()
        self.result_aggregator = ResultAggregator()
        self._setup_logging()

    def _setup_logging(self):
        log_level = self.settings.get_setting("logging", "level") or "INFO"
        log_file = self.settings.get_setting("logging", "file")
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def register_plugin(self, plugin: PluginBase):
        self.plugins[plugin.name] = plugin
        logging.info(f"Registered plugin: {plugin.name}")

    def unregister_plugin(self, plugin_name: str):
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            logging.info(f"Unregistered plugin: {plugin_name}")

    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        return self.plugins.get(plugin_name)

    def get_all_plugins(self) -> List[PluginBase]:
        return list(self.plugins.values())

    def get_enabled_plugins(self) -> List[PluginBase]:
        return [p for p in self.plugins.values() if p.enabled]

    def get_plugins_by_search_type(self, search_type: SearchType) -> List[PluginBase]:
        return [
            p for p in self.get_enabled_plugins()
            if p.validate_search_type(search_type)
        ]

    def run_single_plugin(
        self,
        plugin_name: str,
        query: str,
        search_type: SearchType
    ) -> PluginResult:
        plugin = self.get_plugin(plugin_name)
        
        if not plugin:
            error_msg = f"Plugin '{plugin_name}' not found"
            logging.error(error_msg)
            return PluginResult(
                plugin_name=plugin_name,
                search_type=search_type,
                query=query,
                success=False,
                error=error_msg
            )
        
        if not plugin.enabled:
            error_msg = f"Plugin '{plugin_name}' is disabled"
            logging.warning(error_msg)
            return PluginResult(
                plugin_name=plugin_name,
                search_type=search_type,
                query=query,
                success=False,
                error=error_msg
            )
        
        if not plugin.validate_search_type(search_type):
            error_msg = f"Plugin '{plugin_name}' does not support search type '{search_type.value}'"
            logging.warning(error_msg)
            return PluginResult(
                plugin_name=plugin_name,
                search_type=search_type,
                query=query,
                success=False,
                error=error_msg
            )
        
        logging.info(f"Running plugin '{plugin_name}' for query '{query}'")
        
        try:
            result = plugin.run_search(query, search_type)
            return result
        except Exception as e:
            error_msg = f"Plugin '{plugin_name}' crashed: {str(e)}"
            logging.error(error_msg)
            return PluginResult(
                plugin_name=plugin_name,
                search_type=search_type,
                query=query,
                success=False,
                error=error_msg
            )

    def run_all_plugins(
        self,
        query: str,
        search_type: SearchType,
        parallel: bool = True
    ) -> ResultAggregator:
        plugins = self.get_plugins_by_search_type(search_type)
        
        if not plugins:
            logging.warning(f"No plugins available for search type '{search_type.value}'")
            self.result_aggregator.start_search(0)
            self.result_aggregator.end_search()
            return self.result_aggregator
        
        self.result_aggregator.start_search(len(plugins))
        logging.info(f"Running {len(plugins)} plugins for query '{query}'")
        
        if parallel:
            max_workers = self.settings.get_setting("search", "max_concurrent") or 5
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_plugin = {
                    executor.submit(plugin.run_search, query, search_type): plugin
                    for plugin in plugins
                }
                
                for future in as_completed(future_to_plugin):
                    plugin = future_to_plugin[future]
                    try:
                        result = future.result()
                        self.result_aggregator.add_result(result)
                    except Exception as e:
                        error_msg = f"Plugin '{plugin.name}' crashed: {str(e)}"
                        logging.error(error_msg)
                        self.result_aggregator.add_result(
                            PluginResult(
                                plugin_name=plugin.name,
                                search_type=search_type,
                                query=query,
                                success=False,
                                error=error_msg
                            )
                        )
        else:
            for plugin in plugins:
                try:
                    result = plugin.run_search(query, search_type)
                    self.result_aggregator.add_result(result)
                except Exception as e:
                    error_msg = f"Plugin '{plugin.name}' crashed: {str(e)}"
                    logging.error(error_msg)
                    self.result_aggregator.add_result(
                        PluginResult(
                            plugin_name=plugin.name,
                            search_type=search_type,
                            query=query,
                            success=False,
                            error=error_msg
                        )
                    )
        
        self.result_aggregator.end_search()
        return self.result_aggregator

    def get_results(self) -> ResultAggregator:
        return self.result_aggregator

    def clear_results(self):
        self.result_aggregator.clear()
