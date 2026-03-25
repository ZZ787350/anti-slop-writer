"""Rule engine for pattern matching and text analysis.

This module provides the RuleEngine class for counting and detecting
AI-typical patterns in text.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anti_slop_writer.language_packs.base import LanguagePack


class RuleEngine:
    """Engine for applying language rules to text.

    The rule engine uses a LanguagePack to count and detect AI-typical
    patterns in text. It enforces FR-006 (pattern reduction) and FR-007
    (no new Tier 1 patterns).

    Attributes:
        language_pack: The language pack containing patterns.
    """

    def __init__(self, language_pack: type[LanguagePack]) -> None:
        """Initialize the rule engine.

        Args:
            language_pack: Language pack class to use for pattern matching.
        """
        self._language_pack = language_pack

    @property
    def language_pack(self) -> type[LanguagePack]:
        """Get the language pack."""
        return self._language_pack

    def count_patterns(self, text: str, tier: int = 1) -> int:
        """Count the number of pattern matches in text.

        Args:
            text: Text to analyze.
            tier: Which tier to count (1 or 2).

        Returns:
            Number of pattern matches found.
        """
        return self._language_pack.count_patterns(text, tier=tier)

    def count_all_patterns(self, text: str) -> tuple[int, int]:
        """Count both tier 1 and tier 2 pattern matches.

        Args:
            text: Text to analyze.

        Returns:
            Tuple of (tier1_count, tier2_count).
        """
        return self._language_pack.count_all_patterns(text)

    def check_no_new_tier1(
        self, original: str, rewritten: str
    ) -> tuple[bool, list[tuple[str, str]]]:
        """Check that no new Tier 1 patterns were introduced (FR-007).

        Args:
            original: Original text.
            rewritten: Rewritten text.

        Returns:
            Tuple of (passed, new_matches) where new_matches is a list of
            (matched_text, category) tuples for any new Tier 1 patterns.
        """
        original_matches = {
            match.lower() for match, _ in self._language_pack.find_tier1_matches(original)
        }
        rewritten_matches = self._language_pack.find_tier1_matches(rewritten)

        new_matches: list[tuple[str, str]] = []
        for match, category in rewritten_matches:
            if match.lower() not in original_matches:
                new_matches.append((match, category))

        return len(new_matches) == 0, new_matches

    def check_threshold(
        self, pattern_count_before: int, pattern_count_after: int
    ) -> bool:
        """Check if the pattern reduction meets FR-006 threshold.

        Rules:
        - When pre-rewrite count >= 3: post <= pre-1 OR post <= pre*50%
        - When pre-rewrite count < 3: post <= pre (no increase)
        - When pre-rewrite count = 0: no constraint

        Args:
            pattern_count_before: Pattern count before rewriting.
            pattern_count_after: Pattern count after rewriting.

        Returns:
            True if threshold is met, False otherwise.
        """
        if pattern_count_before == 0:
            return True
        if pattern_count_before < 3:
            return pattern_count_after <= pattern_count_before
        # pre >= 3
        return (
            pattern_count_after <= pattern_count_before - 1
            or pattern_count_after <= pattern_count_before * 0.5
        )

    def get_pattern_summary(self, text: str) -> dict[str, int]:
        """Get a summary of pattern counts by category.

        Args:
            text: Text to analyze.

        Returns:
            Dictionary mapping category names to counts.
        """
        summary: dict[str, int] = {}

        for pattern in self._language_pack.tier1_patterns:
            count = len(pattern.regex.findall(text))
            if count > 0:
                category = f"tier1_{pattern.category}"
                summary[category] = summary.get(category, 0) + count

        for pattern in self._language_pack.tier2_patterns:
            count = len(pattern.regex.findall(text))
            if count > 0:
                category = f"tier2_{pattern.category}"
                summary[category] = summary.get(category, 0) + count

        return summary
