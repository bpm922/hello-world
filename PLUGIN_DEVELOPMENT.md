# Plugin Development Guide

This guide explains how to create new plugins for the OSINT Framework.

## Plugin Architecture

All plugins inherit from the `PluginBase` abstract class and implement a standard interface. This ensures consistency and allows the framework to automatically discover and integrate new tools.

## Creating a New Plugin

### Step 1: Create Plugin File

Create a new file in the `plugins/` directory with the naming convention: `<toolname>_plugin.py`

Example: `whois_plugin.py`, `haveibeenpwned_plugin.py`, `shodan_plugin.py`

### Step 2: Implement the Plugin Class

```python
from core.plugin_base import PluginBase, SearchType, PluginResult
from typing import List
import logging


class YourToolPlugin(PluginBase):
    """
    Brief description of what your plugin does.
    """
    
    def __init__(self):
        super().__init__()
        # Initialize any required resources
        # Check if the tool is installed/configured
    
    @property
    def name(self) -> str:
        """Return the display name of your plugin"""
        return "Your Tool Name"
    
    @property
    def description(self) -> str:
        """Return a brief description of what your plugin does"""
        return "Brief description of functionality"
    
    @property
    def supported_search_types(self) -> List[SearchType]:
        """Return list of SearchType enums this plugin supports"""
        return [
            SearchType.USERNAME,
            SearchType.EMAIL,
            # Add other types as needed
        ]
    
    def run_search(self, query: str, search_type: SearchType) -> PluginResult:
        """
        Execute the search and return standardized results.
        
        Args:
            query: The search term/value
            search_type: The type of search being performed
            
        Returns:
            PluginResult object with success/failure and data
        """
        # Validate search type
        if not self.validate_search_type(search_type):
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Unsupported search type: {search_type.value}"
            )
        
        try:
            # Perform your search logic here
            results = self._perform_search(query, search_type)
            
            # Return success result
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=True,
                data=results,
                metadata={
                    # Optional metadata about the search
                    'api_version': '1.0',
                    'total_results': len(results)
                }
            )
            
        except Exception as e:
            # Return failure result
            logging.error(f"{self.name} error: {e}")
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=str(e)
            )
    
    def _perform_search(self, query: str, search_type: SearchType) -> dict:
        """
        Internal method to perform the actual search.
        Implement your tool-specific logic here.
        """
        # Your implementation here
        pass
```

## Search Types

The framework supports the following search types:

```python
class SearchType(Enum):
    USERNAME = "username"    # Social media usernames
    EMAIL = "email"          # Email addresses
    DOMAIN = "domain"        # Domain names
    URL = "url"              # URLs
    PHONE = "phone"          # Phone numbers
    IP = "ip"                # IP addresses
```

Your plugin should specify which search types it supports in the `supported_search_types` property.

## PluginResult Structure

Always return a `PluginResult` object:

### Success Result

```python
PluginResult(
    plugin_name=self.name,
    search_type=search_type,
    query=query,
    success=True,
    data={
        # Your result data as a dictionary
        'key1': 'value1',
        'results': [item1, item2, item3],
        'count': 3
    },
    metadata={
        # Optional metadata
        'timestamp': '2024-01-01T12:00:00',
        'api_calls': 1
    }
)
```

### Failure Result

```python
PluginResult(
    plugin_name=self.name,
    search_type=search_type,
    query=query,
    success=False,
    error="Clear error message describing what went wrong"
)
```

## Best Practices

### 1. Error Handling

Always wrap your search logic in try-except blocks:

```python
try:
    # Search logic
    results = api.search(query)
    return PluginResult(...)
except ConnectionError as e:
    return PluginResult(..., success=False, error=f"Connection failed: {e}")
except TimeoutError as e:
    return PluginResult(..., success=False, error=f"Search timed out: {e}")
except Exception as e:
    return PluginResult(..., success=False, error=f"Unexpected error: {e}")
```

### 2. API Keys and Credentials

Use the configuration system to access API keys:

