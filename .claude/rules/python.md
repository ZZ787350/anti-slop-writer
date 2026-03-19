# Python Code Standards - anti-slop-writer

> Python development guidelines

## Version and Tooling

- **Python**: 3.11+
- **Formatter**: ruff (line length: 88)
- **Linter**: ruff
- **Type checker**: mypy (strict mode)

## Code Style

### Formatting
- Use ruff for all formatting
- Line length: 88 characters
- Use double quotes for strings
- Trailing commas in multi-line structures

### Imports
```python
# Standard library
import os
from typing import Final

# Third-party
import httpx
from typer import Typer

# Local imports
from anti_slop_writer.core import Rewriter
```

### Type Hints
- Required for all public functions and methods
- Use modern type syntax (Python 3.11+)

```python
# Good
def process(text: str, *, max_length: int | None = None) -> str:
    ...

# Bad
def process(text, max_length=None):
    ...
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Modules | snake_case | `text_processor.py` |
| Classes | PascalCase | `TextProcessor` |
| Functions | snake_case | `process_text` |
| Constants | UPPER_SNAKE | `MAX_LENGTH` |
| Private | _leading_underscore | `_internal_method` |

### Docstrings

Use Google style for public APIs:

```python
def rewrite(text: str, style: str = "neutral") -> str:
    """Rewrite text to reduce AI patterns.

    Args:
        text: The input text to rewrite.
        style: Output style - "formal", "casual", or "neutral".

    Returns:
        The rewritten text.

    Raises:
        ValueError: If text is empty.
    """
    ...
```

## Code Organization

### Module Structure
```python
"""Module docstring."""

# Standard library imports
# Third-party imports
# Local imports

# Constants
MAX_LENGTH: Final[int] = 1000

# Public classes
class Rewriter:
    ...

# Public functions
def rewrite(text: str) -> str:
    ...

# Private functions
def _internal_helper(text: str) -> str:
    ...
```

### Class Structure
```python
class Rewriter:
    """Class docstring."""

    # Class attributes
    default_style: ClassVar[str] = "neutral"

    def __init__(self, style: str = "neutral") -> None:
        """Initialize."""
        self._style = style

    # Public methods
    def rewrite(self, text: str) -> str:
        """Rewrite text."""
        ...

    # Private methods
    def _process(self, text: str) -> str:
        ...
```

## Patterns to Follow

### Prefer Composition
```python
# Good
class Rewriter:
    def __init__(self, provider: Provider) -> None:
        self._provider = provider

# Avoid deep inheritance
class SpecializedRewriter(Rewriter):
    ...
```

### Use Dataclasses for Data
```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RewriteResult:
    """Result of a rewrite operation."""

    original: str
    rewritten: str
    tokens_used: int
```

### Use Pydantic for Config
```python
from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings."""

    api_key: str
    model: str = "gpt-4"
    max_tokens: int = 2000
```

## Patterns to Avoid

### No Premature Abstraction
```python
# Bad: Over-abstracted
class TextProcessorFactory:
    def create_processor(self, type: str) -> TextProcessor:
        ...

# Good: Simple and direct
def process_text(text: str) -> str:
    ...
```

### No God Classes
- Keep classes focused on single responsibility
- If class > 300 lines, consider splitting

### No Deep Nesting
```python
# Bad
def process(data: dict) -> str:
    if "text" in data:
        if data["text"]:
            if len(data["text"]) > 0:
                return data["text"]
    return ""

# Good
def process(data: dict) -> str:
    text = data.get("text")
    if not text:
        return ""
    return text
```

## Running Checks

```bash
# Format
uv run ruff format src/

# Lint
uv run ruff check src/
uv run ruff check --fix src/

# Type check
uv run mypy src/

# All checks
uv run ruff check src/ && uv run mypy src/
```