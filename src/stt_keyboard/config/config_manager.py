"""Configuration file management"""

import yaml
from pathlib import Path
from typing import Optional

from .models import Config
from ..utils.platform_utils import get_config_dir
from ..utils.logger import setup_logger


class ConfigManager:
    """Manages loading and saving configuration"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config manager

        Args:
            config_path: Optional custom config file path
        """
        self.logger = setup_logger(__name__)

        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = get_config_dir() / "config.yaml"

    def load_config(self) -> Config:
        """
        Load configuration from file

        Returns:
            Configuration object
        """
        if not self.config_path.exists():
            self.logger.info(f"Config file not found at {self.config_path}, using defaults")
            config = self.get_default_config()
            self.save_config(config)
            return config

        try:
            with open(self.config_path, 'r') as f:
                data = yaml.safe_load(f)

            if data is None:
                data = {}

            config = Config(**data)
            self.logger.info(f"Configuration loaded from {self.config_path}")
            return config

        except Exception as e:
            self.logger.error(f"Error loading config: {e}, using defaults")
            return self.get_default_config()

    def save_config(self, config: Config):
        """
        Save configuration to file

        Args:
            config: Configuration object to save
        """
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to dict and save
            with open(self.config_path, 'w') as f:
                yaml.dump(config.model_dump(), f, default_flow_style=False, sort_keys=False)

            self.logger.info(f"Configuration saved to {self.config_path}")

        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    def get_default_config(self) -> Config:
        """
        Get default configuration

        Returns:
            Default configuration object
        """
        return Config()

    def validate_config(self, config: Config) -> bool:
        """
        Validate configuration

        Args:
            config: Configuration to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Pydantic handles validation
            Config(**config.model_dump())
            return True
        except Exception as e:
            self.logger.error(f"Config validation error: {e}")
            return False
