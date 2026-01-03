# Plugin Development Guide

## Overview

The STT Keyboard application supports a plugin system that allows extending functionality without modifying core code. Plugins can process transcribed text, execute voice commands, or add custom behaviors.

## Plugin Types

### 1. Text Processor Plugins
Transform transcribed text before it's typed into applications.

**Use cases**:
- Auto-punctuation
- Text formatting
- Spell correction
- Custom abbreviations
- Language-specific processing

### 2. Command Plugins
Execute actions based on voice commands instead of typing text.

**Use cases**:
- Application control ("open browser", "close window")
- System commands ("take screenshot", "adjust volume")
- Custom automation workflows
- Clipboard operations

## Plugin Interface

All plugins must implement the `PluginInterface` base class:

```python
# src/stt_keyboard/plugins/plugin_interface.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


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
    def initialize(self, app_context: 'ApplicationContext') -> None:
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
```

## Plugin Template

Save as `my_plugin.py` in the plugins directory:

```python
from stt_keyboard.plugins import TextProcessorPlugin
# or: from stt_keyboard.plugins import CommandPlugin
from typing import Dict, Any


class MyPlugin(TextProcessorPlugin):
    """
    [Plugin description here]
    
    Example: Converts certain phrases to emoji
    """
    
    # Required metadata
    name = "My Plugin"
    version = "1.0.0"
    description = "What this plugin does"
    author = "Your Name"
    
    def initialize(self, app_context):
        """Initialize plugin resources"""
        self.logger = app_context.logger
        self.config = app_context.config
        
        # Load any plugin-specific configuration
        self.enabled = True
        
        self.logger.info(f"{self.name} v{self.version} initialized")
    
    def shutdown(self):
        """Cleanup resources"""
        self.logger.info(f"{self.name} shutting down")
    
    def process_text(self, text: str, context: Dict[str, Any]) -> str:
        """Process the transcribed text"""
        if not self.enabled:
            return text
            
        # Your processing logic here
        processed = text
        
        return processed
```

## Example Plugins

### 1. Auto-Punctuation Plugin

```python
# plugins/builtin/auto_punctuation.py

from stt_keyboard.plugins import TextProcessorPlugin
from typing import Dict, Any
import re


class AutoPunctuationPlugin(TextProcessorPlugin):
    """
    Automatically converts spoken punctuation markers to symbols
    and capitalizes appropriately.
    """
    
    name = "Auto Punctuation"
    version = "1.0.0"
    description = "Converts spoken punctuation to symbols"
    author = "STT Keyboard Team"
    
    def initialize(self, app_context):
        self.logger = app_context.logger
        
        # Punctuation markers
        self.markers = {
            "period": ".",
            "comma": ",",
            "question mark": "?",
            "exclamation point": "!",
            "exclamation mark": "!",
            "colon": ":",
            "semicolon": ";",
            "dash": "-",
            "hyphen": "-",
            "apostrophe": "'",
            "quote": '"',
            "open quote": '"',
            "close quote": '"',
            "open parenthesis": "(",
            "close parenthesis": ")",
            "new line": "\n",
            "new paragraph": "\n\n"
        }
        
        self.logger.info(f"{self.name} initialized")
    
    def shutdown(self):
        pass
    
    def process_text(self, text: str, context: Dict[str, Any]) -> str:
        """Replace spoken punctuation with symbols"""
        processed = text.lower()
        
        # Replace punctuation markers
        for marker, symbol in self.markers.items():
            # Match whole words only
            pattern = r'\b' + re.escape(marker) + r'\b'
            processed = re.sub(pattern, symbol, processed)
        
        # Capitalize sentences
        processed = self._capitalize_sentences(processed)
        
        # Remove space before punctuation
        processed = re.sub(r'\s+([.,!?;:])', r'\1', processed)
        
        # Add space after punctuation if missing
        processed = re.sub(r'([.,!?;:])([^\s])', r'\1 \2', processed)
        
        return processed
    
    def _capitalize_sentences(self, text: str) -> str:
        """Capitalize first letter of sentences"""
        # Split by sentence endings
        sentences = re.split(r'([.!?]\s+)', text)
        
        # Capitalize first letter of each sentence
        result = []
        for i, part in enumerate(sentences):
            if i % 2 == 0 and part:  # Sentence content
                part = part[0].upper() + part[1:] if len(part) > 0 else part
            result.append(part)
        
        return ''.join(result)
```

### 2. Emoji Converter Plugin

