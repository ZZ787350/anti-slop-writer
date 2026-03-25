"""Configuration management for anti-slop-writer.

This module provides functions for loading configuration from
environment variables and config files.
"""

from __future__ import annotations

import logging
import tomllib
from pathlib import Path
from typing import Any

from anti_slop_writer.providers.config import ProviderConfig, Settings

logger = logging.getLogger(__name__)

# Default config file locations
DEFAULT_CONFIG_PATHS = [
    Path.home() / ".config" / "anti-slop-writer" / "config.toml",
    Path.cwd() / "anti-slop-writer.toml",
    Path.cwd() / ".anti-slop-writer.toml",
]


def load_config_file(path: Path | None = None) -> dict[str, Any]:
    """Load configuration from a TOML file.

    Args:
        path: Path to config file. If None, searches default locations.

    Returns:
        Dictionary of configuration values.
    """
    if path is not None:
        if not path.exists():
            logger.debug("Config file not found: %s", path)
            return {}
        return _read_toml_file(path)

    # Search default locations
    for config_path in DEFAULT_CONFIG_PATHS:
        if config_path.exists():
            logger.debug("Loading config from: %s", config_path)
            return _read_toml_file(config_path)

    logger.debug("No config file found in default locations")
    return {}


def _read_toml_file(path: Path) -> dict[str, Any]:
    """Read a TOML file and return its contents.

    Args:
        path: Path to the TOML file.

    Returns:
        Dictionary of configuration values.
    """
    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
            # Flatten nested structure for Settings
            result: dict[str, Any] = {}
            if "provider" in data:
                result.update(data["provider"])
            if "rewrite" in data:
                result["default_style"] = data["rewrite"].get("style", "neutral")
                if "max_retries" in data["rewrite"]:
                    result["max_retries"] = data["rewrite"]["max_retries"]
                if "timeout" in data["rewrite"]:
                    result["timeout"] = data["rewrite"]["timeout"]
            return result
    except Exception as e:
        logger.warning("Failed to read config file %s: %s", path, e)
        return {}


def get_settings(config_path: Path | None = None) -> Settings:
    """Get application settings merged from config file and environment.

    Configuration hierarchy (priority high to low):
    1. Environment variables (ANTI_SLOP_WRITER_*)
    2. Config file
    3. Built-in defaults

    Args:
        config_path: Optional path to config file.

    Returns:
        Settings instance.
    """
    # Load from config file first
    file_config = load_config_file(config_path)

    # Create settings (env vars override file config)
    return Settings(**file_config)


def get_provider_config(config_path: Path | None = None) -> ProviderConfig:
    """Get provider configuration.

    This is a convenience function that loads settings and converts
    them to a ProviderConfig instance.

    Args:
        config_path: Optional path to config file.

    Returns:
        ProviderConfig instance.

    Raises:
        ValueError: If API key is not configured.
    """
    settings = get_settings(config_path)
    return settings.to_provider_config()
