# OSINT Framework

A comprehensive, modular Open Source Intelligence (OSINT) tool that integrates multiple trending open-source intelligence tools into a unified, production-ready platform.

## Features

- 🔌 **Plugin-Based Architecture**: Easily extensible with self-contained plugin modules
- 🎯 **Multi-Tool Search**: Search across all integrated tools simultaneously
- 📊 **Multiple Export Formats**: JSON, HTML, CSV, and SQLite database exports
- 🎨 **Rich CLI Interface**: Beautiful, interactive menu-driven interface
- ⚡ **Parallel Execution**: Run multiple searches concurrently for faster results
- 📝 **Comprehensive Logging**: Full audit trail and debugging support
- 🔧 **Configuration Management**: Centralized configuration and credential storage

## Architecture

### Project Structure

```
osint-tool/
├── main.py                     # Entry point
├── config/
│   ├── __init__.py
│   ├── settings.py             # Configuration management
│   └── credentials.json        # API keys and credentials (gitignored)
├── core/
│   ├── __init__.py
│   ├── plugin_base.py          # Abstract plugin base class
│   ├── engine.py               # Core search orchestration
│   ├── result_handler.py       # Result aggregation and deduplication
│   └── exporter.py             # Multi-format export functionality
├── plugins/
│   ├── __init__.py             # Plugin discovery
│   ├── sherlock_plugin.py      # Sherlock username search integration
│   └── [future plugins]
├── ui/
│   ├── __init__.py
│   ├── menu.py                 # Interactive CLI menu system
│   └── display.py              # Rich terminal formatting
├── results/                    # Export output directory
├── logs/                       # Application logs
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── .gitignore
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Ubuntu (or any Linux distribution)
- pip (Python package manager)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd osint-tool
```

2. **Create a virtual environment (recommended)**
```bash
python3 -m venv venv
source venv/bin/activate  # On Ubuntu/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Verify installation**
```bash
python main.py
```

## Usage

### Starting the Tool

```bash
python main.py
```

### Main Menu Options

1. **Search All Tools**: Run a query across all enabled plugins simultaneously
2. **Select Individual Tool**: Choose a specific tool for targeted searching
3. **View Available Tools**: Display all registered plugins and their capabilities
4. **Configuration**: Manage plugin settings and credentials
5. **Exit**: Close the application

### Search Types

The framework supports multiple search types:
- `username`: Search for usernames across platforms
- `email`: Search for email addresses
- `domain`: Domain name reconnaissance
- `url`: URL investigation
- `phone`: Phone number lookup
- `ip`: IP address intelligence

### Export Formats

Results can be exported in multiple formats:

- **JSON**: Machine-readable format for integration
- **HTML**: Beautiful, styled report with full details
- **CSV**: Spreadsheet-compatible format
- **SQLite**: Relational database for complex queries

All exports are timestamped and saved to the `results/` directory.

## Integrated Tools

### Sherlock Plugin

**Description**: Username search across 300+ social networks

**Search Types**: Username

**Usage**: The Sherlock plugin automatically searches for a given username across hundreds of social media platforms and websites.

**Example Results**:
- List of found profiles with URLs
- Total number of matches
- Sites checked

## Creating New Plugins

The framework is designed for easy extension. To create a new plugin:

1. **Create a new file** in the `plugins/` directory: `your_plugin.py`

2. **Implement the PluginBase interface**:

```python
from core.plugin_base import PluginBase, SearchType, PluginResult
from typing import List

class YourPlugin(PluginBase):
    @property
    def name(self) -> str:
        return "Your Plugin Name"
    
    @property
    def description(self) -> str:
        return "Description of what your plugin does"
    
    @property
    def supported_search_types(self) -> List[SearchType]:
        return [SearchType.USERNAME, SearchType.EMAIL]
    
    def run_search(self, query: str, search_type: SearchType) -> PluginResult:
        # Implement your search logic here
        try:
            # Perform search
            results = your_search_function(query)
            
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=True,
                data=results
            )
        except Exception as e:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=str(e)
            )
```

3. **Plugin Discovery**: The framework automatically discovers and loads plugins ending with `_plugin.py`

## Configuration

### Settings

Default settings are defined in `config/settings.py`:

```python
{
    "export": {
        "default_format": "json",
        "auto_export": False,
        "output_directory": "./results"
    },
    "search": {
        "timeout": 60,
        "max_concurrent": 5
    },
    "logging": {
        "level": "INFO",
        "file": "./logs/osint_tool.log"
    }
}
```

### Credentials

API keys and credentials are stored in `config/credentials.json` (automatically created on first run):

```json
{
    "api_keys": {
        "example_api": "your_api_key_here"
    },
    "credentials": {
        "example_service": {
            "username": "your_username",
            "password": "your_password"
        }
    }
}
```

**Note**: This file is gitignored for security.

## Logging

All operations are logged to:
- Console output (INFO level and above)
- Log file: `logs/osint_tool.log` (configurable)

Logs include:
- Plugin registration and discovery
- Search execution and results
- Errors and warnings
- Export operations

## Development

### Running Tests

```bash
# Run with verbose logging
python main.py
```

### Debugging

Set logging level to DEBUG in `config/settings.py`:

```python
"logging": {
    "level": "DEBUG"
}
```

## Troubleshooting

### Sherlock Not Found

If you get "Sherlock not found" errors:

```bash
pip install sherlock-project
```

### Permission Errors

Ensure the application has write permissions for:
- `results/` directory
- `logs/` directory
- `config/credentials.json`

### Import Errors

Make sure you're running from the project root:
```bash
cd /path/to/osint-tool
python main.py
```

## Security Considerations

- Never commit `config/credentials.json` to version control
- Use environment variables for sensitive data in production
- Regularly update dependencies for security patches
- Review plugin code before adding to production
- Be mindful of rate limits on external APIs

## Roadmap

Future plugin integrations:
- [ ] theHarvester (email/domain reconnaissance)
- [ ] Maltego transforms
- [ ] SpiderFoot integration
- [ ] Shodan API integration
- [ ] Have I Been Pwned API
- [ ] WHOIS lookups
- [ ] DNS enumeration tools
- [ ] Social media scrapers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your plugin or feature
4. Test thoroughly
5. Submit a pull request

## License

[Specify your license here]

## Acknowledgments

- Sherlock Project for username enumeration
- Rich library for beautiful terminal output
- The OSINT community for inspiration

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ for the OSINT community**
