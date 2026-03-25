"""Integration test for FR-016 Library-First architecture.

FR-016 states: "Library-First: Core logic usable from CLI or as library import"

This test verifies that the core Rewriter can be used directly without
going through the CLI interface.
"""

from __future__ import annotations

import pytest

from anti_slop_writer.core import Rewriter
from anti_slop_writer.language_packs.english import EnglishPack
from anti_slop_writer.providers.base import LLMResponse
from anti_slop_writer.providers.config import ProviderConfig

from fixtures import FakeProvider  # type: ignore[import-untyped]


@pytest.fixture
def provider_config() -> ProviderConfig:
    """A valid ProviderConfig for testing."""
    return ProviderConfig(
        api_key="test-api-key-1234",
        endpoint="https://api.example.com/v1",
        model="gpt-4o-mini",
        timeout=10.0,
        max_retries=1,
    )


class TestLibraryFirstFR016:
    """Tests for FR-016: Library-First architecture.

    These tests import and use the core modules directly, without CLI.
    """

    @pytest.mark.asyncio
    async def test_import_rewriter_directly(self) -> None:
        """Rewriter can be imported directly from core module."""
        # This test itself proves FR-016 by importing Rewriter
        # at the module level and using it here
        assert Rewriter is not None

    @pytest.mark.asyncio
    async def test_use_rewriter_without_cli(
        self, provider_config: ProviderConfig
    ) -> None:
        """Rewriter works without CLI intervention."""
        provider = FakeProvider(provider_config)
        rewriter = Rewriter(provider, EnglishPack)

        result = await rewriter.rewrite("Test text to rewrite.")

        assert result.original_text == "Test text to rewrite."
        assert len(result.rewritten_text) > 0
        assert result.style_used == "neutral"

    @pytest.mark.asyncio
    async def test_use_rewriter_with_style(
        self, provider_config: ProviderConfig
    ) -> None:
        """Rewriter accepts style parameter without CLI."""
        provider = FakeProvider(provider_config)
        rewriter = Rewriter(provider, EnglishPack)

        result = await rewriter.rewrite("Test text.", style="formal")

        assert result.style_used == "formal"

    @pytest.mark.asyncio
    async def test_use_text_processor_directly(self) -> None:
        """TextProcessor can be used directly without CLI."""
        from anti_slop_writer.core import TextProcessor

        processor = TextProcessor()
        word_count = processor.count_words("Hello world test")

        assert word_count == 3

    @pytest.mark.asyncio
    async def test_use_rule_engine_directly(self) -> None:
        """RuleEngine can be used directly without CLI."""
        from anti_slop_writer.core import RuleEngine

        engine = RuleEngine(EnglishPack)
        pattern_count = engine.count_patterns(
            "In today's fast-paced world, it is crucial to leverage this.",
            tier=1,
        )

        assert pattern_count > 0

    @pytest.mark.asyncio
    async def test_async_context_manager(self, provider_config: ProviderConfig) -> None:
        """Rewriter can be used as async context manager."""
        provider = FakeProvider(provider_config)

        async with Rewriter(provider, EnglishPack) as rewriter:
            result = await rewriter.rewrite("Test text.")
            assert result.rewritten_text

    @pytest.mark.asyncio
    async def test_provider_interface_directly(self, provider_config: ProviderConfig) -> None:
        """Provider interface can be used directly."""
        provider = FakeProvider(provider_config)

        response = await provider.call(
            system_prompt="You are a helpful assistant.",
            user_prompt="Hello",
        )

        assert isinstance(response, LLMResponse)
        assert response.content
        assert response.model == "fake-model"

    def test_all_public_exports_available(self) -> None:
        """All public exports from core module are accessible."""
        from anti_slop_writer.core import (
            RewriteContext,
            RewriteRequest,
            RewriteResult,
            Rewriter,
            RuleEngine,
            TextProcessor,
            get_provider_config,
            get_settings,
            load_config_file,
        )

        # All exports should be accessible
        assert Rewriter is not None
        assert RuleEngine is not None
        assert TextProcessor is not None
        assert RewriteRequest is not None
        assert RewriteResult is not None
        assert RewriteContext is not None
        assert load_config_file is not None
        assert get_settings is not None
        assert get_provider_config is not None