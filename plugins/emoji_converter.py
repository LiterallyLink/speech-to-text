"""Emoji converter plugin"""

from typing import Dict, Any

from ..plugin_interface import TextProcessorPlugin


class EmojiConverterPlugin(TextProcessorPlugin):
    """Converts phrases like 'smiley face' to emoji"""

    name = "Emoji Converter"
    version = "1.0.0"
    description = "Convert text phrases to emoji"
    author = "STT Keyboard Team"

    def initialize(self, app_context):
        """Initialize the plugin"""
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

    def shutdown(self):
        """Cleanup resources"""
        pass

    def process_text(self, text: str, context: Dict[str, Any]) -> str:
        """Replace emoji phrases with actual emoji"""
        result = text

        for phrase, emoji in self.emoji_map.items():
            # Case-insensitive replacement
            result = result.replace(phrase, emoji)
            result = result.replace(phrase.title(), emoji)

        return result
