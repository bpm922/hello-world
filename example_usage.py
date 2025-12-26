#!/usr/bin/env python3
"""
Example usage of the OSINT Framework without interactive menu.
This demonstrates how to use the framework programmatically.
"""

import sys
from core.engine import OSINTEngine
from core.plugin_base import SearchType
from core.exporter import Exporter
from plugins import discover_plugins
from ui.display import (
    print_success, print_error, print_info, 
    display_plugins, display_results_summary, 
    display_results_detailed, display_export_results
)


def example_search_all_tools():
    """Example: Search for a username across all available tools"""
    print_info("Example 1: Search All Tools")
    print("=" * 60)
    
    engine = OSINTEngine()
    
    plugins = discover_plugins()
    for plugin in plugins:
        engine.register_plugin(plugin)
    
    print_info("Available plugins:")
    display_plugins(engine.get_all_plugins())
    
    query = "example_user"
    search_type = SearchType.USERNAME
    
    print_info(f"\nSearching for username: {query}")
    
    results = engine.run_all_plugins(query, search_type, parallel=True)
    
    display_results_summary(results)
    
    print_success("\n✓ Search completed!")
    
    return engine


def example_single_plugin():
    """Example: Search using a specific plugin"""
    print_info("\nExample 2: Single Plugin Search")
    print("=" * 60)
    
    engine = OSINTEngine()
    
    plugins = discover_plugins()
    for plugin in plugins:
        engine.register_plugin(plugin)
    
    plugin_name = "Sherlock"
    query = "test_user"
    search_type = SearchType.USERNAME
    
    print_info(f"Searching with {plugin_name} for: {query}")
    
    result = engine.run_single_plugin(plugin_name, query, search_type)
    
    engine.result_aggregator.start_search(1)
    engine.result_aggregator.add_result(result)
    engine.result_aggregator.end_search()
    
    display_results_summary(engine.get_results())
    
    return engine


def example_export_results():
    """Example: Export results to multiple formats"""
    print_info("\nExample 3: Export Results")
    print("=" * 60)
    
    engine = OSINTEngine()
    
    plugins = discover_plugins()
    for plugin in plugins:
        engine.register_plugin(plugin)
    
    query = "demo_export"
    search_type = SearchType.USERNAME
    
    results = engine.run_all_plugins(query, search_type, parallel=False)
    
    exporter = Exporter(results)
    
    print_info("Exporting results...")
    export_paths = exporter.export_all(query=query)
    
    display_export_results(export_paths)
    
    return export_paths


def example_plugin_management():
    """Example: Enable/disable plugins"""
    print_info("\nExample 4: Plugin Management")
    print("=" * 60)
    
    engine = OSINTEngine()
    
    plugins = discover_plugins()
    for plugin in plugins:
        engine.register_plugin(plugin)
    
    print_info("All plugins:")
    for plugin in engine.get_all_plugins():
        status = "Enabled" if plugin.enabled else "Disabled"
        print(f"  - {plugin.name}: {status}")
    
    if engine.get_all_plugins():
        first_plugin = engine.get_all_plugins()[0]
        print_info(f"\nDisabling {first_plugin.name}...")
        first_plugin.disable()
        
        print_info("Enabled plugins after disable:")
        for plugin in engine.get_enabled_plugins():
            print(f"  - {plugin.name}")
        
        print_info(f"\nRe-enabling {first_plugin.name}...")
        first_plugin.enable()
        
        print_info("Enabled plugins after re-enable:")
        for plugin in engine.get_enabled_plugins():
            print(f"  - {plugin.name}")
    
    print_success("\n✓ Plugin management completed!")


def example_search_type_filtering():
    """Example: Get plugins by search type"""
    print_info("\nExample 5: Search Type Filtering")
    print("=" * 60)
    
    engine = OSINTEngine()
    
    plugins = discover_plugins()
    for plugin in plugins:
        engine.register_plugin(plugin)
    
    for search_type in SearchType:
        compatible_plugins = engine.get_plugins_by_search_type(search_type)
        if compatible_plugins:
            print_info(f"\nPlugins supporting {search_type.value}:")
            for plugin in compatible_plugins:
                print(f"  - {plugin.name}")
        else:
            print(f"\nNo plugins support {search_type.value}")
    
    print_success("\n✓ Search type filtering completed!")


def main():
    print("\n")
    print("=" * 60)
    print(" OSINT Framework - Usage Examples")
    print("=" * 60)
    print("\n")
    
    try:
        example_search_all_tools()
        
        example_single_plugin()
        
        example_export_results()
        
        example_plugin_management()
        
        example_search_type_filtering()
        
        print("\n")
        print("=" * 60)
        print_success("All examples completed successfully!")
        print("=" * 60)
        print("\n")
        
        print_info("To run the interactive menu:")
        print("  python main.py")
        print("\n")
        
    except Exception as e:
        print_error(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
