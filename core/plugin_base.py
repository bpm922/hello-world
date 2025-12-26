from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class SearchType(Enum):
    USERNAME = "username"
    EMAIL = "email"
    DOMAIN = "domain"
    URL = "url"
    PHONE = "phone"
    IP = "ip"


class PluginResult:
    def __init__(
        self,
        plugin_name: str,
        search_type: SearchType,
        query: str,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.plugin_name = plugin_name
        self.search_type = search_type
        self.query = query
        self.success = success
        self.data = data or {}
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plugin_name": self.plugin_name,
            "search_type": self.search_type.value,
            "query": self.query,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class PluginBase(ABC):
    def __init__(self):
        self._enabled = True
        self._config = {}

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def supported_search_types(self) -> List[SearchType]:
        pass

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def configure(self, config: Dict[str, Any]):
        self._config = config

    @abstractmethod
    def run_search(self, query: str, search_type: SearchType) -> PluginResult:
        pass

    def validate_search_type(self, search_type: SearchType) -> bool:
        return search_type in self.supported_search_types

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
