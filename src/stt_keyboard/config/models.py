"""Configuration data models using Pydantic"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ApplicationConfig(BaseModel):
    """Application-level configuration"""
    auto_start: bool = False
    minimize_to_tray: bool = True
    show_notifications: bool = True


class AudioConfig(BaseModel):
    """Audio capture configuration"""
    device_id: Optional[int] = None
    sample_rate: int = 16000
    buffer_size: int = 8000


class SpeechConfig(BaseModel):
    """Speech recognition configuration"""
    model_path: str = "models/vosk-model-small-en-us-0.15"
    language: str = "en-US"
    confidence_threshold: float = 0.5


class KeyboardConfig(BaseModel):
    """Keyboard simulation configuration"""
    typing_speed: float = 0.05
    auto_punctuation: bool = True


class HotkeyConfig(BaseModel):
    """Hotkey configuration"""
    toggle_recording: str = "ctrl+shift+space"
    cancel_recording: Optional[str] = "escape"
    mode: str = "push_to_talk"  # push_to_talk, toggle, continuous


class PluginConfig(BaseModel):
    """Plugin system configuration"""
    enabled: List[str] = Field(default_factory=list)
    search_paths: List[str] = Field(
        default_factory=lambda: ["~/.stt-keyboard/plugins", "./plugins"]
    )


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    file: Optional[str] = "~/.stt-keyboard/logs/app.log"
    max_size: str = "10MB"
    backup_count: int = 5


class Config(BaseModel):
    """Main configuration model"""
    application: ApplicationConfig = Field(default_factory=ApplicationConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    speech: SpeechConfig = Field(default_factory=SpeechConfig)
    keyboard: KeyboardConfig = Field(default_factory=KeyboardConfig)
    hotkeys: HotkeyConfig = Field(default_factory=HotkeyConfig)
    plugins: PluginConfig = Field(default_factory=PluginConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
