import json
import csv
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from core.result_handler import ResultAggregator
from config.settings import get_settings
import logging


class Exporter:
    def __init__(self, results: ResultAggregator):
        self.results = results
        self.settings = get_settings()
        self.output_dir = Path(self.settings.get_setting("export", "output_directory"))
        self.output_dir.mkdir(exist_ok=True)

    def _generate_filename(self, extension: str, query: str = "search") -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = "".join(c if c.isalnum() else "_" for c in query)[:30]
        filename = f"{safe_query}_{timestamp}.{extension}"
        return self.output_dir / filename

    def export_json(self, filepath: Optional[Path] = None, query: str = "search") -> Path:
        if filepath is None:
            filepath = self._generate_filename("json", query)
        
        try:
            data = self.results.to_dict()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logging.info(f"JSON export saved to {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"Failed to export JSON: {e}")
            raise

    def export_html(self, filepath: Optional[Path] = None, query: str = "search") -> Path:
        if filepath is None:
            filepath = self._generate_filename("html", query)
        
        try:
            data = self.results.to_dict()
            html = self._generate_html(data, query)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            logging.info(f"HTML export saved to {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"Failed to export HTML: {e}")
            raise

    def _generate_html(self, data: Dict[str, Any], query: str) -> str:
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT Search Results - {query}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .result {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .success {{ border-left: 4px solid #10b981; }}
        .failure {{ border-left: 4px solid #ef4444; }}
        .plugin-name {{
            font-size: 1.2em;
            font-weight: bold;
            color: #1f2937;
            margin-bottom: 10px;
        }}
        .data-section {{
            background: #f9fafb;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
        }}
        .metadata {{
            color: #6b7280;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        .error {{
            color: #ef4444;
            padding: 10px;
            background: #fee2e2;
            border-radius: 5px;
            margin-top: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        th {{
            background-color: #f3f4f6;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 OSINT Search Results</h1>
        <p>Query: <strong>{query}</strong></p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <table>
            <tr>
                <th>Total Plugins</th>
                <th>Successful</th>
                <th>Failed</th>
                <th>Duration</th>
            </tr>
            <tr>
                <td>{data['metadata']['total_plugins']}</td>
                <td style="color: #10b981;">{data['metadata']['successful_plugins']}</td>
                <td style="color: #ef4444;">{data['metadata']['failed_plugins']}</td>
                <td>{self._calculate_duration(data['metadata'])}</td>
            </tr>
        </table>
    </div>
    
    <h2>Results</h2>
"""
        
        for result in data['results']:
            status_class = "success" if result['success'] else "failure"
            status_text = "✓ Success" if result['success'] else "✗ Failed"
            
            html += f"""
    <div class="result {status_class}">
        <div class="plugin-name">{result['plugin_name']}</div>
        <p><strong>Status:</strong> {status_text}</p>
        <p><strong>Search Type:</strong> {result['search_type']}</p>
        <p><strong>Query:</strong> {result['query']}</p>
"""
            
            if result['success'] and result['data']:
                html += '<div class="data-section"><h3>Data</h3>'
                html += self._format_data_html(result['data'])
                html += '</div>'
            
            if result['error']:
                html += f'<div class="error"><strong>Error:</strong> {result["error"]}</div>'
            
            html += f'<div class="metadata">Timestamp: {result["timestamp"]}</div>'
            html += '</div>'
        
        html += """
</body>
</html>"""
        return html

    def _format_data_html(self, data: Dict[str, Any]) -> str:
        html = '<table>'
        for key, value in data.items():
            html += f'<tr><th>{key}</th><td>{self._format_value(value)}</td></tr>'
        html += '</table>'
        return html

    def _format_value(self, value: Any) -> str:
        if isinstance(value, (list, dict)):
            return f'<pre>{json.dumps(value, indent=2)}</pre>'
        return str(value)

    def _calculate_duration(self, metadata: Dict[str, Any]) -> str:
        if metadata['start_time'] and metadata['end_time']:
            start = datetime.fromisoformat(metadata['start_time'])
            end = datetime.fromisoformat(metadata['end_time'])
            duration = (end - start).total_seconds()
            return f"{duration:.2f}s"
        return "N/A"

    def export_csv(self, filepath: Optional[Path] = None, query: str = "search") -> Path:
        if filepath is None:
            filepath = self._generate_filename("csv", query)
        
        try:
            data = self.results.to_dict()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Plugin', 'Status', 'Search Type', 'Query', 'Timestamp', 'Error', 'Data'])
                
                for result in data['results']:
                    writer.writerow([
                        result['plugin_name'],
                        'Success' if result['success'] else 'Failed',
                        result['search_type'],
                        result['query'],
                        result['timestamp'],
                        result.get('error', ''),
                        json.dumps(result.get('data', {}))
                    ])
            
            logging.info(f"CSV export saved to {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"Failed to export CSV: {e}")
            raise

    def export_sqlite(self, filepath: Optional[Path] = None, query: str = "search") -> Path:
        if filepath is None:
            filepath = self._generate_filename("db", query)
        
        try:
            conn = sqlite3.connect(filepath)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT,
                    end_time TEXT,
                    total_plugins INTEGER,
                    successful_plugins INTEGER,
                    failed_plugins INTEGER
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_id INTEGER,
                    plugin_name TEXT,
                    search_type TEXT,
                    query TEXT,
                    success BOOLEAN,
                    data TEXT,
                    error TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (search_id) REFERENCES searches(id)
                )
            ''')
            
            data = self.results.to_dict()
            metadata = data['metadata']
            
            cursor.execute('''
                INSERT INTO searches (start_time, end_time, total_plugins, successful_plugins, failed_plugins)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                metadata['start_time'],
                metadata['end_time'],
                metadata['total_plugins'],
                metadata['successful_plugins'],
                metadata['failed_plugins']
            ))
            
            search_id = cursor.lastrowid
            
            for result in data['results']:
                cursor.execute('''
                    INSERT INTO results (search_id, plugin_name, search_type, query, success, data, error, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    search_id,
                    result['plugin_name'],
                    result['search_type'],
                    result['query'],
                    result['success'],
                    json.dumps(result.get('data', {})),
                    result.get('error'),
                    result['timestamp']
                ))
            
            conn.commit()
            conn.close()
            
            logging.info(f"SQLite export saved to {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"Failed to export SQLite: {e}")
            raise

    def export_all(self, query: str = "search") -> Dict[str, Path]:
        results = {}
        try:
            results['json'] = self.export_json(query=query)
            results['html'] = self.export_html(query=query)
            results['csv'] = self.export_csv(query=query)
            results['sqlite'] = self.export_sqlite(query=query)
        except Exception as e:
            logging.error(f"Error during export_all: {e}")
        return results
