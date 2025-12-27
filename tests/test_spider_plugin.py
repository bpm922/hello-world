"""
Tests for Spider Plugin
"""

import pytest
from plugins.spider_plugin import SpiderPlugin
from plugins.base_plugin import PluginResult


def test_spider_plugin_initialization():
    """Test that Spider plugin initializes correctly"""
    plugin = SpiderPlugin()
    assert plugin.name == "spider"
    assert len(plugin.description) > 0
    assert "crawling" in plugin.description.lower() or "web" in plugin.description.lower()


def test_spider_plugin_search_types():
    """Test that Spider plugin has correct search types"""
    plugin = SpiderPlugin()
    assert "url" in plugin.search_types
    assert "domain" in plugin.search_types


def test_spider_plugin_normalize_url():
    """Test URL normalization"""
    plugin = SpiderPlugin()
    
    # Test without protocol
    assert plugin._normalize_url("example.com", "url") == "https://example.com"
    
    # Test with protocol
    assert plugin._normalize_url("http://example.com", "url") == "http://example.com"


def test_spider_plugin_search():
    """Test Spider plugin search"""
    plugin = SpiderPlugin()
    result = plugin.search("example.com", search_type="url", max_pages=2)
    
    assert isinstance(result, PluginResult)
    assert result.source == "spider"
    assert result.query == "example.com"
    assert result.search_type == "url"


@pytest.mark.integration
def test_spider_plugin_search_integration():
    """Integration test for Spider plugin (requires network)"""
    plugin = SpiderPlugin()
    result = plugin.search("example.com", search_type="url", max_pages=2)
    
    assert isinstance(result, PluginResult)
    assert result.source == "spider"
    # Result may or may not succeed depending on network


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
