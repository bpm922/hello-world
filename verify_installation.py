#!/usr/bin/env python3
"""
Installation verification script for OSINT Framework.
Checks all components are properly installed and configured.
"""

import sys
import os
from pathlib import Path


def check_mark(passed: bool) -> str:
    return "✓" if passed else "✗"


def check_directory_structure():
    """Verify all required directories exist"""
    print("\n[1/7] Checking directory structure...")
    
    required_dirs = [
        'config',
        'core',
        'plugins',
        'ui',
        'results',
        'logs'
    ]
    
    all_good = True
    for dir_name in required_dirs:
        exists = Path(dir_name).is_dir()
        print(f"  {check_mark(exists)} {dir_name}/")
        all_good = all_good and exists
    
    return all_good


def check_core_files():
    """Verify all core Python files exist"""
    print("\n[2/7] Checking core files...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        '.gitignore',
        'config/__init__.py',
        'config/settings.py',
        'core/__init__.py',
        'core/plugin_base.py',
        'core/engine.py',
        'core/result_handler.py',
        'core/exporter.py',
        'plugins/__init__.py',
        'plugins/sherlock_plugin.py',
        'ui/__init__.py',
        'ui/menu.py',
        'ui/display.py'
    ]
    
    all_good = True
    for file_path in required_files:
        exists = Path(file_path).is_file()
        print(f"  {check_mark(exists)} {file_path}")
        all_good = all_good and exists
    
    return all_good


def check_imports():
    """Verify all Python imports work"""
    print("\n[3/7] Checking Python imports...")
    
    imports = [
        ('core.plugin_base', 'PluginBase, SearchType, PluginResult'),
        ('core.engine', 'OSINTEngine'),
        ('core.result_handler', 'ResultAggregator'),
        ('core.exporter', 'Exporter'),
        ('config.settings', 'get_settings'),
        ('plugins', 'discover_plugins'),
        ('ui.menu', 'MenuSystem'),
        ('ui.display', 'console')
    ]
    
    all_good = True
    for module, items in imports:
        try:
            exec(f"from {module} import {items}")
            print(f"  ✓ {module}")
        except Exception as e:
            print(f"  ✗ {module} - Error: {e}")
            all_good = False
    
    return all_good


def check_dependencies():
    """Verify all required packages are installed"""
    print("\n[4/7] Checking dependencies...")
    
    dependencies = [
        'inquirer',
        'rich',
        'requests',
        'bs4',  # beautifulsoup4
        'dotenv'  # python-dotenv
    ]
    
    # Check if sherlock command is available
    import shutil
    sherlock_installed = shutil.which('sherlock') is not None
    
    all_good = True
    for package in dependencies:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - Not installed")
            all_good = False
    
    # Check Sherlock separately
    if sherlock_installed:
        print(f"  ✓ sherlock-project (command-line tool)")
    else:
        print(f"  ⚠ sherlock-project - Not found (optional)")
    
    return all_good


def check_plugin_discovery():
    """Verify plugins can be discovered"""
    print("\n[5/7] Checking plugin discovery...")
    
    try:
        from plugins import discover_plugins
        plugins = discover_plugins()
        
        if plugins:
            print(f"  ✓ Discovered {len(plugins)} plugin(s):")
            for plugin in plugins:
                print(f"    - {plugin.name}: {plugin.description}")
            return True
        else:
            print("  ✗ No plugins discovered")
            return False
    except Exception as e:
        print(f"  ✗ Error discovering plugins: {e}")
        return False


def check_configuration():
    """Verify configuration system works"""
    print("\n[6/7] Checking configuration system...")
    
    try:
        from config.settings import get_settings
        settings = get_settings()
        
        timeout = settings.get_setting("search", "timeout")
        if timeout:
            print(f"  ✓ Configuration loaded (timeout: {timeout}s)")
            
            creds_file = Path('config/credentials.json')
            if creds_file.exists():
                print(f"  ✓ Credentials file exists")
            else:
                print(f"  ⚠ Credentials file not found (will be created on first run)")
            
            return True
        else:
            print("  ✗ Failed to load configuration")
            return False
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False


def check_export_system():
    """Verify export system works"""
    print("\n[7/7] Checking export system...")
    
    try:
        from core.result_handler import ResultAggregator
        from core.plugin_base import PluginResult, SearchType
        from core.exporter import Exporter
        
        # Create test result
        aggregator = ResultAggregator()
        aggregator.start_search(1)
        
        result = PluginResult(
            plugin_name="TestPlugin",
            search_type=SearchType.USERNAME,
            query="test",
            success=True,
            data={"test": "verification"}
        )
        
        aggregator.add_result(result)
        aggregator.end_search()
        
        # Test export
        exporter = Exporter(aggregator)
        
        test_formats = []
        try:
            json_path = exporter.export_json(query="verification_test")
            if json_path.exists():
                test_formats.append("JSON")
                json_path.unlink()  # Clean up
        except:
            pass
        
        if test_formats:
            print(f"  ✓ Export system working ({', '.join(test_formats)})")
            return True
        else:
            print("  ✗ Export system failed")
            return False
            
    except Exception as e:
        print(f"  ✗ Export error: {e}")
        return False


def main():
    print("=" * 60)
    print("OSINT Framework - Installation Verification")
    print("=" * 60)
    
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Core Files", check_core_files),
        ("Python Imports", check_imports),
        ("Dependencies", check_dependencies),
        ("Plugin Discovery", check_plugin_discovery),
        ("Configuration", check_configuration),
        ("Export System", check_export_system)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  ✗ {name} check crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ Installation verification successful!")
        print("\nYou can now run:")
        print("  python main.py          # Interactive menu")
        print("  python example_usage.py # Usage examples")
        print("  python test_framework.py # Run tests")
        return 0
    else:
        print(f"\n✗ {total - passed} check(s) failed!")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
