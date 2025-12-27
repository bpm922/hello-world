"""
Tests for Whois Plugin
"""

import pytest
from plugins.whois_plugin import WhoisPlugin
from plugins.base_plugin import PluginResult


def test_whois_plugin_initialization():
    """Test that Whois plugin initializes correctly"""
    plugin = WhoisPlugin()
    assert plugin.name == "whois"
    assert len(plugin.description) > 0
    assert "domain" in plugin.description.lower() or "dns" in plugin.description.lower()


def test_whois_plugin_search_types():
    """Test that Whois plugin has correct search types"""
    plugin = WhoisPlugin()
    assert "domain" in plugin.search_types
    assert "ip" in plugin.search_types


def test_whois_plugin_search_domain():
    """Test Whois plugin domain search"""
    plugin = WhoisPlugin()
    result = plugin.search("example.com", search_type="domain")
    
    assert isinstance(result, PluginResult)
    assert result.source == "whois"
    assert result.query == "example.com"
    assert result.search_type == "domain"


def test_whois_plugin_search_ip():
    """Test Whois plugin IP search"""
    plugin = WhoisPlugin()
    result = plugin.search("8.8.8.8", search_type="ip")
    
    assert isinstance(result, PluginResult)
    assert result.source == "whois"
    assert result.query == "8.8.8.8"
    assert result.search_type == "ip"


def test_whois_plugin_search_invalid_ip():
    """Test Whois plugin with invalid IP"""
    plugin = WhoisPlugin()
    result = plugin.search("not.an.ip.address", search_type="ip")
    
    assert isinstance(result, PluginResult)
    assert not result.success
    assert "Invalid IP" in result.error_message


@pytest.mark.integration
def test_whois_plugin_search_integration():
    """Integration test for Whois plugin (requires network)"""
    plugin = WhoisPlugin()
    result = plugin.search("example.com", search_type="domain")
    
    assert isinstance(result, PluginResult)
    assert result.source == "whois"
    # Result may or may not succeed depending on network


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
