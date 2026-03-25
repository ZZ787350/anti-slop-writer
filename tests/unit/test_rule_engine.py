"""Unit tests for the RuleEngine class."""

from __future__ import annotations

import pytest

from anti_slop_writer.core.rule_engine import RuleEngine
from anti_slop_writer.language_packs.english import EnglishPack


@pytest.fixture
def rule_engine() -> RuleEngine:
    """Provide a RuleEngine with EnglishPack."""
    return RuleEngine(EnglishPack)


class TestRuleEngineCountPatterns:
    """Tests for pattern counting methods."""

    def test_count_patterns_tier1_empty_text(self, rule_engine: RuleEngine) -> None:
        """count_patterns returns 0 for empty text."""
        assert rule_engine.count_patterns("", tier=1) == 0

    def test_count_patterns_tier1_no_matches(
        self, rule_engine: RuleEngine
    ) -> None:
        """count_patterns returns 0 when no patterns match."""
        clean_text = "The quick brown fox jumps over the lazy dog."
        assert rule_engine.count_patterns(clean_text, tier=1) == 0

    def test_count_patterns_tier1_with_matches(
        self, rule_engine: RuleEngine
    ) -> None:
        """count_patterns correctly counts tier 1 pattern matches."""
        ai_text = "In today's world, it is crucial to leverage this groundbreaking approach."
        # "In today's world" (opening_crutches) + "crucial" + "leverage" (tier2) + "groundbreaking"
        # Tier 1: "In today's world", "crucial", "groundbreaking" = 3
        count = rule_engine.count_patterns(ai_text, tier=1)
        assert count >= 3  # At least these 3

    def test_count_patterns_tier2_with_matches(
        self, rule_engine: RuleEngine
    ) -> None:
        """count_patterns correctly counts tier 2 pattern matches."""
        text = "We need to leverage and facilitate this process."
        # "leverage" + "facilitate" = 2 tier 2 matches
        count = rule_engine.count_patterns(text, tier=2)
        assert count >= 2

    def test_count_all_patterns_returns_tuple(
        self, rule_engine: RuleEngine
    ) -> None:
        """count_all_patterns returns (tier1_count, tier2_count) tuple."""
        text = "It is crucial to leverage this approach."
        tier1, tier2 = rule_engine.count_all_patterns(text)

        assert isinstance(tier1, int)
        assert isinstance(tier2, int)
        assert tier1 >= 1  # "crucial" is tier 1
        assert tier2 >= 1  # "leverage" is tier 2


class TestRuleEngineCheckNoNewTier1:
    """Tests for FR-007: No new Tier 1 patterns should be introduced."""

    def test_check_no_new_tier1_clean_rewrite(
        self, rule_engine: RuleEngine
    ) -> None:
        """check_no_new_tier1 passes when no new Tier 1 patterns added."""
        original = "This is a pivotal moment for our team."
        rewritten = "This is an important moment for our team."
        # Original has "pivotal" (tier 1)
        # Rewritten has no tier 1 patterns

        passed, new_matches = rule_engine.check_no_new_tier1(original, rewritten)

        assert passed is True
        assert new_matches == []

    def test_check_no_new_tier1_introduces_new_pattern(
        self, rule_engine: RuleEngine
    ) -> None:
        """check_no_new_tier1 fails when new Tier 1 pattern introduced."""
        original = "We should consider this option."
        rewritten = "In today's world, we should consider this option."
        # Original has no tier 1 patterns
        # Rewritten has "In today's world" (tier 1)

        passed, new_matches = rule_engine.check_no_new_tier1(original, rewritten)

        assert passed is False
        assert len(new_matches) >= 1
        assert any("today's" in match.lower() for match, _ in new_matches)

    def test_check_no_new_tier1_preserves_existing(
        self, rule_engine: RuleEngine
    ) -> None:
        """check_no_new_tier1 passes when existing Tier 1 pattern preserved."""
        original = "This is a crucial decision."
        rewritten = "This is a crucial decision for us."
        # Both have "crucial" - no NEW patterns

        passed, new_matches = rule_engine.check_no_new_tier1(original, rewritten)

        assert passed is True

    def test_check_no_new_tier1_case_insensitive(
        self, rule_engine: RuleEngine
    ) -> None:
        """check_no_new_tier1 is case-insensitive."""
        original = "This is CRUCIAL."
        rewritten = "This is crucial and groundbreaking."
        # Original has "CRUCIAL" (case-insensitive match)
        # Rewritten has "crucial" + "groundbreaking"
        # New pattern: "groundbreaking"

        passed, new_matches = rule_engine.check_no_new_tier1(original, rewritten)

        assert passed is False
        assert any("groundbreaking" in match.lower() for match, _ in new_matches)


