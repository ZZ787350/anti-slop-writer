"""Shared test fixtures and utilities.

This module contains fixtures, sample data, and utility classes
that are used across multiple test files.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from anti_slop_writer.providers.base import BaseProvider, LLMResponse
from anti_slop_writer.providers.config import ProviderConfig

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# Sample texts
# ---------------------------------------------------------------------------

SAMPLE_AI_TEXT = (
    "In today's fast-paced world, it is crucial to leverage cutting-edge "
    "solutions. This groundbreaking approach will seamlessly transform the "
    "paradigm and foster innovation across the ecosystem."
)

SAMPLE_CLEAN_TEXT = (
    "The new approach saves time and works well in practice. "
    "It removes steps that caused delays and makes the process simpler."
)


# ---------------------------------------------------------------------------
# Mock provider
# ---------------------------------------------------------------------------


class FakeProvider(BaseProvider):
    """A fake LLM provider for tests that returns a configurable response.

    This provider is used in unit tests to mock LLM API calls without
    making actual network requests.

    Attributes:
        _response_text: The text to return in the LLMResponse.
    """

    def __init__(
        self, config: ProviderConfig, response_text: str = SAMPLE_CLEAN_TEXT
    ) -> None:
        """Initialize the fake provider.

        Args:
            config: Provider configuration (not used for actual calls).
            response_text: Text to return in the response.
        """
        super().__init__(config)
        self._response_text = response_text

    async def call(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Return a mock LLM response.

        Args:
            system_prompt: System message (ignored).
            user_prompt: User message (ignored).
            temperature: Sampling temperature (ignored).
            max_tokens: Max tokens (ignored).

        Returns:
            LLMResponse with the configured response_text.
        """
        return LLMResponse(
            content=self._response_text,
            model="fake-model",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        )

    async def close(self) -> None:
        """Close the provider (no-op for fake provider)."""
        pass


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def create_temp_config_file(tmp_path: Path, content: str) -> Path:
    """Create a temporary config file with the given content.

    Args:
        tmp_path: Temporary directory path.
        content: TOML content for the config file.

    Returns:
        Path to the created config file.
    """
    config_dir = tmp_path / ".config" / "anti-slop-writer"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.toml"
    config_file.write_text(content, encoding="utf-8")
    return config_file
