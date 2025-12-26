from typing import List, Dict, Any
from datetime import datetime
from core.plugin_base import PluginResult, SearchType
import logging


class ResultAggregator:
    def __init__(self):
        self.results: List[PluginResult] = []
        self.search_metadata = {
            "start_time": None,
            "end_time": None,
            "total_plugins": 0,
            "successful_plugins": 0,
            "failed_plugins": 0
        }

    def add_result(self, result: PluginResult):
        self.results.append(result)
        if result.success:
            self.search_metadata["successful_plugins"] += 1
        else:
            self.search_metadata["failed_plugins"] += 1
            logging.warning(f"Plugin {result.plugin_name} failed: {result.error}")

    def start_search(self, total_plugins: int):
        self.results = []
        self.search_metadata = {
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "total_plugins": total_plugins,
            "successful_plugins": 0,
            "failed_plugins": 0
        }

    def end_search(self):
        self.search_metadata["end_time"] = datetime.now().isoformat()

    def get_results_by_plugin(self, plugin_name: str) -> List[PluginResult]:
        return [r for r in self.results if r.plugin_name == plugin_name]

    def get_successful_results(self) -> List[PluginResult]:
        return [r for r in self.results if r.success]

    def get_failed_results(self) -> List[PluginResult]:
        return [r for r in self.results if not r.success]

    def deduplicate_data(self) -> Dict[str, Any]:
        unique_data = {}
        for result in self.get_successful_results():
            if not result.data:
                continue
            
            for key, value in result.data.items():
                if key not in unique_data:
                    unique_data[key] = []
                
                if isinstance(value, list):
                    for item in value:
                        if item not in unique_data[key]:
                            unique_data[key].append(item)
                elif value not in unique_data[key]:
                    unique_data[key].append(value)
        
        return unique_data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.search_metadata,
            "results": [r.to_dict() for r in self.results],
            "summary": {
                "total_results": len(self.results),
                "successful": self.search_metadata["successful_plugins"],
                "failed": self.search_metadata["failed_plugins"],
                "unique_data": self.deduplicate_data()
            }
        }

    def get_summary(self) -> str:
        successful = self.search_metadata["successful_plugins"]
        failed = self.search_metadata["failed_plugins"]
        total = self.search_metadata["total_plugins"]
        
        summary = f"\n=== Search Summary ===\n"
        summary += f"Total Plugins: {total}\n"
        summary += f"Successful: {successful}\n"
        summary += f"Failed: {failed}\n"
        
        if self.search_metadata["start_time"] and self.search_metadata["end_time"]:
            start = datetime.fromisoformat(self.search_metadata["start_time"])
            end = datetime.fromisoformat(self.search_metadata["end_time"])
            duration = (end - start).total_seconds()
            summary += f"Duration: {duration:.2f} seconds\n"
        
        return summary

    def clear(self):
        self.results = []
        self.search_metadata = {
            "start_time": None,
            "end_time": None,
            "total_plugins": 0,
            "successful_plugins": 0,
            "failed_plugins": 0
        }
