"""Unit tests for the Rewriter class."""

from __future__ import annotations

import pytest

from anti_slop_writer.core.models import RewriteResult
from anti_slop_writer.core.rewriter import Rewriter
from anti_slop_writer.language_packs.english import EnglishPack
from anti_slop_writer.providers.base import (
    AuthenticationError,
    BaseProvider,
    LLMResponse,
    NetworkError,
)
from anti_slop_writer.providers.config import ProviderConfig

# Sample texts for testing
SAMPLE_AI_TEXT = (
    "In today's fast-paced world, it is crucial to leverage cutting-edge "
    "solutions. This groundbreaking approach will seamlessly transform the "
    "paradigm and foster innovation across the ecosystem."
)

SAMPLE_CLEAN_TEXT = (
    "The new approach saves time and works well in practice. "
    "It removes steps that caused delays and makes the process simpler."
)


class FakeProvider(BaseProvider):
    """A fake LLM provider for tests that returns a configurable response."""

    def __init__(
        self, config: ProviderConfig, response_text: str = SAMPLE_CLEAN_TEXT
    ) -> None:
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
def provider_config() -> ProviderConfig:
    """A valid ProviderConfig pointing at a fake endpoint."""
    return ProviderConfig(
        api_key="test-api-key-1234",
        endpoint="https://api.example.com/v1",
        model="gpt-4o-mini",
        timeout=10.0,
        max_retries=1,
    )


@pytest.fixture
def english_pack() -> type[EnglishPack]:
    """The EnglishPack class."""
    return EnglishPack


