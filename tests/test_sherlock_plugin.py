"""
Tests for Sherlock Plugin
"""

import pytest
from plugins.sherlock_plugin import SherlockPlugin
from plugins.base_plugin import PluginResult


def test_sherlock_plugin_initialization():
    """Test that Sherlock plugin initializes correctly"""
    plugin = SherlockPlugin()
    assert plugin.name == "sherlock"
    assert len(plugin.description) > 0
    assert "username" in plugin.description.lower() or "social" in plugin.description.lower()


def test_sherlock_plugin_search_types():
    """Test that Sherlock plugin has correct search types"""
    plugin = SherlockPlugin()
    assert "username" in plugin.search_types


def test_sherlock_plugin_search():
    """Test Sherlock plugin search"""
    plugin = SherlockPlugin()
    result = plugin.search("testusername123", search_type="username")
    
    assert isinstance(result, PluginResult)
    assert result.source == "sherlock"
    assert result.query == "testusername123"
    assert result.search_type == "username"


@pytest.mark.integration
def test_sherlock_plugin_search_integration():
    """Integration test for Sherlock plugin (requires network and sherlock package)"""
    plugin = SherlockPlugin()
    result = plugin.search("testusername123", search_type="username")
    
    assert isinstance(result, PluginResult)
    assert result.source == "sherlock"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
