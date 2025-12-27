"""
Tests for Shodan Plugin
"""

import pytest
from plugins.shodan_plugin import ShodanPlugin
from plugins.base_plugin import PluginResult


def test_shodan_plugin_initialization():
    """Test that Shodan plugin initializes correctly"""
    plugin = ShodanPlugin()
    assert plugin.name == "shodan"
    assert len(plugin.description) > 0
    assert "ip" in plugin.description.lower() or "intelligence" in plugin.description.lower()


def test_shodan_plugin_search_types():
    """Test that Shodan plugin has correct search types"""
    plugin = ShodanPlugin()
    assert "ip" in plugin.search_types
    assert "domain" in plugin.search_types
    assert "net" in plugin.search_types


def test_shodan_plugin_search_without_api_key():
    """Test Shodan plugin without API key"""
    plugin = ShodanPlugin()
    result = plugin.search("8.8.8.8", search_type="ip")
    
    assert isinstance(result, PluginResult)
    assert result.source == "shodan"
    assert result.query == "8.8.8.8"
    # Should fail without API key
    assert not result.success
    assert "API key" in result.error_message


@pytest.mark.integration
def test_shodan_plugin_search_with_api_key():
    """Integration test for Shodan plugin (requires API key and network)"""
    # This test requires a valid API key
    # Set SHODAN_API_KEY environment variable to run this test
    
    import os
    api_key = os.environ.get("SHODAN_API_KEY")
    
    if not api_key:
        pytest.skip("SHODAN_API_KEY not set")
    
    plugin = ShodanPlugin({"api_key": api_key})
    result = plugin.search("8.8.8.8", search_type="ip")
    
    assert isinstance(result, PluginResult)
    assert result.source == "shodan"
    assert result.query == "8.8.8.8"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