```python
# plugins/builtin/emoji_converter.py

from stt_keyboard.plugins import TextProcessorPlugin
from typing import Dict, Any


class EmojiConverterPlugin(TextProcessorPlugin):
    """Converts phrases like 'smiley face' to emoji"""
    
    name = "Emoji Converter"
    version = "1.0.0"
    description = "Convert text phrases to emoji"
    author = "STT Keyboard Team"
    
    def initialize(self, app_context):
        self.logger = app_context.logger
        
        # Emoji mappings
        self.emoji_map = {
            "smiley face": "😊",
            "happy face": "😊",
            "sad face": "😢",
            "crying face": "😭",
            "laughing face": "😂",
            "heart": "❤️",
            "thumbs up": "👍",
            "thumbs down": "👎",
            "fire": "🔥",
            "star": "⭐",
            "check mark": "✓",
            "warning": "⚠️",
            "rocket": "🚀",
            "party popper": "🎉"
        }
        
        self.logger.info(f"{self.name} initialized with {len(self.emoji_map)} emojis")
    
    def shutdown(self):
        pass
    
    def process_text(self, text: str, context: Dict[str, Any]) -> str:
        """Replace emoji phrases with actual emoji"""
        result = text
        
        for phrase, emoji in self.emoji_map.items():
            # Case-insensitive replacement
            result = result.replace(phrase, emoji)
            result = result.replace(phrase.title(), emoji)
            
        return result
```

### 3. Code Formatting Plugin

```python
# plugins/builtin/code_formatter.py

from stt_keyboard.plugins import TextProcessorPlugin
from typing import Dict, Any
import re


class CodeFormatterPlugin(TextProcessorPlugin):
    """
    Formats code-related speech into proper code syntax.
    Example: "function hello world" -> "function helloWorld()"
    """
    
    name = "Code Formatter"
    version = "1.0.0"
    description = "Format spoken code into proper syntax"
    author = "STT Keyboard Team"
    
    def initialize(self, app_context):
        self.logger = app_context.logger
        self.enabled = False  # Disabled by default, enable in code editors
        
        # Code patterns
        self.patterns = {
            r"function\s+(\w+(?:\s+\w+)*)": self._format_function,
            r"variable\s+(\w+(?:\s+\w+)*)": self._format_variable,
            r"class\s+(\w+(?:\s+\w+)*)": self._format_class,
        }
        
    def shutdown(self):
        pass
    
    def process_text(self, text: str, context: Dict[str, Any]) -> str:
        """Format code patterns"""
        if not self.enabled:
            return text
        
        # Check if we're in a code editor (from context)
        app_name = context.get('app_name', '').lower()
        code_editors = ['vscode', 'sublime', 'atom', 'pycharm', 'vim', 'emacs']
        
        if not any(editor in app_name for editor in code_editors):
            return text
        
        result = text
        
        # Apply code patterns
        for pattern, formatter in self.patterns.items():
            result = re.sub(pattern, formatter, result)
        
        return result
    
    def _format_function(self, match):
        """Format function declaration"""
        name = match.group(1).replace(' ', '_').lower()
        return f"function {name}()"
    
    def _format_variable(self, match):
        """Format variable declaration"""
        name = match.group(1).replace(' ', '_').lower()
        return f"let {name}"
    
    def _format_class(self, match):
        """Format class name to CamelCase"""
        words = match.group(1).split()
        name = ''.join(word.capitalize() for word in words)
        return f"class {name}"
```

### 4. System Command Plugin

```python
# plugins/builtin/system_commands.py

from stt_keyboard.plugins import CommandPlugin
from typing import Dict, Any
import subprocess
import platform


class SystemCommandPlugin(CommandPlugin):
    """Execute system commands via voice"""
    
    name = "System Commands"
    version = "1.0.0"
    description = "Execute basic system commands"
    author = "STT Keyboard Team"
    
    def initialize(self, app_context):
        self.logger = app_context.logger
        self.system = platform.system()
        
        # Define available commands
        self.commands = {
            "open browser": self._open_browser,
            "take screenshot": self._take_screenshot,
            "lock screen": self._lock_screen,
            "increase volume": lambda: self._adjust_volume(10),
            "decrease volume": lambda: self._adjust_volume(-10),
        }
        
        self.logger.info(f"{self.name} initialized for {self.system}")
    
    def shutdown(self):
        pass
    
    def match_command(self, text: str) -> bool:
        """Check if text is a system command"""
        text_lower = text.lower().strip()
        return any(cmd in text_lower for cmd in self.commands.keys())
    
    def execute_command(self, text: str, context: Dict[str, Any]) -> bool:
        """Execute the system command"""
        text_lower = text.lower().strip()
        
        for cmd_phrase, cmd_func in self.commands.items():
            if cmd_phrase in text_lower:
                try:
                    cmd_func()
                    self.logger.info(f"Executed: {cmd_phrase}")
                    return True
                except Exception as e:
                    self.logger.error(f"Failed to execute {cmd_phrase}: {e}")
                    return False
        
        return False
    
    def _open_browser(self):
        """Open default web browser"""
        if self.system == "Windows":
            subprocess.run(["start", "https://google.com"], shell=True)
        elif self.system == "Darwin":  # macOS
            subprocess.run(["open", "https://google.com"])
        else:  # Linux
            subprocess.run(["xdg-open", "https://google.com"])
    
    def _take_screenshot(self):
        """Take a screenshot"""
        if self.system == "Windows":
            subprocess.run(["snippingtool", "/clip"])
        elif self.system == "Darwin":
            subprocess.run(["screencapture", "-i", "-c"])
        else:
            subprocess.run(["gnome-screenshot", "-i"])
    
    def _lock_screen(self):
        """Lock the screen"""
        if self.system == "Windows":
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        elif self.system == "Darwin":
            subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
        else:
            subprocess.run(["gnome-screensaver-command", "-l"])
    
    def _adjust_volume(self, delta: int):
        """Adjust system volume"""
        # [Unverified] Platform-specific implementation needed
        self.logger.warning("Volume adjustment not implemented for this platform")
```

