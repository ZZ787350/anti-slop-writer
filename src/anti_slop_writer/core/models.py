"""Core data models for the anti-slop-writer library.

This module defines the core data structures used throughout the rewriting pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anti_slop_writer.language_packs.base import LanguagePack
    from anti_slop_writer.providers.config import ProviderConfig


@dataclass(frozen=True)
class RewriteRequest:
    """Represents a user's request to rewrite text.

    Attributes:
        text: Input text to rewrite (mutually exclusive with file_path).
        file_path: Path to input file (alternative to text).
        style: Output style - "neutral" (default), "formal", or "casual".
        output_path: Output file path (default: stdout).

    Validation:
        - Exactly one of text or file_path must be provided
        - text must be non-empty after stripping whitespace
        - style must be one of: "neutral", "formal", "casual"
    """

    text: str | None = None
    file_path: Path | None = None
    style: str = "neutral"
    output_path: Path | None = None

    def __post_init__(self) -> None:
        """Validate the request after initialization."""
        # Exactly one of text or file_path must be provided
        if self.text is None and self.file_path is None:
            raise ValueError("Either text or file_path must be provided")

        if self.text is not None and self.file_path is not None:
            raise ValueError("Only one of text or file_path can be provided")

        # Validate text if provided
        if self.text is not None and not self.text.strip():
            raise ValueError("Input text cannot be empty")

        # Validate style
        valid_styles = {"neutral", "formal", "casual"}
        if self.style not in valid_styles:
            raise ValueError(
                f"Invalid style '{self.style}'. Must be: {', '.join(sorted(valid_styles))}"
            )


@dataclass(frozen=True)
class RewriteResult:
    """Represents the outcome of a rewrite operation.

    Attributes:
        original_text: The input text (not logged, not stored permanently).
        rewritten_text: The processed output.
        pattern_count_before: Number of AI patterns found in input.
        pattern_count_after: Number of AI patterns in output.
        processing_time_ms: Time taken for LLM call in milliseconds.
        style_used: The style applied during rewriting.
    """

    original_text: str
    rewritten_text: str
    pattern_count_before: int
    pattern_count_after: int
    processing_time_ms: int
    style_used: str

    @property
    def pattern_reduction(self) -> int:
        """Calculate the number of patterns reduced."""
        return self.pattern_count_before - self.pattern_count_after

    def meets_threshold(self) -> bool:
        """Check if the result meets FR-006 conditional threshold.

        Rules:
        - When pre-rewrite count >= 3: post <= pre-1 OR post <= pre*50%
        - When pre-rewrite count < 3: post <= pre (no increase)
        - When pre-rewrite count = 0: no constraint
        """
        pre = self.pattern_count_before
        post = self.pattern_count_after

        if pre == 0:
            return True
        if pre < 3:
            return post <= pre
        # pre >= 3
        return post <= pre - 1 or post <= pre * 0.5


@dataclass
class RewriteContext:
    """Runtime context passed through the rewrite pipeline.

    This class aggregates all necessary components for processing a rewrite request.

    Attributes:
        request: The user's rewrite request.
        config: Provider configuration for LLM connection.
        language_pack: Language-specific rules for pattern detection.
    """

    request: RewriteRequest
    config: ProviderConfig
    language_pack: LanguagePack = field(compare=False)
