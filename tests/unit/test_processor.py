"""Unit tests for TextProcessor file I/O handling."""

from __future__ import annotations

from pathlib import Path

import pytest

from anti_slop_writer.core.processor import TextProcessor


class TestTextProcessorFileIO:
    """Tests for file I/O operations in TextProcessor."""

    def test_read_file_success(self, tmp_path: Path) -> None:
        """TextProcessor can read a valid file."""
        # Arrange
        test_file = tmp_path / "test_input.txt"
        test_content = "This is test content for reading."
        test_file.write_text(test_content, encoding="utf-8")

        processor = TextProcessor()

        # Act
        result = processor.read_file(test_file)

        # Assert
        assert result == test_content

    def test_read_file_nonexistent_raises_filenotfound(self, tmp_path: Path) -> None:
        """TextProcessor raises FileNotFoundError for missing file."""
        # Arrange
        nonexistent_file = tmp_path / "does_not_exist.txt"
        processor = TextProcessor()

        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            processor.read_file(nonexistent_file)

        assert "File not found" in str(exc_info.value)

    def test_read_file_directory_raises_valueerror(self, tmp_path: Path) -> None:
        """TextProcessor raises ValueError when path is a directory."""
        # Arrange
        processor = TextProcessor()

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            processor.read_file(tmp_path)

        assert "not a file" in str(exc_info.value)

    def test_read_file_utf8_encoding(self, tmp_path: Path) -> None:
        """TextProcessor correctly reads UTF-8 encoded content."""
        # Arrange
        test_file = tmp_path / "utf8_test.txt"
        test_content = "UTF-8 content: café, naïve, 日本語"
        test_file.write_text(test_content, encoding="utf-8")

        processor = TextProcessor()

        # Act
        result = processor.read_file(test_file)

        # Assert
        assert result == test_content

    def test_write_file_success(self, tmp_path: Path) -> None:
        """TextProcessor can write content to a file."""
        # Arrange
        output_file = tmp_path / "output.txt"
        test_content = "This is test content for writing."
        processor = TextProcessor()

        # Act
        processor.write_file(output_file, test_content)

        # Assert
        assert output_file.exists()
        assert output_file.read_text(encoding="utf-8") == test_content

    def test_write_file_creates_parent_directories(self, tmp_path: Path) -> None:
        """TextProcessor creates parent directories if they don't exist."""
        # Arrange
        output_file = tmp_path / "subdir" / "nested" / "output.txt"
        test_content = "Content in nested directory."
        processor = TextProcessor()

        # Act
        processor.write_file(output_file, test_content)

        # Assert
        assert output_file.exists()
        assert output_file.read_text(encoding="utf-8") == test_content

    def test_write_file_overwrites_existing(self, tmp_path: Path) -> None:
        """TextProcessor overwrites existing file content."""
        # Arrange
        output_file = tmp_path / "existing.txt"
        output_file.write_text("Original content", encoding="utf-8")
        new_content = "New content that replaces original."
        processor = TextProcessor()

        # Act
        processor.write_file(output_file, new_content)

        # Assert
        assert output_file.read_text(encoding="utf-8") == new_content

    def test_get_default_output_path_basic(self, tmp_path: Path) -> None:
        """TextProcessor generates correct default output path."""
        # Arrange
        input_file = tmp_path / "draft.txt"
        processor = TextProcessor()

        # Act
        output_path = processor.get_default_output_path(input_file)

        # Assert
        assert output_path == tmp_path / "draft_rewritten.txt"
        assert output_path.parent == input_file.parent

    def test_get_default_output_path_with_extension(self, tmp_path: Path) -> None:
        """TextProcessor preserves file extension in default output path."""
        # Arrange
        input_file = tmp_path / "article.md"
        processor = TextProcessor()

        # Act
        output_path = processor.get_default_output_path(input_file)

        # Assert
        assert output_path.suffix == ".md"
        assert output_path.stem == "article_rewritten"

    def test_get_default_output_path_no_extension(self, tmp_path: Path) -> None:
        """TextProcessor handles files without extension."""
        # Arrange
        input_file = tmp_path / "document"
        processor = TextProcessor()

        # Act
        output_path = processor.get_default_output_path(input_file)

        # Assert
        assert output_path.name == "document_rewritten"
        assert output_path.suffix == ""

    def test_get_default_output_path_nested_path(self, tmp_path: Path) -> None:
        """TextProcessor preserves directory structure in output path."""
        # Arrange
        input_file = tmp_path / "subdir" / "nested" / "file.txt"
        processor = TextProcessor()

        # Act
        output_path = processor.get_default_output_path(input_file)

        # Assert
        expected = tmp_path / "subdir" / "nested" / "file_rewritten.txt"
        assert output_path == expected


class TestTextProcessorValidation:
    """Tests for file validation in TextProcessor."""

    def test_validate_text_empty_string(self) -> None:
        """TextProcessor rejects empty string."""
        processor = TextProcessor()

        is_valid, error_msg = processor.validate_text("")

        assert is_valid is False
        assert "empty" in error_msg.lower()

    def test_validate_text_whitespace_only(self) -> None:
        """TextProcessor rejects whitespace-only string."""
        processor = TextProcessor()

        is_valid, error_msg = processor.validate_text("   \n\t  ")

        assert is_valid is False
        assert "empty" in error_msg.lower()

    def test_validate_text_valid_content(self) -> None:
        """TextProcessor accepts valid text content."""
        processor = TextProcessor()

        is_valid, error_msg = processor.validate_text("This is valid text.")

        assert is_valid is True
        assert error_msg == ""

    def test_sanitize_text_removes_control_characters(self) -> None:
        """TextProcessor removes control characters except newline and tab."""
        processor = TextProcessor()

        # String with various control characters
        dirty_text = "Hello\x00World\x1F\nNew\tLine"

        result = processor.sanitize_text(dirty_text)

        # Should keep printable chars, newlines, and tabs
        assert result == "HelloWorld\nNew\tLine"


class TestTextProcessorWordCount:
    """Tests for word counting functionality."""

    def test_count_words_basic(self) -> None:
        """TextProcessor counts words correctly in basic text."""
        processor = TextProcessor()

        assert processor.count_words("Hello world") == 2
        assert processor.count_words("One two three four five") == 5

    def test_count_words_with_punctuation(self) -> None:
        """TextProcessor handles punctuation correctly."""
        processor = TextProcessor()

        assert processor.count_words("Hello, world!") == 2
        # "It's" is counted as 2 words (It + s) by word boundary regex
        assert processor.count_words("It's a test.") == 4

    def test_count_words_empty_string(self) -> None:
        """TextProcessor returns 0 for empty string."""
        processor = TextProcessor()

        assert processor.count_words("") == 0
        assert processor.count_words("   ") == 0

    def test_check_word_count_warning_below_threshold(self, capsys) -> None:
        """TextProcessor does not warn when below threshold."""
        processor = TextProcessor(word_count_threshold=100)
        text = "Short text with few words."

        result = processor.check_word_count_warning(text)

        captured = capsys.readouterr()
        assert result is None
        assert "Warning" not in captured.err

    def test_check_word_count_warning_above_threshold(self, capsys) -> None:
        """TextProcessor emits warning when above threshold."""
        processor = TextProcessor(word_count_threshold=5)
        text = "One two three four five six seven eight nine ten"

        result = processor.check_word_count_warning(text)

        captured = capsys.readouterr()
        assert result == 10  # Returns word count
        assert "Warning" in captured.err
        assert "10" in captured.err