## Plugin Configuration

Plugins can have their own configuration in the main config file:

```yaml
# config.yaml
plugins:
  enabled:
    - "auto_punctuation"
    - "emoji_converter"
    - "system_commands"
  
  search_paths:
    - "~/.stt-keyboard/plugins"
    - "./plugins"
  
  # Plugin-specific settings
  auto_punctuation:
    enabled: true
    capitalize_sentences: true
    
  emoji_converter:
    enabled: true
    
  code_formatter:
    enabled: false
    auto_detect_editor: true
```

## Plugin Discovery

The plugin loader searches for plugins in configured directories:

```python
# src/stt_keyboard/plugins/plugin_loader.py

import importlib
import sys
from pathlib import Path
from typing import List, Dict

from .plugin_interface import PluginInterface, TextProcessorPlugin, CommandPlugin
from ..utils.logger import setup_logger


class PluginLoader:
    """Loads and manages plugins"""
    
    def __init__(self, search_paths: List[str]):
        self.logger = setup_logger(__name__)
        self.search_paths = [Path(p).expanduser() for p in search_paths]
        
        self.loaded_plugins: Dict[str, PluginInterface] = {}
        
    def discover_plugins(self) -> List[str]:
        """Discover available plugins in search paths"""
        plugins = []
        
        for search_path in self.search_paths:
            if not search_path.exists():
                continue
                
            for file_path in search_path.glob("*.py"):
                if file_path.stem.startswith("_"):
                    continue
                plugins.append(file_path.stem)
        
        return plugins
    
    def load_plugin(self, plugin_name: str):
        """Load a plugin by name"""
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
        
        # Import the module
        module = importlib.import_module(plugin_name)
        
        # Find the plugin class
        plugin_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, PluginInterface) and 
                attr != PluginInterface):
                plugin_class = attr
                break
        
        if not plugin_class:
            raise ValueError(f"No plugin class found in {plugin_name}")
        
        # Instantiate and initialize
        plugin = plugin_class()
        plugin.initialize(None)  # Pass app context in real implementation
        
        self.loaded_plugins[plugin_name] = plugin
        self.logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
    
    def unload_plugin(self, plugin_name: str):
        """Unload a plugin"""
        if plugin_name in self.loaded_plugins:
            plugin = self.loaded_plugins[plugin_name]
            plugin.shutdown()
            del self.loaded_plugins[plugin_name]
            self.logger.info(f"Unloaded plugin: {plugin.name}")
    
    def get_text_processors(self) -> List[TextProcessorPlugin]:
        """Get all loaded text processor plugins"""
        return [p for p in self.loaded_plugins.values() 
                if isinstance(p, TextProcessorPlugin)]
    
    def get_command_plugins(self) -> List[CommandPlugin]:
        """Get all loaded command plugins"""
        return [p for p in self.loaded_plugins.values() 
                if isinstance(p, CommandPlugin)]
```

## Testing Your Plugin

```python
# tests/test_my_plugin.py

import pytest
from plugins.my_plugin import MyPlugin


def test_plugin_metadata():
    """Test plugin metadata"""
    plugin = MyPlugin()
    assert plugin.name == "My Plugin"
    assert plugin.version == "1.0.0"
    

def test_plugin_initialization():
    """Test plugin initialization"""
    plugin = MyPlugin()
    
    # Mock app context
    class MockContext:
        logger = None
        config = None
    
    plugin.initialize(MockContext())
    plugin.shutdown()


def test_text_processing():
    """Test text processing"""
    plugin = MyPlugin()
    plugin.initialize(MockContext())
    
    result = plugin.process_text("test input", {})
    assert result  # Add specific assertions
    
    plugin.shutdown()
```

## Distribution

Share your plugin with the community:

1. Create a repository
2. Add clear README with usage instructions
3. Include example configuration
4. Submit to plugin directory (if exists)

## Best Practices

1. **Error Handling**: Always handle exceptions gracefully
2. **Logging**: Use the provided logger for debugging
3. **Performance**: Keep processing fast (< 100ms)
4. **Testing**: Include unit tests
5. **Documentation**: Document what your plugin does
6. **Configuration**: Make behavior configurable when possible
7. **Compatibility**: Test on multiple platforms if possible

This guide provides everything needed to create powerful plugins for the STT Keyboard application.
