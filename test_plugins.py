#!/usr/bin/env python3
"""
Test script for all OSINT plugins
"""

import sys
from core.engine import OSINTEngine
from core.plugin_base import SearchType
from plugins import discover_plugins
from ui.display import print_success, print_error, print_info, console


def test_plugin(engine, plugin_name, query, search_type):
    """Test a single plugin"""
    print_info(f"Testing {plugin_name} with query: '{query}'")
    
    result = engine.run_single_plugin(plugin_name, query, search_type)
    
    if result.success:
        print_success(f"{plugin_name} search successful!")
        if result.data:
            console.print(f"  Data keys: {list(result.data.keys())[:5]}...")
        return True
    else:
        print_error(f"{plugin_name} failed: {result.error}")
        return False


def main():
    print_info("Testing All OSINT Plugins")
    console.print("=" * 60)
    
    engine = OSINTEngine()
    
    plugins = discover_plugins()
    for plugin in plugins:
        engine.register_plugin(plugin)
    
    print_info(f"Loaded {len(plugins)} plugins\n")
    
    test_cases = [
        ("Phone Number Lookup", "+1-555-123-4567", SearchType.PHONE),
        ("Email Validator", "test@example.com", SearchType.EMAIL),
        ("Have I Been Pwned", "test@example.com", SearchType.EMAIL),
        ("IP Geolocation", "8.8.8.8", SearchType.IP),
        ("DNS Lookup", "google.com", SearchType.DOMAIN),
        ("WHOIS", "google.com", SearchType.DOMAIN),
        ("Sherlock", "test_user_12345", SearchType.USERNAME),
    ]
    
    results = []
    
    for plugin_name, query, search_type in test_cases:
        console.print(f"\n{'='*60}")
        success = test_plugin(engine, plugin_name, query, search_type)
        results.append((plugin_name, success))
        console.print()
    
    console.print("=" * 60)
    console.print("\n[bold cyan]Test Summary:[/bold cyan]")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for plugin_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        color = "green" if success else "red"
        console.print(f"[{color}]{status}[/{color}] {plugin_name}")
    
    console.print(f"\nResults: {passed}/{total} plugins working")
    
    if passed == total:
        print_success("\n✓ All plugins operational!")
        return 0
    else:
        print_error(f"\n✗ {total - passed} plugin(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