class TestRewriterInit:
    """Tests for Rewriter initialization."""

    def test_init_with_valid_provider(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """Rewriter initializes with valid provider and language pack."""
        provider = FakeProvider(provider_config)
        rewriter = Rewriter(provider, english_pack)

        assert rewriter.provider is provider
        assert rewriter.language_pack is english_pack

    def test_init_with_style_default(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """Rewriter uses neutral style by default."""
        provider = FakeProvider(provider_config)
        rewriter = Rewriter(provider, english_pack)

        assert rewriter.default_style == "neutral"


class TestRewriterRewrite:
    """Tests for the rewrite method."""

    @pytest.mark.asyncio
    async def test_rewrite_basic(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """Rewriter produces RewriteResult with expected fields."""
        provider = FakeProvider(provider_config)
        rewriter = Rewriter(provider, english_pack)

        result = await rewriter.rewrite("Test text to rewrite.")

        assert isinstance(result, RewriteResult)
        assert result.original_text == "Test text to rewrite."
        assert len(result.rewritten_text) > 0
        assert result.style_used == "neutral"
        assert result.processing_time_ms >= 0

    @pytest.mark.asyncio
    async def test_rewrite_with_style(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """Rewriter applies style to the system prompt."""
        provider = FakeProvider(provider_config)
        rewriter = Rewriter(provider, english_pack)

        result = await rewriter.rewrite("Test text.", style="formal")

        assert result.style_used == "formal"

    @pytest.mark.asyncio
    async def test_rewrite_pattern_counting(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """Rewriter counts patterns before and after rewriting."""
        ai_text = "In today's world, it is crucial to leverage this approach."
        clean_text = "Now, it's important to use this approach."

        provider = FakeProvider(provider_config, response_text=clean_text)
        rewriter = Rewriter(provider, english_pack)

        result = await rewriter.rewrite(ai_text)

        assert result.pattern_count_before > 0
        assert result.pattern_count_after < result.pattern_count_before

    @pytest.mark.asyncio
    async def test_rewrite_empty_text_raises_error(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """Rewriter raises ValueError for empty text."""
        provider = FakeProvider(provider_config)
        rewriter = Rewriter(provider, english_pack)

        with pytest.raises(ValueError, match="cannot be empty"):
            await rewriter.rewrite("")

    @pytest.mark.asyncio
    async def test_rewrite_whitespace_only_raises_error(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """Rewriter raises ValueError for whitespace-only text."""
        provider = FakeProvider(provider_config)
        rewriter = Rewriter(provider, english_pack)

        with pytest.raises(ValueError, match="cannot be empty"):
            await rewriter.rewrite("   \n\t  ")

    @pytest.mark.asyncio
    async def test_rewrite_invalid_style_raises_error(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """Rewriter raises ValueError for invalid style."""
        provider = FakeProvider(provider_config)
        rewriter = Rewriter(provider, english_pack)

        with pytest.raises(ValueError, match="Invalid style"):
            await rewriter.rewrite("Test text.", style="unknown")


class TestRewriterErrorHandling:
    """Tests for error handling in the rewrite flow."""

    @pytest.mark.asyncio
    async def test_rewrite_authentication_error(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """Rewriter propagates authentication errors."""

        class AuthErrorProvider(FakeProvider):
            async def call(self, *args: object, **kwargs: object) -> LLMResponse:
                raise AuthenticationError("Invalid API key")

        provider = AuthErrorProvider(provider_config)
        rewriter = Rewriter(provider, english_pack)

        with pytest.raises(AuthenticationError):
            await rewriter.rewrite("Test text.")

    @pytest.mark.asyncio
    async def test_rewrite_network_error(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """Rewriter propagates network errors."""

        class NetworkErrorProvider(FakeProvider):
            async def call(self, *args: object, **kwargs: object) -> LLMResponse:
                raise NetworkError("Connection refused")

        provider = NetworkErrorProvider(provider_config)
        rewriter = Rewriter(provider, english_pack)

        with pytest.raises(NetworkError):
            await rewriter.rewrite("Test text.")


class TestRewriterResult:
    """Tests for RewriteResult methods."""

    def test_pattern_reduction_calculation(self) -> None:
        """pattern_reduction returns correct difference."""
        result = RewriteResult(
            original_text="test",
            rewritten_text="test",
            pattern_count_before=10,
            pattern_count_after=3,
            processing_time_ms=100,
            style_used="neutral",
        )

        assert result.pattern_reduction == 7

    def test_meets_threshold_pre_zero(self) -> None:
        """meets_threshold returns True when pre-count is zero."""
        result = RewriteResult(
            original_text="test",
            rewritten_text="test",
            pattern_count_before=0,
            pattern_count_after=0,
            processing_time_ms=100,
            style_used="neutral",
        )

        assert result.meets_threshold() is True

    def test_meets_threshold_pre_less_than_3(self) -> None:
        """meets_threshold requires no increase when pre-count < 3."""
        # No increase - passes
        result_pass = RewriteResult(
            original_text="test",
            rewritten_text="test",
            pattern_count_before=2,
            pattern_count_after=2,
            processing_time_ms=100,
            style_used="neutral",
        )
        assert result_pass.meets_threshold() is True

        # Increase - fails
        result_fail = RewriteResult(
            original_text="test",
            rewritten_text="test",
            pattern_count_before=2,
            pattern_count_after=3,
            processing_time_ms=100,
            style_used="neutral",
        )
        assert result_fail.meets_threshold() is False

    def test_meets_threshold_pre_gte_3(self) -> None:
        """meets_threshold requires reduction when pre-count >= 3."""
        # Reduce by at least 1 - passes
        result_reduce_by_1 = RewriteResult(
            original_text="test",
            rewritten_text="test",
            pattern_count_before=5,
            pattern_count_after=4,
            processing_time_ms=100,
            style_used="neutral",
        )
        assert result_reduce_by_1.meets_threshold() is True

        # Reduce to <= 50% - passes
        result_reduce_50 = RewriteResult(
            original_text="test",
            rewritten_text="test",
            pattern_count_before=10,
            pattern_count_after=5,
            processing_time_ms=100,
            style_used="neutral",
        )
        assert result_reduce_50.meets_threshold() is True

        # No reduction - fails
        result_no_reduce = RewriteResult(
            original_text="test",
            rewritten_text="test",
            pattern_count_before=5,
            pattern_count_after=5,
            processing_time_ms=100,
            style_used="neutral",
        )
        assert result_no_reduce.meets_threshold() is False


class TestStylePromptInjection:
    """Tests for style prompt injection (Phase 5, US3)."""

    @pytest.mark.asyncio
    async def test_style_formal_includes_style_instruction(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """Formal style includes formal style instruction in system prompt."""
        captured_prompts: dict[str, str] = {}

        class CapturingProvider(FakeProvider):
            async def call(
                self,
                system_prompt: str,
                user_prompt: str,
                **kwargs: object,
            ) -> LLMResponse:
                captured_prompts["system"] = system_prompt
                captured_prompts["user"] = user_prompt
                return await super().call(system_prompt, user_prompt, **kwargs)

        provider = CapturingProvider(provider_config)
        rewriter = Rewriter(provider, english_pack)

        await rewriter.rewrite("Test text.", style="formal")

        # Verify formal style instructions are in the system prompt
        system_prompt = captured_prompts["system"]
        assert "contractions" in system_prompt.lower() or "complete sentences" in system_prompt.lower()

    @pytest.mark.asyncio
    async def test_style_casual_includes_style_instruction(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """Casual style includes casual style instruction in system prompt."""
        captured_prompts: dict[str, str] = {}

        class CapturingProvider(FakeProvider):
            async def call(
                self,
                system_prompt: str,
                user_prompt: str,
                **kwargs: object,
            ) -> LLMResponse:
                captured_prompts["system"] = system_prompt
                return await super().call(system_prompt, user_prompt, **kwargs)

        provider = CapturingProvider(provider_config)
        rewriter = Rewriter(provider, english_pack)

        await rewriter.rewrite("Test text.", style="casual")

        # Verify casual style instructions are in the system prompt
        system_prompt = captured_prompts["system"]
        assert "contractions" in system_prompt.lower() or "conversational" in system_prompt.lower()

    @pytest.mark.asyncio
    async def test_style_neutral_no_extra_instruction(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """Neutral style does not add extra style instructions."""
        captured_prompts: dict[str, str] = {}

        class CapturingProvider(FakeProvider):
            async def call(
                self,
                system_prompt: str,
                user_prompt: str,
                **kwargs: object,
            ) -> LLMResponse:
                captured_prompts["system"] = system_prompt
                return await super().call(system_prompt, user_prompt, **kwargs)

        provider = CapturingProvider(provider_config)
        rewriter = Rewriter(provider, english_pack)

        await rewriter.rewrite("Test text.", style="neutral")

        # Neutral style should not have a style section
        system_prompt = captured_prompts["system"]
        # The prompt should not have an extra Style section for neutral
        assert "Style:" not in system_prompt or system_prompt.endswith("Be direct and clear")

    @pytest.mark.asyncio
    async def test_default_style_is_used_when_not_specified(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """Rewriter uses default_style when style not specified."""
        provider = FakeProvider(provider_config)
        rewriter = Rewriter(provider, english_pack, default_style="formal")

        result = await rewriter.rewrite("Test text.")

        assert result.style_used == "formal"

    @pytest.mark.asyncio
    async def test_explicit_style_overrides_default(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """Explicit style parameter overrides default_style."""
        provider = FakeProvider(provider_config)
        rewriter = Rewriter(provider, english_pack, default_style="formal")

        result = await rewriter.rewrite("Test text.", style="casual")

        assert result.style_used == "casual"

    @pytest.mark.asyncio
    async def test_all_valid_styles_accepted(
        self, provider_config: ProviderConfig, english_pack: type[EnglishPack]
    ) -> None:
        """All valid styles (neutral, formal, casual) are accepted."""
        provider = FakeProvider(provider_config)
        rewriter = Rewriter(provider, english_pack)

        for style in ["neutral", "formal", "casual"]:
            result = await rewriter.rewrite("Test text.", style=style)
            assert result.style_used == style

    def test_english_pack_has_all_style_prompts(
        self, english_pack: type[EnglishPack]
    ) -> None:
        """EnglishPack has prompts for all valid styles."""
        valid_styles = ["neutral", "formal", "casual"]

        for style in valid_styles:
            assert style in english_pack.style_prompts

    def test_english_pack_get_system_prompt_returns_string(
        self, english_pack: type[EnglishPack]
    ) -> None:
        """get_system_prompt returns a non-empty string for all styles."""
        for style in ["neutral", "formal", "casual"]:
            prompt = english_pack.get_system_prompt(style)
            assert isinstance(prompt, str)
            assert len(prompt) > 0
            # All prompts should contain the core instruction
            assert "AI" in prompt or "natural" in prompt.lower()