"""Utility modules for STT Keyboard application"""

from .logger import setup_logger
from .platform_utils import get_platform, Platform

__all__ = ['setup_logger', 'get_platform', 'Platform']
