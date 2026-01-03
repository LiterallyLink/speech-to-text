"""Plugin discovery and loading"""

import importlib
import sys
from pathlib import Path
from typing import List, Dict

from .plugin_interface import PluginInterface, TextProcessorPlugin, CommandPlugin
from ..utils.logger import setup_logger


class PluginLoader:
    """Loads and manages plugins"""

    def __init__(self, search_paths: List[str]):
        """
        Initialize plugin loader

        Args:
            search_paths: List of directories to search for plugins
        """
        self.logger = setup_logger(__name__)
        self.search_paths = [Path(p).expanduser() for p in search_paths]

        self.loaded_plugins: Dict[str, PluginInterface] = {}

    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in search paths

        Returns:
            List of plugin names
        """
        plugins = []

        for search_path in self.search_paths:
            if not search_path.exists():
                continue

            for file_path in search_path.glob("*.py"):
                if file_path.stem.startswith("_"):
                    continue
                plugins.append(file_path.stem)

        return plugins

    def load_plugin(self, plugin_name: str, app_context: Any = None):
        """
        Load a plugin by name

        Args:
            plugin_name: Name of the plugin to load
            app_context: Application context to pass to plugin
        """
        # Find the plugin file
        plugin_file = None
        for search_path in self.search_paths:
            candidate = search_path / f"{plugin_name}.py"
            if candidate.exists():
                plugin_file = candidate
                break

        if not plugin_file:
            raise FileNotFoundError(f"Plugin '{plugin_name}' not found")

        # Add to sys.path if needed
        plugin_dir = str(plugin_file.parent)
        if plugin_dir not in sys.path:
            sys.path.insert(0, plugin_dir)

        try:
            # Import the module
            module = importlib.import_module(plugin_name)

            # Find the plugin class
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, PluginInterface) and
                    attr not in [PluginInterface, TextProcessorPlugin, CommandPlugin]):
                    plugin_class = attr
                    break

            if not plugin_class:
                raise ValueError(f"No plugin class found in {plugin_name}")

            # Instantiate and initialize
            plugin = plugin_class()
            plugin.initialize(app_context)

            self.loaded_plugins[plugin_name] = plugin
            self.logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")

        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            raise

    def unload_plugin(self, plugin_name: str):
        """
        Unload a plugin

        Args:
            plugin_name: Name of plugin to unload
        """
        if plugin_name in self.loaded_plugins:
            plugin = self.loaded_plugins[plugin_name]
            plugin.shutdown()
            del self.loaded_plugins[plugin_name]
            self.logger.info(f"Unloaded plugin: {plugin.name}")

    def unload_all(self):
        """Unload all plugins"""
        for plugin_name in list(self.loaded_plugins.keys()):
            self.unload_plugin(plugin_name)

    def get_text_processors(self) -> List[TextProcessorPlugin]:
        """
        Get all loaded text processor plugins

        Returns:
            List of text processor plugins
        """
        return [p for p in self.loaded_plugins.values()
                if isinstance(p, TextProcessorPlugin)]

    def get_command_plugins(self) -> List[CommandPlugin]:
        """
        Get all loaded command plugins

        Returns:
            List of command plugins
        """
        return [p for p in self.loaded_plugins.values()
                if isinstance(p, CommandPlugin)]
