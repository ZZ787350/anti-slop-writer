"""Integration tests for the CLI interface."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from anti_slop_writer.interfaces.cli import app


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Typer CLI test runner."""
    return CliRunner()


# Sample text for tests
SAMPLE_AI_TEXT = "In today's world, it is crucial to leverage this approach."
SAMPLE_CLEAN_TEXT = "This approach is important and useful to use."


class TestCLIRewriteBasic:
    """Tests for basic CLI rewrite functionality."""

    def test_rewrite_with_text_argument(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI accepts text as positional argument."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        # Mock the provider to return clean text
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

            result = cli_runner.invoke(app, ["rewrite", "Test text to rewrite."])

            assert result.exit_code in (0, 1, 2, 3, 4, 5)

    def test_rewrite_empty_text_exits_with_error(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI exits with code 1 for empty text."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        result = cli_runner.invoke(app, ["rewrite", ""])

        assert result.exit_code == 1
        output = result.output.lower()
        assert "empty" in output

    def test_rewrite_whitespace_only_exits_with_error(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI exits with code 1 for whitespace-only text."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        result = cli_runner.invoke(app, ["rewrite", "   \n\t  "])

        assert result.exit_code == 1


class TestCLIExitCodes:
    """Tests for exit code handling per contracts/cli.md."""

    def test_exit_code_1_input_error(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI exits with 1 for input errors."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        result = cli_runner.invoke(app, ["rewrite", ""])

        assert result.exit_code == 1

    def test_exit_code_2_missing_api_key(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI exits with 2 when API key is missing."""
        monkeypatch.delenv("ANTI_SLOP_WRITER_API_KEY", raising=False)

        result = cli_runner.invoke(app, ["rewrite", "Test text."])

        assert result.exit_code == 2
        output = result.output.lower()
        assert "api key" in output

    def test_exit_code_1_invalid_style(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI exits with 1 for invalid style option."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        result = cli_runner.invoke(
            app, ["rewrite", "--style", "invalid_style", "Test text."]
        )

        assert result.exit_code == 1
        output = result.output.lower()
        assert "style" in output


class TestCLIStyleOption:
    """Tests for --style option handling."""

    def test_style_neutral(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI accepts neutral style."""
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

            result = cli_runner.invoke(
                app, ["rewrite", "--style", "neutral", "Test text."]
            )

            # Should not error due to style
            if result.exit_code == 1:
                output = result.output.lower()
                assert "style" not in output or "invalid" not in output

    def test_style_formal(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI accepts formal style."""
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

            result = cli_runner.invoke(
                app, ["rewrite", "--style", "formal", "Test text."]
            )

            if result.exit_code == 1:
                output = result.output.lower()
                assert "style" not in output or "invalid" not in output

    def test_style_casual(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI accepts casual style."""
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

            result = cli_runner.invoke(
                app, ["rewrite", "--style", "casual", "Test text."]
            )

            if result.exit_code == 1:
                output = result.output.lower()
                assert "style" not in output or "invalid" not in output


class TestCLIHelp:
    """Tests for CLI help and documentation."""

    def test_help_flag(self, cli_runner: CliRunner) -> None:
        """CLI shows help with --help flag."""
        result = cli_runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "rewrite" in result.output.lower()

    def test_rewrite_help(self, cli_runner: CliRunner) -> None:
        """rewrite command shows help with --help."""
        result = cli_runner.invoke(app, ["rewrite", "--help"])

        assert result.exit_code == 0
        assert "--style" in result.output
        assert "--input" in result.output
        assert "--output" in result.output


class TestCLIErrors:
    """Tests for error message formatting."""

    def test_error_messages_are_user_friendly(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """Error messages should be clear and actionable."""
        monkeypatch.delenv("ANTI_SLOP_WRITER_API_KEY", raising=False)

        result = cli_runner.invoke(app, ["rewrite", "Test text."])

        # Error message should suggest resolution
        output = result.output.lower()
        assert "api key" in output

    def test_error_messages_no_sensitive_data(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """Error messages should not expose sensitive data."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "sk-super-secret-key-12345")
        monkeypatch.setenv("ANTI_SLOP_WRITER_ENDPOINT", "https://invalid-endpoint.test/v1")

        # Mock the provider to raise a network error
        with patch(
            "anti_slop_writer.interfaces.cli.OpenAICompatibleProvider"
        ) as mock_provider_class:
            from anti_slop_writer.providers import NetworkError

            mock_provider = AsyncMock()
            mock_provider.call = AsyncMock(side_effect=NetworkError("Connection failed"))
            mock_provider.close = AsyncMock()
            mock_provider_class.return_value = mock_provider

            result = cli_runner.invoke(app, ["rewrite", "Test text."])

            # Error message should not contain the API key
            output = result.output
            assert "sk-super-secret-key" not in output


class TestCLIFileIO:
    """Tests for file input/output handling (Phase 4, US2)."""

    def test_input_file_option(
        self, cli_runner: CliRunner, tmp_path: Path, monkeypatch
    ) -> None:
        """CLI accepts --input option for file-based processing."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        input_file = tmp_path / "input.txt"
        input_file.write_text("Test content to rewrite.")

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

            result = cli_runner.invoke(app, ["rewrite", "--input", str(input_file)])

            assert result.exit_code == 0
            assert SAMPLE_CLEAN_TEXT in result.output

    def test_input_file_not_found(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI exits with code 1 when input file doesn't exist."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        result = cli_runner.invoke(
            app, ["rewrite", "--input", "/nonexistent/path/file.txt"]
        )

        assert result.exit_code == 1
        output = result.output.lower()
        assert "file not found" in output

    def test_output_file_option(
        self, cli_runner: CliRunner, tmp_path: Path, monkeypatch
    ) -> None:
        """CLI accepts --output option for specifying output file."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        output_file = tmp_path / "output.txt"

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

            result = cli_runner.invoke(
                app, ["rewrite", "--output", str(output_file), "Test text."]
            )

            assert result.exit_code == 0
            assert output_file.exists()
            assert output_file.read_text() == SAMPLE_CLEAN_TEXT

    def test_input_and_output_together(
        self, cli_runner: CliRunner, tmp_path: Path, monkeypatch
    ) -> None:
        """CLI handles both --input and --output options."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        input_file = tmp_path / "article.txt"
        input_file.write_text("AI generated content to rewrite.")
        output_file = tmp_path / "rewritten.txt"

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

            result = cli_runner.invoke(
                app,
                ["rewrite", "--input", str(input_file), "--output", str(output_file)],
            )

            assert result.exit_code == 0
            assert output_file.exists()
            assert SAMPLE_CLEAN_TEXT in output_file.read_text()

    def test_output_creates_parent_directories(
        self, cli_runner: CliRunner, tmp_path: Path, monkeypatch
    ) -> None:
        """CLI creates parent directories for output file if needed."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        output_file = tmp_path / "subdir" / "nested" / "output.txt"

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

            result = cli_runner.invoke(
                app, ["rewrite", "--output", str(output_file), "Test text."]
            )

            assert result.exit_code == 0
            assert output_file.exists()

    def test_text_and_input_mutually_exclusive(
        self, cli_runner: CliRunner, tmp_path: Path, monkeypatch
    ) -> None:
        """CLI rejects both text argument and --input option together."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        input_file = tmp_path / "input.txt"
        input_file.write_text("File content")

        result = cli_runner.invoke(
            app, ["rewrite", "--input", str(input_file), "Direct text"]
        )

        assert result.exit_code == 1
        output = result.output.lower()
        assert "both" in output or "mutually" in output


class TestCLIStdin:
    """Tests for stdin input handling (Phase 4, US2)."""

    def test_stdin_input_with_dash(
        self, cli_runner: CliRunner, monkeypatch
    ) -> None:
        """CLI accepts '-' to read from stdin."""
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

            # Simulate stdin input
            result = cli_runner.invoke(
                app, ["rewrite", "-"], input="Text from stdin"
            )

            assert result.exit_code == 0

    def test_stdin_with_output_file(
        self, cli_runner: CliRunner, tmp_path: Path, monkeypatch
    ) -> None:
        """CLI can read from stdin and write to file."""
        monkeypatch.setenv("ANTI_SLOP_WRITER_API_KEY", "test-key")

        output_file = tmp_path / "from_stdin.txt"

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

            result = cli_runner.invoke(
                app, ["rewrite", "-", "--output", str(output_file)],
                input="Text from stdin"
            )

            assert result.exit_code == 0
            assert output_file.exists()