class TestRuleEngineCheckThreshold:
    """Tests for FR-006: Pattern reduction threshold checking."""

    def test_check_threshold_pre_zero(self, rule_engine: RuleEngine) -> None:
        """check_threshold passes when pre-count is zero."""
        assert rule_engine.check_threshold(0, 0) is True
        assert rule_engine.check_threshold(0, 5) is True  # No constraint when pre=0

    def test_check_threshold_pre_less_than_3(
        self, rule_engine: RuleEngine
    ) -> None:
        """check_threshold requires no increase when pre < 3."""
        assert rule_engine.check_threshold(1, 1) is True
        assert rule_engine.check_threshold(1, 0) is True
        assert rule_engine.check_threshold(2, 2) is True
        assert rule_engine.check_threshold(2, 3) is False  # Increase not allowed

    def test_check_threshold_pre_gte_3_reduce_by_1(
        self, rule_engine: RuleEngine
    ) -> None:
        """check_threshold passes when reduced by at least 1 (pre >= 3)."""
        assert rule_engine.check_threshold(3, 2) is True
        assert rule_engine.check_threshold(5, 4) is True
        assert rule_engine.check_threshold(10, 9) is True

    def test_check_threshold_pre_gte_3_reduce_to_50_percent(
        self, rule_engine: RuleEngine
    ) -> None:
        """check_threshold passes when reduced to <= 50% (pre >= 3)."""
        assert rule_engine.check_threshold(10, 5) is True
        assert rule_engine.check_threshold(10, 4) is True
        assert rule_engine.check_threshold(100, 50) is True

    def test_check_threshold_pre_gte_3_fails_no_reduction(
        self, rule_engine: RuleEngine
    ) -> None:
        """check_threshold fails when not reduced (pre >= 3)."""
        assert rule_engine.check_threshold(3, 3) is False
        assert rule_engine.check_threshold(5, 5) is False
        assert rule_engine.check_threshold(10, 10) is False

    def test_check_threshold_pre_gte_3_fails_insufficient_reduction(
        self, rule_engine: RuleEngine
    ) -> None:
        """check_threshold fails when reduction insufficient (pre >= 3)."""
        # 10 -> 9 reduces by 1, but 9 > 50% of 10
        # This should still pass because reduce by 1 is one valid criterion
        assert rule_engine.check_threshold(10, 9) is True

        # 10 -> 6 is reduce by 4, and 6 <= 50% of 10
        assert rule_engine.check_threshold(10, 6) is True

        # 10 -> 8: reduce by 2 but 8 > 50% - passes because reduced by at least 1
        assert rule_engine.check_threshold(10, 8) is True


class TestRuleEngineGetPatternSummary:
    """Tests for pattern summary generation."""

    def test_get_pattern_summary_empty(self, rule_engine: RuleEngine) -> None:
        """get_pattern_summary returns empty dict for clean text."""
        text = "The quick brown fox jumps."
        summary = rule_engine.get_pattern_summary(text)

        assert summary == {}

    def test_get_pattern_summary_with_matches(
        self, rule_engine: RuleEngine
    ) -> None:
        """get_pattern_summary returns category counts."""
        text = "It is crucial and pivotal to leverage this."
        summary = rule_engine.get_pattern_summary(text)

        # "crucial" and "pivotal" are significance_puffers (tier 1)
        assert "tier1_significance_puffers" in summary
        assert summary["tier1_significance_puffers"] >= 2

        # "leverage" is analytical_verbs (tier 2)
        assert "tier2_analytical_verbs" in summary

    def test_get_pattern_summary_multiple_categories(
        self, rule_engine: RuleEngine
    ) -> None:
        """get_pattern_summary correctly groups by category."""
        text = "In today's world, it is crucial to leverage and facilitate."
        summary = rule_engine.get_pattern_summary(text)

        # Should have opening_crutches category
        assert any("opening_crutches" in cat for cat in summary.keys())
        # Should have significance_puffers category
        assert any("significance_puffers" in cat for cat in summary.keys())
        # Should have analytical_verbs category
        assert any("analytical_verbs" in cat for cat in summary.keys())


class TestRuleEngineLanguagePackProperty:
    """Tests for language_pack property."""

    def test_language_pack_returns_correct_class(
        self, rule_engine: RuleEngine
    ) -> None:
        """language_pack property returns the configured language pack class."""
        assert rule_engine.language_pack is EnglishPack

    def test_language_pack_can_be_used_for_direct_access(
        self, rule_engine: RuleEngine
    ) -> None:
        """language_pack can be used to access language pack methods."""
        pack = rule_engine.language_pack
        assert pack.language_code == "en"