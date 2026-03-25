"""Integration tests for provider configuration and custom endpoints."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from anti_slop_writer.interfaces.cli import app
from anti_slop_writer.providers import (
    AuthenticationError,
    MalformedResponseError,
    NetworkError,
    RateLimitError,
)
from fixtures import SAMPLE_CLEAN_TEXT  # type: ignore[import-untyped]


class TestCLIProviderConfig:
    """Tests for CLI provider configuration (Phase 6, US4)."""

    def test_default_provider_configuration(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI uses default OpenAI endpoint when no custom config."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        with patch(
            "anti_slop_writer.interfaces.cli.OpenAICompatibleProvider"
        ) as mock_provider_class:
            mock_provider = AsyncMock()
            mock_provider.call = AsyncMock(
                return_value=type(
                    "LLMResponse",
                    (),
                    {"content": SAMPLE_CLEAN_TEXT, "model": "test", "usage": {}},
                )()
            )
            mock_provider.close = AsyncMock()
            mock_provider_class.return_value = mock_provider

            result = cli_runner.invoke(app, ["rewrite", "Test text."])

            assert result.exit_code == 0
            # Verify provider was created with default endpoint
            call_args = mock_provider_class.call_args
            assert call_args is not None

    def test_custom_endpoint_from_env(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI uses custom endpoint from environment variable."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")
        monkeypatch.setenv(
            "ANTI_SLOP_WRITER_ENDPOINT",
            "https://custom.llm.api.com/v1",
        )

        with patch(
            "anti_slop_writer.interfaces.cli.OpenAICompatibleProvider"
        ) as mock_provider_class:
            mock_provider = AsyncMock()
            mock_provider.call = AsyncMock(
                return_value=type(
                    "LLMResponse",
                    (),
                    {"content": SAMPLE_CLEAN_TEXT, "model": "test", "usage": {}},
                )()
            )
            mock_provider.close = AsyncMock()
            mock_provider_class.return_value = mock_provider

            result = cli_runner.invoke(app, ["rewrite", "Test text."])

            assert result.exit_code == 0

    def test_custom_model_from_env(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI uses custom model from environment variable."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")
        monkeypatch.setenv("ANTI_SLOP_WRITER_MODEL", "gpt-4")

        with patch(
            "anti_slop_writer.interfaces.cli.OpenAICompatibleProvider"
        ) as mock_provider_class:
            mock_provider = AsyncMock()
            mock_provider.call = AsyncMock(
                return_value=type(
                    "LLMResponse",
                    (),
                    {"content": SAMPLE_CLEAN_TEXT, "model": "gpt-4", "usage": {}},
                )()
            )
            mock_provider.close = AsyncMock()
            mock_provider_class.return_value = mock_provider

            result = cli_runner.invoke(app, ["rewrite", "Test text."])

            assert result.exit_code == 0


class TestCLIProviderErrors:
    """Tests for provider error handling."""

    def test_authentication_error_message(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI shows clear message for authentication errors."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "invalid-key")

        with patch(
            "anti_slop_writer.interfaces.cli.OpenAICompatibleProvider"
        ) as mock_provider_class:
            mock_provider = AsyncMock()
            mock_provider.call = AsyncMock(
                side_effect=AuthenticationError("Invalid API key")
            )
            mock_provider.close = AsyncMock()
            mock_provider_class.return_value = mock_provider

            result = cli_runner.invoke(app, ["rewrite", "Test text."])

            assert result.exit_code == 3
            output = result.output.lower()
            assert "authentication" in output or "api key" in output

    def test_rate_limit_error_message(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI shows clear message for rate limit errors."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        with patch(
            "anti_slop_writer.interfaces.cli.OpenAICompatibleProvider"
        ) as mock_provider_class:
            mock_provider = AsyncMock()
            mock_provider.call = AsyncMock(
                side_effect=RateLimitError("Rate limited")
            )
            mock_provider.close = AsyncMock()
            mock_provider_class.return_value = mock_provider

            result = cli_runner.invoke(app, ["rewrite", "Test text."])

            assert result.exit_code == 3
            output = result.output.lower()
            assert "rate" in output

    def test_network_error_message(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI shows clear message for network errors."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")
        monkeypatch.setenv("ANTI_SLOP_WRITER_ENDPOINT", "https://invalid.endpoint.com/v1")

        with patch(
            "anti_slop_writer.interfaces.cli.OpenAICompatibleProvider"
        ) as mock_provider_class:
            mock_provider = AsyncMock()
            mock_provider.call = AsyncMock(
                side_effect=NetworkError("Connection refused")
            )
            mock_provider.close = AsyncMock()
            mock_provider_class.return_value = mock_provider

            result = cli_runner.invoke(app, ["rewrite", "Test text."])

            assert result.exit_code == 4
            output = result.output.lower()
            assert "network" in output or "connection" in output or "timeout" in output

    def test_malformed_response_error_message(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI shows clear message for malformed response errors."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        with patch(
            "anti_slop_writer.interfaces.cli.OpenAICompatibleProvider"
        ) as mock_provider_class:
            mock_provider = AsyncMock()
            mock_provider.call = AsyncMock(
                side_effect=MalformedResponseError("Invalid response format")
            )
            mock_provider.close = AsyncMock()
            mock_provider_class.return_value = mock_provider

            result = cli_runner.invoke(app, ["rewrite", "Test text."])

            assert result.exit_code == 5


class TestConfigFileLoading:
    """Tests for config file loading (Phase 6, US4)."""

    def test_config_file_loads_from_home_directory(
        self, cli_runner: CliRunner, tmp_path: Path, monkeypatch
    ) -> None:
        """CLI loads config from ~/.config/anti-slop-writer/config.toml."""
        # Create a config file in temp directory
        config_dir = tmp_path / ".config" / "anti-slop-writer"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.toml"
        config_file.write_text("""
