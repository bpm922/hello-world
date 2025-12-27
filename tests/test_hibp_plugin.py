"""
Tests for HIBP Plugin
"""

import pytest
from plugins.hibp_plugin import HIBPPlugin
from plugins.base_plugin import PluginResult


def test_hibp_plugin_initialization():
    """Test that HIBP plugin initializes correctly"""
    plugin = HIBPPlugin()
    assert plugin.name == "hibp"
    assert len(plugin.description) > 0
    assert "breach" in plugin.description.lower() or "pwned" in plugin.description.lower()


def test_hibp_plugin_search_types():
    """Test that HIBP plugin has correct search types"""
    plugin = HIBPPlugin()
    assert "email" in plugin.search_types
    assert "username" in plugin.search_types


def test_hibp_plugin_search():
    """Test HIBP plugin search"""
    plugin = HIBPPlugin()
    # Use a test email that likely won't have breaches
    result = plugin.search("nonexistent12345@example.com", search_type="email")
    
    assert isinstance(result, PluginResult)
    assert result.source == "hibp"
    assert result.query == "nonexistent12345@example.com"
    assert result.search_type == "email"


@pytest.mark.integration
def test_hibp_plugin_search_integration():
    """Integration test for HIBP plugin (requires network)"""
    plugin = HIBPPlugin()
    result = plugin.search("test@example.com", search_type="email")
    
    assert isinstance(result, PluginResult)
    assert result.source == "hibp"
    # Result may or may not succeed depending on network


def test_hibp_plugin_check_password():
    """Test password checking functionality"""
    plugin = HIBPPlugin()
    
    # Test with a weak common password (likely found in breaches)
    result = plugin.check_password("password123")
    
    assert isinstance(result, dict)
    assert "found" in result
    assert "message" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
