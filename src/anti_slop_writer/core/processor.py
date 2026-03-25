"""Text processing utilities for the rewriting pipeline.

This module provides utilities for text validation, word counting,
and structure preservation verification.
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# FR-017: Word count threshold for warning
WORD_COUNT_WARNING_THRESHOLD = 5000


class TextProcessor:
    """Utilities for processing and validating text.

    This class provides text processing utilities including:
    - Word counting
    - Text validation
    - Paragraph structure analysis
    - FR-017 word count warning

    Attributes:
        word_count_threshold: Threshold for emitting word count warning.
    """

    def __init__(self, *, word_count_threshold: int = WORD_COUNT_WARNING_THRESHOLD) -> None:
        """Initialize the TextProcessor.

        Args:
            word_count_threshold: Word count threshold for warning (default: 5000).
        """
        self._word_count_threshold = word_count_threshold

    @property
    def word_count_threshold(self) -> int:
        """Get the word count warning threshold."""
        return self._word_count_threshold

    def count_words(self, text: str) -> int:
        """Count the number of words in text.

        Words are defined as sequences of alphanumeric characters
        separated by whitespace or punctuation.

        Args:
            text: Text to count words in.

        Returns:
            Number of words.
        """
        # Match word boundaries - sequences of alphanumeric chars
        words = re.findall(r"\b\w+\b", text)
        return len(words)

    def validate_text(self, text: str) -> tuple[bool, str]:
        """Validate that text is suitable for rewriting.

        Args:
            text: Text to validate.

        Returns:
            Tuple of (is_valid, error_message).
            error_message is empty string if valid.
        """
        if not text:
            return False, "Input text cannot be empty"

        if not text.strip():
            return False, "Input text cannot be empty"

        # Remove control characters except newline and tab
        sanitized = "".join(c for c in text if c.isprintable() or c in "\n\t")
        if not sanitized.strip():
            return False, "Input text contains only control characters"

        return True, ""

    def check_word_count_warning(self, text: str) -> int | None:
        """Check if text exceeds word count threshold and emit warning (FR-017).

        If the word count exceeds the threshold, emits a warning to stderr
        but does not block processing.

        Args:
            text: Text to check.

        Returns:
            Word count if exceeds threshold, None otherwise.
        """
        word_count = self.count_words(text)

        if word_count > self._word_count_threshold:
            warning = (
                f"Warning: Input exceeds {self._word_count_threshold:,} words "
                f"({word_count:,} words). Output quality may be reduced.\n"
            )
            # Emit to stderr per FR-017
            print(warning, file=sys.stderr, end="")
            logger.warning(
                "Input exceeds word count threshold",
                extra={
                    "word_count": word_count,
                    "threshold": self._word_count_threshold,
                },
            )
            return word_count

        return None

    def count_paragraphs(self, text: str) -> int:
        """Count the number of paragraphs in text.

        Paragraphs are defined as blocks of text separated by
        one or more blank lines.

        Args:
            text: Text to analyze.

        Returns:
            Number of paragraphs.
        """
        # Split by one or more blank lines
        paragraphs = re.split(r"\n\s*\n", text.strip())
        # Filter out empty strings
        return len([p for p in paragraphs if p.strip()])

    def validate_structure_preservation(
        self, original: str, rewritten: str
    ) -> tuple[bool, str]:
        """Verify that paragraph structure is preserved (FR-004).

        Args:
            original: Original text.
            rewritten: Rewritten text.

        Returns:
            Tuple of (preserved, error_message).
        """
        original_paragraphs = self.count_paragraphs(original)
        rewritten_paragraphs = self.count_paragraphs(rewritten)

        if original_paragraphs != rewritten_paragraphs:
            return False, (
                f"Paragraph structure not preserved: "
                f"original has {original_paragraphs}, rewritten has {rewritten_paragraphs}"
            )

        return True, ""

    def sanitize_text(self, text: str) -> str:
        """Sanitize text by removing control characters.

        Removes control characters except newlines and tabs.

        Args:
            text: Text to sanitize.

        Returns:
            Sanitized text.
        """
        return "".join(c for c in text if c.isprintable() or c in "\n\t")

    def read_file(self, path: Path) -> str:
        """Read text from a file.

        Args:
            path: Path to the file.

        Returns:
            File contents as string.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If file is not readable.
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")

        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Failed to read file: {path} - {e}") from e

    def write_file(self, path: Path, content: str) -> None:
        """Write text to a file.

        Creates parent directories if they don't exist.

        Args:
            path: Path to the file.
            content: Content to write.

        Raises:
            ValueError: If file cannot be written.
        """
        try:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Failed to write file: {path} - {e}") from e

    def get_default_output_path(self, input_path: Path) -> Path:
        """Generate default output path for a given input path.

        Default naming: <input_filename>_rewritten.<extension>
        Example: draft.txt -> draft_rewritten.txt

        Args:
            input_path: Input file path.

        Returns:
            Output file path with _rewritten suffix.
        """
        stem = input_path.stem
        suffix = input_path.suffix
        parent = input_path.parent

        return parent / f"{stem}_rewritten{suffix}"
