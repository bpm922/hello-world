"""
Base Plugin Class for Kirwada OSINT Tool

All plugins must inherit from this class and implement the required methods.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class PluginResult:
    """Standardized result format for all plugins"""
    source: str  # Plugin name
    search_type: str  # Type of search performed
    query: str  # The original search query
    data: List[Dict[str, Any]]  # The results
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata
    success: bool = True
    error_message: Optional[str] = None
    execution_time: Optional[float] = None


class BasePlugin(ABC):
    """Abstract base class for all OSINT plugins"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the plugin
        
        Args:
            config: Plugin configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"Kirwada.{self.name}")
        self.name = self.__class__.__name__.replace('Plugin', '').lower()
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a brief description of what this plugin does"""
        pass
    
    @property
    @abstractmethod
    def search_types(self) -> List[str]:
        """Return list of supported search types (e.g., ['username', 'email', 'domain'])"""
        pass
    
    @abstractmethod
    def search(self, query: str, search_type: str = 'default', **kwargs) -> PluginResult:
        """
        Perform a search with the given query
        
        Args:
            query: The search query
            search_type: Type of search to perform
            **kwargs: Additional parameters for the search
            
        Returns:
            PluginResult object with standardized results
        """
        pass
    
    def is_search_type_supported(self, search_type: str) -> bool:
        """Check if a search type is supported by this plugin"""
        return search_type in self.search_types or search_type in self.search_types
    
    def validate_config(self) -> bool:
        """
        Validate plugin configuration
        
        Returns:
            True if configuration is valid, False otherwise
        """
        return True
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value with a default fallback"""
        return self.config.get(key, default)
    
    def log_info(self, message: str):
        """Log an info message"""
        self.logger.info(message)
    
    def log_error(self, message: str):
        """Log an error message"""
        self.logger.error(message)
    
    def log_warning(self, message: str):
        """Log a warning message"""
        self.logger.warning(message)
