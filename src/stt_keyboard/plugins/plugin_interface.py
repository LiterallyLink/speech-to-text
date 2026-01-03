"""Plugin interface definitions"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class PluginInterface(ABC):
    """Base interface for all plugins"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the plugin name"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Return the plugin version (semantic versioning)"""
        pass

    @property
    def description(self) -> str:
        """Return a description of the plugin"""
        return ""

    @property
    def author(self) -> str:
        """Return the plugin author"""
        return "Unknown"

    @abstractmethod
    def initialize(self, app_context: Any) -> None:
        """
        Called when the plugin is loaded

        Args:
            app_context: Application context with access to config, logger, etc.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Called when the plugin is unloaded or app shuts down"""
        pass


class TextProcessorPlugin(PluginInterface):
    """Plugin for processing transcribed text"""

    @abstractmethod
    def process_text(self, text: str, context: Dict[str, Any]) -> str:
        """
        Process text before it's typed

        Args:
            text: Original transcribed text
            context: Additional context information
                - 'timestamp': When text was transcribed
                - 'language': Current language model
                - 'confidence': Transcription confidence (if available)
                - 'app_name': Active application name (if detectable)

        Returns:
            Processed text to be typed
        """
        pass


class CommandPlugin(PluginInterface):
    """Plugin for executing voice commands"""

    @abstractmethod
    def match_command(self, text: str) -> bool:
        """
        Check if text matches this plugin's command pattern

        Args:
            text: Transcribed text

        Returns:
            True if this plugin can handle the command
        """
        pass

    @abstractmethod
    def execute_command(self, text: str, context: Dict[str, Any]) -> bool:
        """
        Execute the voice command

        Args:
            text: Transcribed text
            context: Additional context information

        Returns:
            True if command was handled and no text should be typed,
            False to continue processing
        """
        pass
