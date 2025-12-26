import inquirer
from typing import Optional, List
from core.engine import OSINTEngine
from core.plugin_base import SearchType
from core.exporter import Exporter
from ui.display import (
    console, print_banner, print_success, print_error, 
    print_warning, print_info, display_plugins,
    display_results_summary, display_results_detailed,
    display_export_results, clear_screen
)
import logging


class MenuSystem:
    def __init__(self, engine: OSINTEngine):
        self.engine = engine
        self.running = True

    def run(self):
        while self.running:
            clear_screen()
            print_banner()
            self._main_menu()

    def _main_menu(self):
        choices = [
            "Search All Tools",
            "Select Individual Tool",
            "View Available Tools",
            "Configuration",
            "Exit"
        ]
        
        questions = [
            inquirer.List(
                'action',
                message="Select an option",
                choices=choices,
            ),
        ]
        
        try:
            answers = inquirer.prompt(questions)
            if not answers:
                self.running = False
                return
            
            action = answers['action']
            
            if action == "Search All Tools":
                self._search_all_menu()
            elif action == "Select Individual Tool":
                self._select_tool_menu()
            elif action == "View Available Tools":
                self._view_tools_menu()
            elif action == "Configuration":
                self._config_menu()
            elif action == "Exit":
                self._exit()
        except (KeyboardInterrupt, EOFError):
            self._exit()

    def _search_all_menu(self):
        clear_screen()
        print_info("Search Across All Tools")
        console.print("\n")
        
        search_type = self._select_search_type()
        if not search_type:
            return
        
        query = self._get_search_query()
        if not query:
            return
        
        self._execute_search_all(query, search_type)

    def _select_tool_menu(self):
        plugins = self.engine.get_enabled_plugins()
        
        if not plugins:
            print_error("No plugins available")
            console.input("\nPress Enter to continue...")
            return
        
        clear_screen()
        print_info("Select a Tool")
        console.print("\n")
        
        plugin_choices = [f"{p.name} - {p.description}" for p in plugins]
        plugin_choices.append("Back")
        
        questions = [
            inquirer.List(
                'plugin',
                message="Select a plugin",
                choices=plugin_choices,
            ),
        ]
        
        try:
            answers = inquirer.prompt(questions)
            if not answers or answers['plugin'] == "Back":
                return
            
            plugin_name = answers['plugin'].split(" - ")[0]
            self._single_tool_search(plugin_name)
        except (KeyboardInterrupt, EOFError):
            return

    def _single_tool_search(self, plugin_name: str):
        plugin = self.engine.get_plugin(plugin_name)
        
        if not plugin:
            print_error(f"Plugin '{plugin_name}' not found")
            console.input("\nPress Enter to continue...")
            return
        
        clear_screen()
        print_info(f"Search with {plugin.name}")
        console.print(f"[cyan]{plugin.description}[/cyan]\n")
        
        search_type = self._select_search_type(plugin.supported_search_types)
        if not search_type:
            return
        
        query = self._get_search_query()
        if not query:
            return
        
        self._execute_single_search(plugin_name, query, search_type)

    def _view_tools_menu(self):
        clear_screen()
        plugins = self.engine.get_all_plugins()
        display_plugins(plugins)
        console.input("\n[cyan]Press Enter to continue...[/cyan]")

    def _config_menu(self):
        clear_screen()
        print_info("Configuration Menu")
        console.print("\n")
        
        choices = [
            "View Settings",
            "Toggle Plugin",
            "Back"
        ]
        
        questions = [
            inquirer.List(
                'action',
                message="Select an option",
                choices=choices,
            ),
        ]
        
        try:
            answers = inquirer.prompt(questions)
            if not answers or answers['action'] == "Back":
                return
            
            if answers['action'] == "View Settings":
                self._view_settings()
            elif answers['action'] == "Toggle Plugin":
                self._toggle_plugin()
        except (KeyboardInterrupt, EOFError):
            return

    def _view_settings(self):
        clear_screen()
        print_info("Current Settings")
        console.print("\n")
        
        settings = self.engine.settings._settings
        console.print(settings)
        
        console.input("\n[cyan]Press Enter to continue...[/cyan]")

    def _toggle_plugin(self):
        plugins = self.engine.get_all_plugins()
        
        if not plugins:
            print_error("No plugins available")
            console.input("\nPress Enter to continue...")
            return
        
        plugin_choices = [
            f"{p.name} - {'[Enabled]' if p.enabled else '[Disabled]'}"
            for p in plugins
        ]
        
        questions = [
            inquirer.List(
                'plugin',
                message="Select a plugin to toggle",
                choices=plugin_choices,
            ),
        ]
        
        try:
            answers = inquirer.prompt(questions)
            if not answers:
                return
            
            plugin_name = answers['plugin'].split(" - ")[0]
            plugin = self.engine.get_plugin(plugin_name)
            
            if plugin:
                if plugin.enabled:
                    plugin.disable()
                    print_success(f"Disabled {plugin_name}")
                else:
                    plugin.enable()
                    print_success(f"Enabled {plugin_name}")
                
                console.input("\nPress Enter to continue...")
        except (KeyboardInterrupt, EOFError):
            return

    def _select_search_type(self, supported_types: Optional[List[SearchType]] = None) -> Optional[SearchType]:
        if supported_types is None:
            search_types = list(SearchType)
        else:
            search_types = supported_types
        
        choices = [st.value for st in search_types]
        choices.append("Cancel")
        
        questions = [
            inquirer.List(
                'search_type',
                message="Select search type",
                choices=choices,
            ),
        ]
        
        try:
            answers = inquirer.prompt(questions)
            if not answers or answers['search_type'] == "Cancel":
                return None
            
            return SearchType(answers['search_type'])
        except (KeyboardInterrupt, EOFError):
            return None

    def _get_search_query(self) -> Optional[str]:
        questions = [
            inquirer.Text(
                'query',
                message="Enter search query",
            ),
        ]
        
        try:
            answers = inquirer.prompt(questions)
            if not answers or not answers['query']:
                return None
            return answers['query'].strip()
        except (KeyboardInterrupt, EOFError):
            return None

    def _execute_search_all(self, query: str, search_type: SearchType):
        clear_screen()
        print_info(f"Searching for '{query}' across all tools...")
        console.print("\n")
        
        with console.status("[bold green]Running searches..."):
            self.engine.run_all_plugins(query, search_type, parallel=True)
        
        results = self.engine.get_results()
        
        display_results_summary(results)
        display_results_detailed(results)
        
        self._export_menu(results, query)

    def _execute_single_search(self, plugin_name: str, query: str, search_type: SearchType):
        clear_screen()
        print_info(f"Searching with {plugin_name} for '{query}'...")
        console.print("\n")
        
        with console.status("[bold green]Running search..."):
            result = self.engine.run_single_plugin(plugin_name, query, search_type)
        
        self.engine.result_aggregator.start_search(1)
        self.engine.result_aggregator.add_result(result)
        self.engine.result_aggregator.end_search()
        
        results = self.engine.get_results()
        
        display_results_summary(results)
        display_results_detailed(results)
        
        self._export_menu(results, query)

    def _export_menu(self, results, query: str):
        choices = [
            "Export as JSON",
            "Export as HTML",
            "Export as CSV",
            "Export as SQLite",
            "Export All Formats",
            "Skip Export"
        ]
        
        questions = [
            inquirer.List(
                'export',
                message="Export results?",
                choices=choices,
            ),
        ]
        
        try:
            answers = inquirer.prompt(questions)
            if not answers or answers['export'] == "Skip Export":
                console.input("\n[cyan]Press Enter to continue...[/cyan]")
                return
            
            exporter = Exporter(results)
            export_choice = answers['export']
            
            with console.status("[bold green]Exporting..."):
                if export_choice == "Export as JSON":
                    path = exporter.export_json(query=query)
                    display_export_results({'json': path})
                elif export_choice == "Export as HTML":
                    path = exporter.export_html(query=query)
                    display_export_results({'html': path})
                elif export_choice == "Export as CSV":
                    path = exporter.export_csv(query=query)
                    display_export_results({'csv': path})
                elif export_choice == "Export as SQLite":
                    path = exporter.export_sqlite(query=query)
                    display_export_results({'sqlite': path})
                elif export_choice == "Export All Formats":
                    paths = exporter.export_all(query=query)
                    display_export_results(paths)
            
            console.input("\n[cyan]Press Enter to continue...[/cyan]")
        except (KeyboardInterrupt, EOFError):
            console.input("\n[cyan]Press Enter to continue...[/cyan]")
        except Exception as e:
            print_error(f"Export failed: {e}")
            console.input("\n[cyan]Press Enter to continue...[/cyan]")

    def _exit(self):
        clear_screen()
        print_success("Thank you for using OSINT Tool!")
        self.running = False
