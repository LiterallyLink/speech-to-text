"""Platform-specific utilities"""

import platform
from enum import Enum
from pathlib import Path


class Platform(Enum):
    """Supported platforms"""
    WINDOWS = "Windows"
    MACOS = "Darwin"
    LINUX = "Linux"
    UNKNOWN = "Unknown"


def get_platform() -> Platform:
    """
    Get the current platform

    Returns:
        Platform enum value
    """
    system = platform.system()

    if system == "Windows":
        return Platform.WINDOWS
    elif system == "Darwin":
        return Platform.MACOS
    elif system == "Linux":
        return Platform.LINUX
    else:
        return Platform.UNKNOWN


def get_config_dir() -> Path:
    """
    Get the platform-specific configuration directory

    Returns:
        Path to config directory
    """
    home = Path.home()
    current_platform = get_platform()

    if current_platform == Platform.WINDOWS:
        return home / ".stt-keyboard"
    elif current_platform == Platform.MACOS:
        return home / ".stt-keyboard"
    elif current_platform == Platform.LINUX:
        return home / ".stt-keyboard"
    else:
        return Path(".stt-keyboard")


def get_log_dir() -> Path:
    """Get the log directory"""
    return get_config_dir() / "logs"


def get_models_dir() -> Path:
    """Get the models directory"""
    return Path("models")
