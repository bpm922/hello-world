"""
Tests for Photon Plugin
"""

import pytest
from plugins.photon_plugin import PhotonPlugin
from plugins.base_plugin import PluginResult


def test_photon_plugin_initialization():
    """Test that Photon plugin initializes correctly"""
    plugin = PhotonPlugin()
    assert plugin.name == "photon"
    assert len(plugin.description) > 0
    assert "website" in plugin.description.lower()


def test_photon_plugin_search_types():
    """Test that Photon plugin has correct search types"""
    plugin = PhotonPlugin()
    assert "url" in plugin.search_types
    assert "domain" in plugin.search_types


def test_photon_plugin_normalize_url():
    """Test URL normalization"""
    plugin = PhotonPlugin()
    
    # Test without protocol
    assert plugin._normalize_url("example.com", "url") == "https://example.com"
    assert plugin._normalize_url("example.com", "domain") == "https://example.com"
    
    # Test with protocol
    assert plugin._normalize_url("http://example.com", "url") == "http://example.com"
    assert plugin._normalize_url("https://example.com", "url") == "https://example.com"


def test_photon_plugin_search_with_invalid_url():
    """Test Photon plugin with invalid URL"""
    plugin = PhotonPlugin()
    result = plugin.search("thisisnotavalidurl!!#$", search_type="url")
    
    assert isinstance(result, PluginResult)
    assert result.source == "photon"
    assert result.query == "thisisnotavalidurl!!#$"


@pytest.mark.integration
def test_photon_plugin_search_integration():
    """Integration test for Photon plugin (requires network)"""
    plugin = PhotonPlugin()
    
    # This test will try to crawl a real website
    # Mark as integration test since it requires network access
    result = plugin.search("example.com", search_type="url", max_pages=2)
    
    assert isinstance(result, PluginResult)
    assert result.source == "photon"
    assert result.query == "example.com"
    # Result may or may not succeed depending on network


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
