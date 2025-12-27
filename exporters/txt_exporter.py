"""
TXT Exporter for Kirwada OSINT Tool
"""

from typing import List, Dict, Any
from .base_exporter import BaseExporter


class TxtExporter(BaseExporter):
    """Export results to plain text format"""
    
    @property
    def format_name(self) -> str:
        return 'txt'
    
    def export(self, results: List[Dict[str, Any]], output_file: str) -> bool:
        """
        Export results to TXT file
        
        Args:
            results: List of plugin results
            output_file: Path to output file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            self.log_info(f"Exporting results to TXT: {output_file}")
            
            # Ensure output directory exists
            self._ensure_output_dir(output_file)
            
            # Generate text content
            content = self._format_results(results)
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log_info(f"Successfully exported {len(results)} results to {output_file}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to export TXT: {str(e)}")
            return False
    
    def _format_results(self, results: List[Dict[str, Any]]) -> str:
        """Format results for text export"""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("KIRWADA OSINT TOOL - RESULTS REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Metadata
        metadata = self._generate_metadata(results)
        lines.append("METADATA")
        lines.append("-" * 40)
        lines.append(f"Export Time: {metadata['export_time']}")
        lines.append(f"Total Results: {metadata['total_results']}")
        lines.append(f"Sources: {', '.join(metadata['sources'])}")
        lines.append(f"Queries: {', '.join(metadata['queries'])}")
        lines.append("")
        
        # Results
        lines.append("RESULTS")
        lines.append("=" * 80)
        lines.append("")
        
        for i, result in enumerate(results, 1):
            lines.append(f"[{i}] Source: {result.get('source', 'Unknown').upper()}")
            lines.append("-" * 80)
            lines.append(f"Query: {result.get('query', '')}")
            lines.append(f"Search Type: {result.get('search_type', '')}")
            lines.append(f"Success: {result.get('success', True)}")
            
            if result.get('execution_time'):
                lines.append(f"Execution Time: {result['execution_time']:.2f}s")
            
            if result.get('error_message'):
                lines.append(f"Error: {result['error_message']}")
            
            # Format data
            data_list = result.get('data', [])
            if data_list and isinstance(data_list, list) and len(data_list) > 0:
                data = data_list[0]
                if isinstance(data, dict):
                    lines.append("")
                    lines.append("Data:")
                    self._format_dict(data, lines, indent="  ")
                elif isinstance(data, (list, str)):
                    lines.append("")
                    lines.append("Data:")
                    lines.append(f"  {str(data)[:1000]}")
            
            lines.append("")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_dict(self, data: Dict[str, Any], lines: List[str], indent: str = ""):
        """Recursively format dictionary for text output"""
        for key, value in sorted(data.items()):
            if isinstance(value, dict):
                lines.append(f"{indent}{key}:")
                self._format_dict(value, lines, indent + "  ")
            elif isinstance(value, list):
                if value and len(value) > 0:
                    lines.append(f"{indent}{key}:")
                    for item in value[:20]:  # Limit to 20 items
                        if isinstance(item, dict):
                            lines.append(f"{indent}  -")
                            self._format_dict(item, lines, indent + "    ")
                        else:
                            lines.append(f"{indent}  - {str(item)[:200]}")
                    if len(value) > 20:
                        lines.append(f"{indent}  ... ({len(value) - 20} more items)")
                else:
                    lines.append(f"{indent}{key}: []")
            else:
                # Truncate long values
                value_str = str(value)
                if len(value_str) > 500:
                    value_str = value_str[:500] + "..."
                lines.append(f"{indent}{key}: {value_str}")
