"""
Base Exporter Class for Kirwada OSINT Tool
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path


class BaseExporter(ABC):
    """Abstract base class for all result exporters"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"Kirwada.Exporter.{self.__class__.__name__}")
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return the format name (e.g., 'json', 'csv', 'txt')"""
        pass
    
    @abstractmethod
    def export(self, results: List[Dict[str, Any]], output_file: str) -> bool:
        """
        Export results to a file
        
        Args:
            results: List of plugin results
            output_file: Path to output file
            
        Returns:
            True if export successful, False otherwise
        """
        pass
    
    def _generate_metadata(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate metadata for the export"""
        return {
            'export_time': datetime.now().isoformat(),
            'total_results': len(results),
            'sources': list(set(r.get('source', '') for r in results)),
            'queries': list(set(r.get('query', '') for r in results))
        }
    
    def _ensure_output_dir(self, output_file: str):
        """Ensure output directory exists"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_info(self, message: str):
        """Log an info message"""
        self.logger.info(message)
    
    def log_error(self, message: str):
        """Log an error message"""
        self.logger.error(message)
