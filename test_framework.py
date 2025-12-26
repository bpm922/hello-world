#!/usr/bin/env python3

import sys
from core.engine import OSINTEngine
from core.plugin_base import SearchType
from core.exporter import Exporter
from plugins import discover_plugins
from ui.display import print_success, print_error, print_info


def test_plugin_discovery():
    print_info("Testing plugin discovery...")
    plugins = discover_plugins()
    
    if not plugins:
        print_error("No plugins discovered!")
        return False
    
    print_success(f"Discovered {len(plugins)} plugin(s)")
    for plugin in plugins:
        print(f"  - {plugin.name}: {plugin.description}")
    
    return True


def test_engine_initialization():
    print_info("Testing engine initialization...")
    
    engine = OSINTEngine()
    plugins = discover_plugins()
    
    for plugin in plugins:
        engine.register_plugin(plugin)
    
    registered = engine.get_all_plugins()
    
    if len(registered) != len(plugins):
        print_error("Plugin registration failed!")
        return False
    
    print_success(f"Engine initialized with {len(registered)} plugin(s)")
    return True


def test_result_aggregation():
    print_info("Testing result aggregation...")
    
    from core.result_handler import ResultAggregator
    from core.plugin_base import PluginResult
    
    aggregator = ResultAggregator()
    aggregator.start_search(2)
    
    result1 = PluginResult(
        plugin_name="TestPlugin1",
        search_type=SearchType.USERNAME,
        query="testuser",
        success=True,
        data={"found": True, "profiles": ["site1", "site2"]}
    )
    
    result2 = PluginResult(
        plugin_name="TestPlugin2",
        search_type=SearchType.USERNAME,
        query="testuser",
        success=False,
        error="Test error"
    )
    
    aggregator.add_result(result1)
    aggregator.add_result(result2)
    aggregator.end_search()
    
    if len(aggregator.results) != 2:
        print_error("Result aggregation failed!")
        return False
    
    if aggregator.search_metadata["successful_plugins"] != 1:
        print_error("Success count incorrect!")
        return False
    
    if aggregator.search_metadata["failed_plugins"] != 1:
        print_error("Failed count incorrect!")
        return False
    
    print_success("Result aggregation working correctly")
    return True


def test_export_system():
    print_info("Testing export system...")
    
    from core.result_handler import ResultAggregator
    from core.plugin_base import PluginResult
    import os
    
    aggregator = ResultAggregator()
    aggregator.start_search(1)
    
    result = PluginResult(
        plugin_name="TestPlugin",
        search_type=SearchType.USERNAME,
        query="testuser",
        success=True,
        data={"test": "data"}
    )
    
    aggregator.add_result(result)
    aggregator.end_search()
    
    exporter = Exporter(aggregator)
    
    try:
        json_path = exporter.export_json(query="test")
        html_path = exporter.export_html(query="test")
        csv_path = exporter.export_csv(query="test")
        sqlite_path = exporter.export_sqlite(query="test")
        
        if not all([
            os.path.exists(json_path),
            os.path.exists(html_path),
            os.path.exists(csv_path),
            os.path.exists(sqlite_path)
        ]):
            print_error("Export files not created!")
            return False
        
        print_success("All export formats working correctly")
        print(f"  - JSON: {json_path}")
        print(f"  - HTML: {html_path}")
        print(f"  - CSV: {csv_path}")
        print(f"  - SQLite: {sqlite_path}")
        
        return True
    except Exception as e:
        print_error(f"Export failed: {e}")
        return False


def test_configuration():
    print_info("Testing configuration system...")
    
    from config.settings import get_settings
    
    settings = get_settings()
    
    timeout = settings.get_setting("search", "timeout")
    if timeout is None:
        print_error("Failed to read settings!")
        return False
    
    print_success(f"Configuration system working (timeout: {timeout}s)")
    return True


def main():
    print_info("Starting OSINT Framework Tests\n")
    
    tests = [
        ("Plugin Discovery", test_plugin_discovery),
        ("Engine Initialization", test_engine_initialization),
        ("Result Aggregation", test_result_aggregation),
        ("Export System", test_export_system),
        ("Configuration", test_configuration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_error(f"Test crashed: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print("Test Summary")
    print('='*60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print_success("\n✓ All tests passed!")
        return 0
    else:
        print_error(f"\n✗ {failed} test(s) failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
