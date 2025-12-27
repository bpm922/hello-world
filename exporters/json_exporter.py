"""
JSON Exporter for Kirwada OSINT Tool
"""

import json
from typing import List, Dict, Any
from .base_exporter import BaseExporter


class JsonExporter(BaseExporter):
    """Export results to JSON format"""
    
    @property
    def format_name(self) -> str:
        return 'json'
    
    def export(self, results: List[Dict[str, Any]], output_file: str) -> bool:
        """
        Export results to JSON file
        
        Args:
            results: List of plugin results
            output_file: Path to output file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            self.log_info(f"Exporting results to JSON: {output_file}")
            
            # Ensure output directory exists
            self._ensure_output_dir(output_file)
            
            # Prepare export data with metadata
            export_data = {
                'metadata': self._generate_metadata(results),
                'results': self._format_results(results)
            }
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)
            
            self.log_info(f"Successfully exported {len(results)} results to {output_file}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to export JSON: {str(e)}")
            return False
    
    def _format_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format results for JSON export"""
        formatted = []
        
        for result in results:
            formatted.append({
                'source': result.get('source', ''),
                'search_type': result.get('search_type', ''),
                'query': result.get('query', ''),
                'success': result.get('success', True),
                'execution_time': result.get('execution_time', None),
                'error_message': result.get('error_message', None),
                'data': result.get('data', []),
                'metadata': result.get('metadata', {})
            })
        
        return formatted
