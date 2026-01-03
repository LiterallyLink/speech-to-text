"""Auto-punctuation plugin"""

from typing import Dict, Any
import re

from ..plugin_interface import TextProcessorPlugin


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
        """Initialize the plugin"""
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

    def shutdown(self):
        """Cleanup resources"""
        pass

    def process_text(self, text: str, context: Dict[str, Any]) -> str:
        """Replace spoken punctuation with symbols"""
        processed = text.lower()

        # Replace punctuation markers
        for marker, symbol in self.markers.items():
            # Match whole words only
            pattern = r'\b' + re.escape(marker) + r'\b'
            processed = re.sub(pattern, symbol, processed, flags=re.IGNORECASE)

        # Capitalize sentences
        processed = self._capitalize_sentences(processed)

        # Remove space before punctuation
        processed = re.sub(r'\s+([.,!?;:])', r'\1', processed)

        # Add space after punctuation if missing
        processed = re.sub(r'([.,!?;:])([^\s])', r'\1 \2', processed)

        return processed

    def _capitalize_sentences(self, text: str) -> str:
        """Capitalize first letter of sentences"""
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()

        # Split by sentence endings and capitalize
        sentences = re.split(r'([.!?]\s+)', text)

        result = []
        for i, part in enumerate(sentences):
            if i % 2 == 0 and part:  # Sentence content
                if part and part[0].islower():
                    part = part[0].upper() + part[1:] if len(part) > 1 else part.upper()
            result.append(part)

        return ''.join(result)
