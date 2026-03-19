# Testing Rules - anti-slop-writer

> Test requirements and guidelines

## Test Framework

- **Framework**: pytest
- **Coverage target**: ≥80% for new code
- **Location**: `tests/` directory mirroring `src/` structure

## Test Requirements

### Unit Tests
- Every public function/method needs at least one test
- Test both success and error cases
- Use descriptive test names: `test_<function>_<scenario>_<expected>`

### Integration Tests
- Required for provider integrations
- Use mocking for external API calls
- Test error handling and retries

## Test Structure

```python
class TestClassName:
    """Tests for ClassName."""

    def test_method_scenario_expected(self) -> None:
        """Test description of what's being tested."""
        # Arrange
        ...

        # Act
        ...

        # Assert
        ...
```

## Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=src/anti_slop_writer

# Specific file
uv run pytest tests/test_rewriter.py

# Verbose
uv run pytest -v
```

## Test Coverage

### Must Have Coverage
- Core rewriting logic
- Rule engine
- Provider implementations
- CLI commands

### Acceptable Gaps
- Error messages (strings)
- Debug logging
- Private helper methods (if trivial)

## Fixtures

Use `tests/conftest.py` for shared fixtures:

```python
import pytest

from anti_slop_writer.core import Rewriter


@pytest.fixture
def rewriter() -> Rewriter:
    """Provide a default Rewriter instance."""
    return Rewriter()
```

## Mocking External APIs

Always mock LLM API calls:

```python
from unittest.mock import patch


def test_rewrite_with_mocked_api(rewriter: Rewriter) -> None:
    """Test rewriting with mocked LLM response."""
    with patch("anti_slop_writer.providers.openai.OpenAIProvider.call") as mock:
        mock.return_value = "Rewritten text"
        result = rewriter.rewrite("Original text")
        assert result == "Rewritten text"
```

## Done Definition for Tests

A feature's tests are complete when:
- [ ] All public APIs have tests
- [ ] Edge cases are covered
- [ ] Error paths are tested
- [ ] Coverage ≥80%
- [ ] All tests pass