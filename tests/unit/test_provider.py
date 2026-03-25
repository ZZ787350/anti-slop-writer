"""Unit tests for Provider configuration."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from anti_slop_writer.providers.config import ProviderConfig, Settings


class TestProviderConfig:
    """Tests for ProviderConfig validation."""

    def test_valid_config(self) -> None:
        """ProviderConfig accepts valid configuration."""
        config = ProviderConfig(
            endpoint="https://api.openai.com/v1",
            api_key="sk-test-key-123",
            model="gpt-4o-mini",
        )

        assert config.endpoint == "https://api.openai.com/v1"
        assert config.api_key == "sk-test-key-123"
        assert config.model == "gpt-4o-mini"

    def test_endpoint_trailing_slash_removed(self) -> None:
        """ProviderConfig removes trailing slash from endpoint."""
        config = ProviderConfig(
            endpoint="https://api.openai.com/v1/",
            api_key="sk-test-key",
        )

        assert config.endpoint == "https://api.openai.com/v1"

    def test_endpoint_must_be_https(self) -> None:
        """ProviderConfig rejects non-HTTPS endpoints."""
        with pytest.raises(ValidationError) as exc_info:
            ProviderConfig(
                endpoint="http://api.example.com/v1",
                api_key="sk-test-key",
            )

        assert "HTTPS" in str(exc_info.value)

    def test_api_key_cannot_be_empty(self) -> None:
        """ProviderConfig rejects empty API key."""
        with pytest.raises(ValidationError) as exc_info:
            ProviderConfig(
                endpoint="https://api.openai.com/v1",
                api_key="",
            )

        assert "empty" in str(exc_info.value).lower()

    def test_api_key_cannot_be_whitespace(self) -> None:
        """ProviderConfig rejects whitespace-only API key."""
        with pytest.raises(ValidationError) as exc_info:
            ProviderConfig(
                endpoint="https://api.openai.com/v1",
                api_key="   ",
            )

        assert "empty" in str(exc_info.value).lower()

    def test_default_model(self) -> None:
        """ProviderConfig uses default model when not specified."""
        config = ProviderConfig(
            endpoint="https://api.openai.com/v1",
            api_key="sk-test-key",
        )

        assert config.model == "gpt-4o-mini"

    def test_default_max_retries(self) -> None:
        """ProviderConfig has default max_retries of 3."""
        config = ProviderConfig(
            endpoint="https://api.openai.com/v1",
            api_key="sk-test-key",
        )

        assert config.max_retries == 3

    def test_max_retries_validation_range(self) -> None:
        """ProviderConfig validates max_retries is in range 0-5."""
        # Valid values
        for retries in [0, 1, 3, 5]:
            config = ProviderConfig(
                endpoint="https://api.openai.com/v1",
                api_key="sk-test-key",
                max_retries=retries,
            )
            assert config.max_retries == retries

        # Invalid: too high
        with pytest.raises(ValidationError):
            ProviderConfig(
                endpoint="https://api.openai.com/v1",
                api_key="sk-test-key",
                max_retries=6,
            )

        # Invalid: negative
        with pytest.raises(ValidationError):
            ProviderConfig(
                endpoint="https://api.openai.com/v1",
                api_key="sk-test-key",
                max_retries=-1,
            )

    def test_default_timeout(self) -> None:
        """ProviderConfig has default timeout of 60 seconds."""
        config = ProviderConfig(
            endpoint="https://api.openai.com/v1",
            api_key="sk-test-key",
        )

        assert config.timeout == 60.0

    def test_timeout_validation_range(self) -> None:
        """ProviderConfig validates timeout is in range 1-300."""
        # Valid values
        for timeout in [1.0, 30.0, 60.0, 300.0]:
            config = ProviderConfig(
                endpoint="https://api.openai.com/v1",
                api_key="sk-test-key",
                timeout=timeout,
            )
            assert config.timeout == timeout

        # Invalid: too high
        with pytest.raises(ValidationError):
            ProviderConfig(
                endpoint="https://api.openai.com/v1",
                api_key="sk-test-key",
                timeout=301.0,
            )

        # Invalid: zero
        with pytest.raises(ValidationError):
            ProviderConfig(
                endpoint="https://api.openai.com/v1",
                api_key="sk-test-key",
                timeout=0.0,
            )

    def test_api_key_not_in_repr(self) -> None:
        """ProviderConfig does not include API key in repr."""
        config = ProviderConfig(
            endpoint="https://api.openai.com/v1",
            api_key="sk-super-secret-key-12345",
        )

        repr_str = repr(config)
        assert "sk-super-secret-key" not in repr_str


class TestSettings:
    """Tests for Settings configuration."""

    def test_settings_defaults(self) -> None:
        """Settings has sensible defaults."""
        settings = Settings()

        assert settings.endpoint == "https://api.openai.com/v1"
        assert settings.model == "gpt-4o-mini"
        assert settings.default_style == "neutral"
        assert settings.max_retries == 3
        assert settings.timeout == 60.0

    def test_settings_from_env_vars(self, monkeypatch) -> None:
        """Settings loads from environment variables."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "env-api-key")
        monkeypatch.setenv("ANTI_SLOP_WRITER_ENDPOINT", "https://custom.api.com/v1")
        monkeypatch.setenv("ANTI_SLOP_WRITER_MODEL", "gpt-4")

        settings = Settings()

        assert settings.api_key == "env-api-key"
        assert settings.endpoint == "https://custom.api.com/v1"
        assert settings.model == "gpt-4"

    def test_settings_to_provider_config(self, monkeypatch) -> None:
        """Settings can convert to ProviderConfig."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-api-key")

        settings = Settings(
            endpoint="https://api.example.com/v1",
            model="custom-model",
        )

        config = settings.to_provider_config()

        assert isinstance(config, ProviderConfig)
        assert config.endpoint == "https://api.example.com/v1"
        assert config.api_key == "test-api-key"
        assert config.model == "custom-model"

    def test_settings_to_provider_config_raises_without_api_key(self) -> None:
        """Settings.to_provider_config raises error without API key."""
        settings = Settings(api_key=None)

        with pytest.raises(ValueError) as exc_info:
            settings.to_provider_config()

        assert "API key not found" in str(exc_info.value)

    def test_settings_endpoint_validation(self) -> None:
        """Settings validates endpoint is HTTPS."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(endpoint="http://not-secure.com/v1")

        assert "HTTPS" in str(exc_info.value)


class TestProviderConfigCustomEndpoints:
    """Tests for custom endpoint configurations (US4)."""

    def test_azure_openai_endpoint(self) -> None:
        """ProviderConfig accepts Azure OpenAI endpoint format."""
        config = ProviderConfig(
            endpoint="https://my-resource.openai.azure.com/openai/deployments/gpt-4",
            api_key="azure-key",
        )

        assert "azure.com" in config.endpoint

    def test_zhipu_glm_endpoint(self) -> None:
        """ProviderConfig accepts Zhipu GLM endpoint."""
        config = ProviderConfig(
            endpoint="https://open.bigmodel.cn/api/paas/v4",
            api_key="zhipu-key",
            model="glm-4",
        )

        assert config.model == "glm-4"

    def test_custom_endpoint(self) -> None:
        """ProviderConfig accepts custom OpenAI-compatible endpoints."""
        config = ProviderConfig(
            endpoint="https://llm.example.com/v1",
            api_key="custom-key",
            model="local-model",
        )

        assert config.endpoint == "https://llm.example.com/v1"
        assert config.model == "local-model"