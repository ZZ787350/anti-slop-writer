"""Base class for language-specific rule packs.

This module defines the abstract interface for language packs that contain
vocabulary patterns and style guidance for text rewriting.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class Pattern:
    """A pattern for detecting AI-typical language.

    Attributes:
        regex: Compiled regex pattern for matching.
        category: Category name (e.g., "significance_puffers").
        replacement: Suggested alternative text (for tier2 patterns).
    """

    regex: re.Pattern[str]
    category: str
    replacement: str | None = None


class LanguagePack(ABC):
    """Abstract base class for language-specific rules.

    Language packs define vocabulary patterns and style prompts for a specific
    language. Each pack contains two tiers of patterns:
    - Tier 1: Hard-ban patterns that must not appear in output
    - Tier 2: Soft-guidance patterns that should be reduced

    Attributes:
        language_code: ISO 639-1 code (e.g., "en").
        tier1_patterns: Hard-ban patterns (must not appear in output).
        tier2_patterns: Soft-guidance patterns (should be reduced).
        style_prompts: Style-specific prompt modifiers.
    """

    language_code: ClassVar[str]
    tier1_patterns: ClassVar[list[Pattern]]
    tier2_patterns: ClassVar[list[Pattern]]
    style_prompts: ClassVar[dict[str, str]]

    @classmethod
    @abstractmethod
    def get_system_prompt(cls, style: str = "neutral") -> str:
        """Generate the system prompt for the LLM.

        Args:
            style: Output style - "neutral", "formal", or "casual".

        Returns:
            System prompt string for the LLM.
        """
        ...

    @classmethod
    @abstractmethod
    def count_patterns(cls, text: str, tier: int = 1) -> int:
        """Count the number of pattern matches in text.

        Args:
            text: Text to analyze.
            tier: Which tier to count (1 or 2).

        Returns:
            Number of pattern matches found.
        """
        ...

    @classmethod
    def count_all_patterns(cls, text: str) -> tuple[int, int]:
        """Count both tier 1 and tier 2 pattern matches.

        Args:
            text: Text to analyze.

        Returns:
            Tuple of (tier1_count, tier2_count).
        """
        return cls.count_patterns(text, tier=1), cls.count_patterns(text, tier=2)

    @classmethod
    def find_tier1_matches(cls, text: str) -> list[tuple[str, str]]:
        """Find all tier 1 pattern matches in text.

        Args:
            text: Text to analyze.

        Returns:
            List of (matched_text, category) tuples.
        """
        matches: list[tuple[str, str]] = []
        for pattern in cls.tier1_patterns:
            for match in pattern.regex.finditer(text):
                matches.append((match.group(), pattern.category))
        return matches
