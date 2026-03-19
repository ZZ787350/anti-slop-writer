# CONTRIBUTING.md - anti-slop-writer

> Development and contribution guide

## Development Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourname/anti-slop-writer.git
cd anti-slop-writer

# Install dependencies
uv sync

# Or with pip
pip install -e ".[dev]"
```

### Environment Setup

Create a `.env` file for API keys:

```bash
# .env
OPENAI_API_KEY=your-key-here
# or
ANTHROPIC_API_KEY=your-key-here
```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/anti_slop_writer

# Run specific test file
uv run pytest tests/test_rewriter.py

# Run with verbose output
uv run pytest -v
```

### Type Checking

```bash
uv run mypy src/
```

### Linting and Formatting

```bash
# Check for issues
uv run ruff check src/

# Auto-fix issues
uv run ruff check --fix src/

# Format code
uv run ruff format src/
```

### Run All Checks

```bash
uv run ruff check src/ && uv run mypy src/ && uv run pytest
```

## Project Structure

```
anti-slop-writer/
├── src/anti_slop_writer/    # Main package
│   ├── core/                # Core rewriting logic
│   ├── language_packs/      # Language-specific rules
│   ├── providers/           # LLM integrations
│   └── interfaces/          # CLI entry point
├── tests/                   # Test suite
├── references/              # Documentation references
└── pyproject.toml           # Project configuration
```

## Code Style

- **Formatter**: ruff (line length: 88)
- **Type hints**: Required for all public functions
- **Docstrings**: Google style for public APIs
- **Imports**: Sorted by ruff/isort

### Example

```python
"""Module for text rewriting."""

from typing import Final

from anti_slop_writer.core import Rewriter


def rewrite_text(text: str, style: str = "neutral") -> str:
    """Rewrite text to reduce AI patterns.

    Args:
        text: The input text to rewrite.
        style: Output style (formal, casual, neutral).

    Returns:
        The rewritten text.

    Raises:
        ValueError: If text is empty.
    """
    if not text:
        raise ValueError("Text cannot be empty")

    rewriter = Rewriter(style=style)
    return rewriter.rewrite(text)
```

## Testing Guidelines

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_core/
│   ├── test_rewriter.py
│   └── test_processor.py
├── test_providers/
│   └── test_openai.py
└── test_interfaces/
    └── test_cli.py
```

### Writing Tests

```python
import pytest

from anti_slop_writer.core import Rewriter


class TestRewriter:
    """Tests for the Rewriter class."""

    def test_rewrite_basic_text(self) -> None:
        """Test basic text rewriting."""
        rewriter = Rewriter()
        result = rewriter.rewrite("Hello world")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_rewrite_empty_raises(self) -> None:
        """Test that empty input raises ValueError."""
        rewriter = Rewriter()
        with pytest.raises(ValueError, match="empty"):
            rewriter.rewrite("")
```

## Pull Request Process

1. **Create a branch**: `git checkout -b feature/your-feature`
2. **Make changes**: Follow code style guidelines
3. **Add tests**: New features need tests
4. **Run checks**: `uv run ruff check src/ && uv run mypy src/ && uv run pytest`
5. **Commit**: Use clear commit messages
6. **Push and create PR**: Describe changes and link issues

### PR Checklist

- [ ] Tests pass locally
- [ ] Type checking passes
- [ ] Linting passes
- [ ] New code has tests
- [ ] Documentation updated (if needed)

## Module Boundaries

Respect the dependency direction:

```
Interfaces → Core ← Language Packs
    ↓
Providers
```

- Core never imports from Interfaces
- Language Packs never import from Core
- Providers never import from Core

## Questions?

Open an issue for:
- Bug reports
- Feature requests
- Documentation improvements