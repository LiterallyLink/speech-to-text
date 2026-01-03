"""Plugin system for STT Keyboard"""

from .plugin_interface import PluginInterface, TextProcessorPlugin, CommandPlugin
from .plugin_loader import PluginLoader

__all__ = [
    'PluginInterface',
    'TextProcessorPlugin',
    'CommandPlugin',
    'PluginLoader',
]
