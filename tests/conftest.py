"""Test configuration and shared fixtures."""

from __future__ import annotations

from pathlib import Path
from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest

from anti_slop_writer.language_packs.english import EnglishPack
from anti_slop_writer.providers.base import BaseProvider, LLMResponse
from anti_slop_writer.providers.config import ProviderConfig


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
# Provider config fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def provider_config() -> ProviderConfig:
    """A valid ProviderConfig pointing at a fake endpoint."""
    return ProviderConfig(
        api_key="test-api-key-1234",
        endpoint="https://api.example.com/v1",
        model="gpt-4o-mini",
        timeout=10.0,
        max_retries=1,
    )


# ---------------------------------------------------------------------------
# Mock provider fixture
# ---------------------------------------------------------------------------


class FakeProvider(BaseProvider):
    """A fake LLM provider for tests that returns a configurable response."""

    def __init__(self, config: ProviderConfig, response_text: str = SAMPLE_CLEAN_TEXT) -> None:
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
        return LLMResponse(
            content=self._response_text,
            model="fake-model",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        )

    async def close(self) -> None:
        pass


@pytest.fixture
def fake_provider(provider_config: ProviderConfig) -> FakeProvider:
    """FakeProvider that returns SAMPLE_CLEAN_TEXT by default."""
    return FakeProvider(provider_config)


@pytest.fixture
def fake_provider_factory(provider_config: ProviderConfig):
    """Factory for creating FakeProvider with custom response text."""
    def _factory(response_text: str) -> FakeProvider:
        return FakeProvider(provider_config, response_text=response_text)
    return _factory


# ---------------------------------------------------------------------------
# Language pack fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def english_pack() -> type[EnglishPack]:
    """The EnglishPack class (used as a class, not instance)."""
    return EnglishPack


# ---------------------------------------------------------------------------
# Filesystem fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_input_file(tmp_path: Path) -> Path:
    """A temp file containing SAMPLE_AI_TEXT for file-based I/O tests."""
    f = tmp_path / "input.txt"
    f.write_text(SAMPLE_AI_TEXT, encoding="utf-8")
    return f


@pytest.fixture
def sample_clean_file(tmp_path: Path) -> Path:
    """A temp file containing SAMPLE_CLEAN_TEXT."""
    f = tmp_path / "clean.txt"
    f.write_text(SAMPLE_CLEAN_TEXT, encoding="utf-8")
    return f
