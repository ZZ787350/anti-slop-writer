# Security Rules - anti-slop-writer

> Security requirements and guidelines

## Core Principles

1. **No data storage**: User text is processed in-memory only
2. **No telemetry**: No usage tracking or analytics
3. **API key safety**: Keys via environment or config, never in code

## Data Handling

### Text Processing
- Process text in-memory only
- Never log user text content
- Never write user text to disk
- Clear sensitive data from memory after use

### Logging
```python
# Good: Log metadata only
logger.info("Processing text", length=len(text))

# Bad: Log actual content
logger.info("Processing text", content=text)
```

## API Key Management

### Allowed
- Environment variables
- Config files with restricted permissions
- System keyring (future)

### Forbidden
- Hardcoded keys
- Keys in command-line arguments
- Keys in log files
- Keys in error messages

### Configuration
```python
# Good: Load from environment
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    class Config:
        env_file = ".env"
```

```bash
# Good: Environment variable
export OPENAI_API_KEY="sk-..."

# Good: .env file (not committed)
OPENAI_API_KEY=sk-...
```

## Input Validation

### Validate All User Input
```python
def rewrite(text: str, max_length: int = 10000) -> str:
    """Rewrite text with validation."""
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if len(text) > max_length:
        raise ValueError(f"Text exceeds maximum length of {max_length}")

    # Sanitize: remove control characters
    text = "".join(c for c in text if c.isprintable() or c in "\n\t")

    return _do_rewrite(text)
```

### File Path Validation
```python
import os
from pathlib import Path


def read_file(path: str) -> str:
    """Read file with path validation."""
    file_path = Path(path).resolve()

    # Ensure within allowed directory
    if not str(file_path).startswith(os.getcwd()):
        raise ValueError("File path must be within project directory")

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return file_path.read_text()
```

## Error Handling

### Don't Leak Information
```python
# Good: Generic error message
except httpx.HTTPStatusError:
    raise ProviderError("API request failed")

# Bad: Exposes internal details
except httpx.HTTPStatusError as e:
    raise ProviderError(f"API request failed: {e.response.text}")
```

### Safe Exception Messages
```python
class RewriteError(Exception):
    """Base error for rewrite operations."""

    def __init__(self, message: str) -> None:
        # Sanitize message before storing
        safe_message = message.replace("\n", " ")[:200]
        super().__init__(safe_message)
```

## Dependencies

### Dependency Selection
- Check for known vulnerabilities
- Prefer well-maintained packages
- Minimize dependency count

### Version Pinning
```toml
# pyproject.toml
dependencies = [
    "typer>=0.12.0,<1.0.0",  # Allow minor updates, not major
    "httpx>=0.27.0",
]
```

## Network Security

### HTTPS Only
```python
# Good: HTTPS
httpx.Client(base_url="https://api.openai.com")

# Bad: HTTP
httpx.Client(base_url="http://api.openai.com")
```

### Timeout Configuration
```python
# Always set timeouts
httpx.Client(timeout=httpx.Timeout(30.0, connect=5.0))
```

## Security Checklist

Before release, verify:

- [ ] No hardcoded credentials
- [ ] No user data in logs
- [ ] All inputs validated
- [ ] All network calls use HTTPS
- [ ] Timeouts set on all network calls
- [ ] Error messages don't leak info
- [ ] .env in .gitignore
- [ ] Dependencies checked for vulnerabilities