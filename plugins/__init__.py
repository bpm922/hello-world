from pathlib import Path
import importlib
import inspect
from typing import List
from core.plugin_base import PluginBase
import logging


def discover_plugins() -> List[PluginBase]:
    plugins = []
    plugin_dir = Path(__file__).parent
    
    for plugin_file in plugin_dir.glob("*_plugin.py"):
        module_name = plugin_file.stem
        
        try:
            module = importlib.import_module(f"plugins.{module_name}")
            
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginBase) and 
                    obj is not PluginBase):
                    plugin_instance = obj()
                    plugins.append(plugin_instance)
                    logging.info(f"Discovered plugin: {plugin_instance.name}")
        except Exception as e:
            logging.error(f"Failed to load plugin {module_name}: {e}")
    
    return plugins
