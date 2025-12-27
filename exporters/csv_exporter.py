"""
CSV Exporter for Kirwada OSINT Tool
"""

import csv
from typing import List, Dict, Any
from .base_exporter import BaseExporter


class CsvExporter(BaseExporter):
    """Export results to CSV format"""
    
    @property
    def format_name(self) -> str:
        return 'csv'
    
    def export(self, results: List[Dict[str, Any]], output_file: str) -> bool:
        """
        Export results to CSV file
        
        Args:
            results: List of plugin results
            output_file: Path to output file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            self.log_info(f"Exporting results to CSV: {output_file}")
            
            # Ensure output directory exists
            self._ensure_output_dir(output_file)
            
            # Flatten results for CSV
            rows = self._flatten_results(results)
            
            if not rows:
                self.log_info("No results to export")
                # Still create file with headers
                rows = [{'source': '', 'search_type': '', 'query': '', 'success': '', 'data': ''}]
            
            # Get all unique columns
            fieldnames = set()
            for row in rows:
                fieldnames.update(row.keys())
            fieldnames = sorted(list(fieldnames))
            
            # Write to file
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            self.log_info(f"Successfully exported {len(rows)} rows to {output_file}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to export CSV: {str(e)}")
            return False
    
    def _flatten_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Flatten results for CSV export"""
        rows = []
        
        for result in results:
            # Create base row
            row = {
                'source': result.get('source', ''),
                'search_type': result.get('search_type', ''),
                'query': result.get('query', ''),
                'success': str(result.get('success', True)),
                'execution_time': str(result.get('execution_time', '')),
                'error_message': result.get('error_message', '')
            }
            
            # Flatten data from the result
            data_list = result.get('data', [])
            if data_list and isinstance(data_list, list) and len(data_list) > 0:
                data = data_list[0]
                
                # Add common fields from data
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key not in row:
                            # Convert complex values to strings
                            if isinstance(value, (list, dict)):
                                row[key] = str(value)[:1000]  # Limit length
                            else:
                                row[key] = str(value) if value is not None else ''
            
            rows.append(row)
        
        return rows
