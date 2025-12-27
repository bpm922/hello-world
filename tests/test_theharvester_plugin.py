"""
Tests for TheHarvester Plugin
"""

import pytest
from plugins.theharvester_plugin import TheHarvesterPlugin
from plugins.base_plugin import PluginResult


def test_theharvester_plugin_initialization():
    """Test that TheHarvester plugin initializes correctly"""
    plugin = TheHarvesterPlugin()
    assert plugin.name == "theharvester"
    assert len(plugin.description) > 0
    assert "email" in plugin.description.lower()


def test_theharvester_plugin_search_types():
    """Test that TheHarvester plugin has correct search types"""
    plugin = TheHarvesterPlugin()
    assert "domain" in plugin.search_types
    assert "company" in plugin.search_types


def test_theharvester_plugin_search():
    """Test TheHarvester plugin search"""
    plugin = TheHarvesterPlugin()
    result = plugin.search("example.com", search_type="domain", sources=["bing"])
    
    assert isinstance(result, PluginResult)
    assert result.source == "theharvester"
    assert result.query == "example.com"
    assert result.search_type == "domain"


@pytest.mark.integration
def test_theharvester_plugin_search_integration():
    """Integration test for TheHarvester plugin (requires network)"""
    plugin = TheHarvesterPlugin()
    result = plugin.search("example.com", search_type="domain", sources=["bing"])
    
    assert isinstance(result, PluginResult)
    assert result.source == "theharvester"
    # Result may or may not succeed depending on network


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
