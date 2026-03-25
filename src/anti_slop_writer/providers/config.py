"""Provider configuration models.

This module defines the configuration for connecting to LLM providers.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderConfig(BaseModel):
    """Configuration for connecting to an LLM service.

    Attributes:
        endpoint: API base URL (e.g., "https://api.openai.com/v1").
        api_key: API key (from env or config file).
        model: Model identifier (default: "gpt-4o-mini").
        max_retries: Max retry attempts (default: 3, range: 0-5).
        timeout: Request timeout in seconds (default: 60.0, range: 1-300).

    Security:
        api_key is never logged or serialized in repr/str.
    """

    endpoint: str
    api_key: str = Field(repr=False)  # Never include in repr
    model: str = "gpt-4o-mini"
    max_retries: int = Field(default=3, ge=0, le=5)
    timeout: float = Field(default=60.0, ge=1.0, le=300.0)

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        """Validate that endpoint is a valid HTTPS URL."""
        if not v.startswith("https://"):
            raise ValueError("Endpoint must be a valid HTTPS URL")
        return v.rstrip("/")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate that api_key is non-empty."""
        if not v or not v.strip():
            raise ValueError("API key cannot be empty")
        return v


class Settings(BaseSettings):
    """Application settings loaded from environment variables and config files.

    Configuration hierarchy (priority high to low):
    1. Environment variables (ANTI_SLOP_WRITER_*)
    2. Config file (~/.config/anti-slop-writer/config.toml)
    3. Built-in defaults

    Environment Variables:
        ANTI_SLOP_WRITER_API_KEY: API key for LLM provider
        ANTI_SLOP_WRITER_ENDPOINT: Override default endpoint
        ANTI_SLOP_WRITER_MODEL: Override default model
    """

    model_config = SettingsConfigDict(
        env_prefix="ANTI_SLOP_WRITER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: str | None = Field(default=None, repr=False)
    endpoint: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    max_retries: int = Field(default=3, ge=0, le=5)
    timeout: float = Field(default=60.0, ge=1.0, le=300.0)
    default_style: str = "neutral"

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        """Validate that endpoint is a valid HTTPS URL."""
        if not v.startswith("https://"):
            raise ValueError("Endpoint must be a valid HTTPS URL")
        return v.rstrip("/")

    def to_provider_config(self) -> ProviderConfig:
        """Convert settings to ProviderConfig.

        Raises:
            ValueError: If api_key is not configured.
        """
        if not self.api_key:
            raise ValueError(
                "API key not found. Set ANTI_SLOP_WRITER_API_KEY "
                "or configure in config.toml"
            )
        return ProviderConfig(
            endpoint=self.endpoint,
            api_key=self.api_key,
            model=self.model,
            max_retries=self.max_retries,
            timeout=self.timeout,
        )