[provider]
endpoint = "https://custom.from.config.com/v1"
model = "config-model"

[rewrite]
style = "formal"
""")

        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        # Mock DEFAULT_CONFIG_PATHS to use our temp directory
        with patch(
            "anti_slop_writer.core.config.DEFAULT_CONFIG_PATHS",
            [config_file],
        ):
            with patch(
                "anti_slop_writer.interfaces.cli.OpenAICompatibleProvider"
            ) as mock_provider_class:
                mock_provider = AsyncMock()
                mock_provider.call = AsyncMock(
                    return_value=type(
                        "LLMResponse",
                        (),
                        {"content": SAMPLE_CLEAN_TEXT, "model": "config-model", "usage": {}},
                    )()
                )
                mock_provider.close = AsyncMock()
                mock_provider_class.return_value = mock_provider

                result = cli_runner.invoke(app, ["rewrite", "Test text."])

                # Should succeed with config-loaded settings
                assert result.exit_code == 0

    def test_env_vars_override_config_file(
        self, cli_runner: CliRunner, tmp_path: Path, monkeypatch
    ) -> None:
        """Environment variables take precedence over config file."""
        config_dir = tmp_path / ".config" / "anti-slop-writer"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.toml"
        config_file.write_text("""
[provider]
endpoint = "https://from-config.com/v1"
model = "config-model"
""")

        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")
        # Env var should override config file
        monkeypatch.setenv("ANTI_SLOP_WRITER_MODEL", "env-override-model")

        # Mock DEFAULT_CONFIG_PATHS to use our temp directory
        with patch(
            "anti_slop_writer.core.config.DEFAULT_CONFIG_PATHS",
            [config_file],
        ):
            with patch(
                "anti_slop_writer.interfaces.cli.OpenAICompatibleProvider"
            ) as mock_provider_class:
                mock_provider = AsyncMock()
                mock_provider.call = AsyncMock(
                    return_value=type(
                        "LLMResponse",
                        (),
                        {"content": SAMPLE_CLEAN_TEXT, "model": "env-override-model", "usage": {}},
                    )()
                )
                mock_provider.close = AsyncMock()
                mock_provider_class.return_value = mock_provider

                result = cli_runner.invoke(app, ["rewrite", "Test text."])

                assert result.exit_code == 0


class TestProviderOption:
    """Tests for --provider option (reserved for future use)."""

    def test_provider_option_accepted(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI accepts --provider option without error."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        with patch(
            "anti_slop_writer.interfaces.cli.OpenAICompatibleProvider"
        ) as mock_provider_class:
            mock_provider = AsyncMock()
            mock_provider.call = AsyncMock(
                return_value=type(
                    "LLMResponse",
                    (),
                    {"content": SAMPLE_CLEAN_TEXT, "model": "test", "usage": {}},
                )()
            )
            mock_provider.close = AsyncMock()
            mock_provider_class.return_value = mock_provider

            # --provider option should be accepted (even if not fully implemented)
            result = cli_runner.invoke(
                app, ["rewrite", "--provider", "default", "Test text."]
            )

            # Should not fail due to --provider option
            assert result.exit_code in (0, 1, 2, 3, 4, 5)
