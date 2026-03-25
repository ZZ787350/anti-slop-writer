"""Core rewriter class for text transformation.

This module provides the Rewriter class that orchestrates LLM-based
text rewriting while enforcing AI pattern reduction rules.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from anti_slop_writer.core.models import RewriteResult
from anti_slop_writer.core.rule_engine import RuleEngine

if TYPE_CHECKING:
    from anti_slop_writer.language_packs.base import LanguagePack
    from anti_slop_writer.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class Rewriter:
    """Orchestrates text rewriting to reduce AI-sounding patterns.

    The Rewriter coordinates between:
    - LLM provider for text generation
    - Language pack for pattern detection
    - Rule engine for quality verification

    Attributes:
        provider: LLM provider for API calls.
        language_pack: Language pack for pattern rules.
        default_style: Default style for rewriting.
    """

    def __init__(
        self,
        provider: BaseProvider,
        language_pack: type[LanguagePack],
        *,
        default_style: str = "neutral",
    ) -> None:
        """Initialize the Rewriter.

        Args:
            provider: LLM provider instance.
            language_pack: Language pack class for pattern detection.
            default_style: Default style for rewriting ("neutral", "formal", "casual").
        """
        self._provider = provider
        self._language_pack = language_pack
        self._default_style = default_style
        self._rule_engine = RuleEngine(language_pack)

    @property
    def provider(self) -> BaseProvider:
        """Get the LLM provider."""
        return self._provider

    @property
    def language_pack(self) -> type[LanguagePack]:
        """Get the language pack class."""
        return self._language_pack

    @property
    def default_style(self) -> str:
        """Get the default style."""
        return self._default_style

    async def rewrite(
        self,
        text: str,
        *,
        style: str | None = None,
    ) -> RewriteResult:
        """Rewrite text to reduce AI-sounding patterns.

        Args:
            text: Input text to rewrite.
            style: Output style ("neutral", "formal", "casual").
                   Defaults to self.default_style.

        Returns:
            RewriteResult with original, rewritten text, and metrics.

        Raises:
            ValueError: If text is empty or style is invalid.
            ProviderError: If LLM API call fails.
        """
        # Validate input
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")

        # Use default style if not specified
        effective_style = style or self._default_style

        # Validate style
        valid_styles = {"neutral", "formal", "casual"}
        if effective_style not in valid_styles:
            raise ValueError(
                f"Invalid style '{effective_style}'. Must be: {', '.join(sorted(valid_styles))}"
            )

        # Count patterns before rewriting
        pattern_count_before = self._rule_engine.count_patterns(text, tier=1) + \
                               self._rule_engine.count_patterns(text, tier=2)

        logger.debug(
            "Starting rewrite",
            extra={
                "text_length": len(text),
                "pattern_count_before": pattern_count_before,
                "style": effective_style,
            },
        )

        # Generate system prompt
        system_prompt = self._language_pack.get_system_prompt(effective_style)

        # Call LLM
        start_time = time.monotonic()
        response = await self._provider.call(
            system_prompt=system_prompt,
            user_prompt=text,
        )
        elapsed_ms = int((time.monotonic() - start_time) * 1000)

        rewritten_text = response.content

        # Count patterns after rewriting
        pattern_count_after = self._rule_engine.count_patterns(rewritten_text, tier=1) + \
                              self._rule_engine.count_patterns(rewritten_text, tier=2)

        logger.debug(
            "Rewrite complete",
            extra={
                "elapsed_ms": elapsed_ms,
                "pattern_count_after": pattern_count_after,
                "pattern_reduction": pattern_count_before - pattern_count_after,
            },
        )

        return RewriteResult(
            original_text=text,
            rewritten_text=rewritten_text,
            pattern_count_before=pattern_count_before,
            pattern_count_after=pattern_count_after,
            processing_time_ms=elapsed_ms,
            style_used=effective_style,
        )

    async def __aenter__(self) -> Rewriter:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit - closes provider."""
        await self._provider.close()
