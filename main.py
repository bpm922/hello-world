#!/usr/bin/env python3

import sys
import logging
from core.engine import OSINTEngine
from plugins import discover_plugins
from ui.menu import MenuSystem
from ui.display import print_error, print_info


def main():
    try:
        print_info("Initializing OSINT Tool...")
        
        engine = OSINTEngine()
        
        print_info("Discovering plugins...")
        plugins = discover_plugins()
        
        if not plugins:
            print_error("No plugins found! Please check your plugins directory.")
            sys.exit(1)
        
        for plugin in plugins:
            engine.register_plugin(plugin)
        
        print_info(f"Loaded {len(plugins)} plugin(s)")
        
        menu = MenuSystem(engine)
        menu.run()
        
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        print_error(f"A fatal error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