```python
from config.settings import get_settings

class YourPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        settings = get_settings()
        self.api_key = settings.get_credential('your_service', 'api_key')
        
        if not self.api_key:
            logging.warning(f"{self.name}: No API key configured")
```

Users can add credentials to `config/credentials.json`:

```json
{
    "your_service": {
        "api_key": "your_api_key_here"
    }
}
```

### 3. Timeouts

Always implement timeouts for external API calls:

```python
import requests

response = requests.get(
    url,
    timeout=30  # 30 second timeout
)
```

### 4. Logging

Use Python's logging module for debugging:

```python
import logging

logging.info(f"Starting search for {query}")
logging.warning(f"API rate limit approaching")
logging.error(f"Failed to connect: {error}")
```

### 5. Rate Limiting

Respect API rate limits:

```python
import time

class YourPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
    
    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def run_search(self, query, search_type):
        self._rate_limit()
        # Perform search...
```

### 6. Data Validation

Validate input before processing:

```python
def run_search(self, query: str, search_type: SearchType) -> PluginResult:
    # Validate query
    if not query or not query.strip():
        return PluginResult(
            plugin_name=self.name,
            search_type=search_type,
            query=query,
            success=False,
            error="Query cannot be empty"
        )
    
    # For email searches, validate email format
    if search_type == SearchType.EMAIL:
        if '@' not in query:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error="Invalid email format"
            )
```

## Example: Complete Plugin

Here's a complete example of a simple WHOIS plugin:

```python
from core.plugin_base import PluginBase, SearchType, PluginResult
from typing import List
import subprocess
import logging


class WhoisPlugin(PluginBase):
    """
    WHOIS lookup plugin for domain information.
    """
    
    @property
    def name(self) -> str:
        return "WHOIS"
    
    @property
    def description(self) -> str:
        return "Domain registration and ownership information"
    
    @property
    def supported_search_types(self) -> List[SearchType]:
        return [SearchType.DOMAIN]
    
    def run_search(self, query: str, search_type: SearchType) -> PluginResult:
        if search_type != SearchType.DOMAIN:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Unsupported search type: {search_type.value}"
            )
        
        try:
            logging.info(f"Running WHOIS lookup for: {query}")
            
            result = subprocess.run(
                ['whois', query],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return PluginResult(
                    plugin_name=self.name,
                    search_type=search_type,
                    query=query,
                    success=False,
                    error=result.stderr or "WHOIS lookup failed"
                )
            
            # Parse WHOIS output (simplified)
            whois_data = result.stdout
            
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=True,
                data={
                    'domain': query,
                    'whois_data': whois_data,
                    'length': len(whois_data)
                }
            )
            
        except subprocess.TimeoutExpired:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error="WHOIS lookup timed out"
            )
        except FileNotFoundError:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error="WHOIS command not found. Install with: apt install whois"
            )
        except Exception as e:
            logging.error(f"WHOIS error: {e}")
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
```

## Testing Your Plugin

1. **Create a test script**:

```python
from core.engine import OSINTEngine
from core.plugin_base import SearchType
from plugins.your_plugin import YourPlugin

# Initialize engine
engine = OSINTEngine()
engine.register_plugin(YourPlugin())

# Test search
result = engine.run_single_plugin(
    "YourPluginName",
    "test_query",
    SearchType.USERNAME
)

# Check results
if result.success:
    print("Success!", result.data)
else:
    print("Failed:", result.error)
```

2. **Test with the framework**:

```bash
python main.py
# Select your plugin from the menu and test
```

3. **Run automated tests**:

```bash
python test_framework.py
```

## Plugin Distribution

When your plugin is ready:

1. Document any external dependencies in `requirements.txt`
2. Add usage instructions to the README
3. Include API key setup instructions if needed
4. Test with various input types
5. Handle edge cases (empty input, invalid format, etc.)

## Need Help?

- Review existing plugins in `plugins/` directory
- Check the `core/plugin_base.py` for the base class definition
- Run `python example_usage.py` to see the framework in action
- Look at test examples in `test_framework.py`
