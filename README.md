# Kirwada OSINT Tool

![Kirwada Logo](https://img.shields.io/badge/Kirwada-OSINT-blue)
![Python](https://img.shields.io/badge/Python-3.7%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

An open-source intelligence gathering tool with multiple reconnaissance plugins for cybersecurity professionals, penetration testers, and security researchers.

## Features

- **Multi-Plugin Architecture**: 7 integrated reconnaissance tools
- **Standardized Results**: Unified output format across all plugins
- **Multiple Export Formats**: JSON, CSV, and TXT export capabilities
- **Comprehensive Coverage**: From social media to infrastructure analysis
- **Easy Configuration**: Centralized API key management
- **Interactive CLI**: User-friendly command-line interface
- **Extensible Design**: Easy to add new plugins

## Available Plugins

### 1. Photon Plugin
Website reconnaissance and data extraction
- Extracts URLs, emails, phone numbers from target websites
- Discovers JavaScript files and API endpoints
- Maps website structure and finds important files
- **Search Types**: `url`, `domain`

### 2. TheHarvester Plugin
Email and subdomain discovery
- Multiple data source integration (Google, Bing, DuckDuckGo)
- Email extraction and analysis
- Subdomain enumeration
- **Search Types**: `domain`, `company`

### 3. Spider Plugin
Web crawling and link discovery
- Comprehensive website structure mapping
- Technology stack detection
- Form and endpoint enumeration
- Internal/external link categorization
- **Search Types**: `url`, `domain`

### 4. Shodan Plugin
IP/device intelligence and metadata
- Service and vulnerability detection
- Network infrastructure analysis
- Device metadata extraction
- **Requires API Key**
- **Search Types**: `ip`, `domain`, `net`

### 5. Have I Been Pwned (HIBP) Plugin
Breach data search
- Email breach data lookup
- Compromised account detection
- Password exposure checking
- Free API integration
- **Search Types**: `email`, `username`

### 6. Whois/DNS Plugin
Domain ownership and DNS information
- Domain registration details
- DNS records lookup (A, MX, NS, TXT, CNAME, AAAA)
- IP reverse lookup
- DNSSEC verification
- **Search Types**: `domain`, `ip`

### 7. Sherlock Plugin
Username search across social media
- 300+ supported platforms
- Real-time username availability check
- Social media account discovery
- **Search Types**: `username`

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/kirwada.git
cd kirwada
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run Kirwada:
```bash
python main.py
```

### Dependencies

Create a `requirements.txt` file with the following:

```txt
# Core dependencies
requests>=2.28.0
beautifulsoup4>=4.11.0
dnspython>=2.2.0

# Optional plugins
python-whois>=0.8.0
shodan>=1.31.0

# For username search
sherlock>=0.14.0

# Development (optional)
pytest>=7.0.0
black>=22.0.0
flake8>=4.0.0
```

## Configuration

### API Keys

Some plugins require API keys for full functionality:

#### Shodan API Key (Required for Shodan plugin)
1. Sign up at https://shodan.io/
2. Get your API key from https://developer.shodan.io/api
3. Configure in Kirwada:
   - Option 1: Use menu option 6 (Configure API Keys)
   - Option 2: Edit `config/plugin_config.json`:
     ```json
     {
       "plugins": {
         "shodan": {
           "api_key": "YOUR_SHODAN_API_KEY_HERE"
         }
       }
     }
     ```
   - Option 3: Set environment variable:
     ```bash
     export SHODAN_API_KEY="your_api_key_here"
     ```

#### Have I Been Pwned API Key (Optional but recommended)
1. Sign up at https://haveibeenpwned.com/API/Key
2. Purchase an API key (subscription required for commercial use)
3. Configure in `config/plugin_config.json` or use menu option 6

### Plugin Configuration

Edit `config/plugin_config.json` to customize plugin behavior:

```json
{
  "plugins": {
    "photon": {
      "enabled": true,
      "default_max_depth": 2,
      "default_max_pages": 100
    },
    "theharvester": {
      "enabled": true,
      "default_sources": ["bing", "google", "duckduckgo"]
    },
    "spider": {
      "enabled": true,
      "default_max_depth": 3,
      "default_max_pages": 200
    }
  },
  "exporters": {
    "default_format": "json",
    "output_directory": "./results"
  },
  "logging": {
    "level": "INFO",
    "file": "./kirwada.log"
  }
}
```

## Usage

### Interactive Mode

Run Kirwada and use the interactive menu:

```bash
python main.py
```

Menu options:
1. **Search with Single Tool** - Run a specific plugin
2. **Search All Tools** - Run all enabled plugins simultaneously
3. **List Available Plugins** - View all plugins and their status
4. **Export Results** - Export stored results to file
5. **View Results** - View previously stored results
6. **Configure API Keys** - Set up API keys for plugins
7. **Help** - Display help information
8. **Exit** - Exit the application
9. **About** - About Kirwada

### Example Searches

#### Search with Single Plugin
```
1. Search with Single Tool
Available Plugins:
1. PHOTON (✓) - Website reconnaissance and data extraction
2. THEHARVESTER (✓) - Email and subdomain discovery
3. SPIDER (✓) - Web crawling and link discovery
4. SHODAN (⚠) - IP/device intelligence using Shodan API
5. HIBP (✓) - Breach data search using Have I Been Pwned API
6. WHOIS (✓) - Domain ownership and DNS records lookup

Select plugin (1-6): 1
Enter search query for photon: example.com

Searching with photon...
[INFO] Starting Photon crawl on https://example.com
...
```

#### Search All Tools
```
2. Search All Tools
Enter search query: example.com

Searching with all plugins...
------------------------------------------------------------
[1/6] Running photon... ✓
[2/6] Running theharvester... ✓
[3/6] Running spider... ✓
[4/6] Running shodan... ✗ (Error: API key not configured)
[5/6] Running hibp... ✓
[6/6] Running whois... ✓
------------------------------------------------------------

Completed: 5 searches
```

### Programmatic Usage

```python
from main import Kirwada

# Initialize Kirwada
app = Kirwada()

# Search with all plugins
results = app.run_single_search("example.com")

# Search with specific plugin
results = app.run_single_search("example.com", plugin_name="photon")

# Search with specific search type
results = app.run_single_search("user123", plugin_name="sherlock", search_type="username")

# Access results
for result in results:
    print(f"Plugin: {result.source}")
    print(f"Success: {result.success}")
    print(f"Data: {result.data}")
```

### Exporting Results

Export results to different formats:

```python
from exporters import JsonExporter, CsvExporter, TxtExporter

# Prepare results
results_dicts = [
    {
        'source': 'photon',
        'search_type': 'url',
        'query': 'example.com',
        'data': [...],
        'success': True,
        'execution_time': 2.5
    }
]

# Export to JSON
json_exporter = JsonExporter()
json_exporter.export(results_dicts, 'results/output.json')

# Export to CSV
csv_exporter = CsvExporter()
csv_exporter.export(results_dicts, 'results/output.csv')

# Export to TXT
txt_exporter = TxtExporter()
txt_exporter.export(results_dicts, 'results/output.txt')
```

## Sample Output

### Photon Plugin Output
```json
{
  "source": "photon",
  "search_type": "url",
  "query": "example.com",
  "data": [
    {
      "urls": ["https://example.com", "https://example.com/about"],
      "emails": ["contact@example.com", "info@example.com"],
      "phone_numbers": ["+1-555-123-4567"],
      "javascript_files": ["https://example.com/js/app.js"],
      "files": ["https://example.com/docs/brochure.pdf"],
      "endpoints": ["/api/users", "/api/login"],
      "pages_crawled": 15,
      "max_depth_reached": 2
    }
  ],
  "success": true,
  "execution_time": 3.45
}
```

### Shodan Plugin Output
```json
{
  "source": "shodan",
  "search_type": "ip",
  "query": "8.8.8.8",
  "data": [
    {
      "ip": "8.8.8.8",
      "hostnames": ["dns.google"],
      "country_name": "United States",
      "org": "Google LLC",
      "isp": "Google LLC",
      "ports": [53, 443],
      "vulns": [],
      "services": [...]
    }
  ],
  "success": true,
  "execution_time": 0.52
}
```

### HIBP Plugin Output
```json
{
  "source": "hibp",
  "search_type": "email",
  "query": "test@example.com",
  "data": [
    {
      "breach_count": 3,
      "breaches": [...],
      "paste_count": 0,
      "pastes": [],
      "summary": {
        "total_breaches": 3,
        "data_classes_compromised": ["Email addresses", "Passwords", "Names"],
        "sites": [...],
        "total_records_exposed": 125000000
      }
    }
  ],
  "success": true,
  "execution_time": 1.23
}
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_photon_plugin.py

# Run with coverage
pytest --cov=plugins tests/
```

## Development

### Adding a New Plugin

1. Create a new plugin file in `plugins/`:
```python
from plugins.base_plugin import BasePlugin, PluginResult

class MyPlugin(BasePlugin):
    @property
    def description(self) -> str:
        return "My plugin description"
    
    @property
    def search_types(self) -> List[str]:
        return ['username', 'email']
    
    def search(self, query: str, search_type: str = 'default', **kwargs) -> PluginResult:
        # Implement your search logic here
        pass
```

2. The plugin will be auto-discovered and loaded automatically.

### Code Style

Follow PEP 8 guidelines:
```bash
# Format code
black .

# Lint code
flake8 plugins/ exporters/ main.py
```

## Troubleshooting

### Common Issues

1. **"Shodan API key not configured"**
   - Configure your Shodan API key using menu option 6
   - Or set the `SHODAN_API_KEY` environment variable

2. **"python-whois module not installed"**
   - Install with: `pip install python-whois`
   - The Whois plugin will have limited functionality without it

3. **"Rate limit exceeded"**
   - Some APIs have rate limits (HIBP, Shodan)
   - Wait before retrying or get a paid API plan

4. **"No results found"**
   - Check your search query
   - Try different search types
   - Some plugins may return empty results for certain queries

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

**Legal Warning**: This tool is intended for educational purposes and authorized security testing only. Users are responsible for ensuring they have proper authorization before using this tool on any system. The authors are not responsible for any misuse of this software.

## Acknowledgments

- [Sherlock Project](https://github.com/sherlock-project/sherlock) - Username search
- [Photon](https://github.com/s0md3v/Photon) - Website reconnaissance
- [TheHarvester](https://github.com/laramies/theHarvester) - OSINT tool
- [Shodan](https://www.shodan.io/) - Internet intelligence
- [Have I Been Pwned](https://haveibeenpwned.com/) - breach data

## Contact

- GitHub: https://github.com/yourusername/kirwada
- Issues: https://github.com/yourusername/kirwada/issues
- Email: your-email@example.com

## Changelog

### Version 1.0.0 (2024-12-27)
- Initial release
- 7 integrated reconnaissance plugins
- Multi-format export support
- Interactive CLI interface
- Comprehensive documentation

---

Made with ❤️ by the Kirwada Team
