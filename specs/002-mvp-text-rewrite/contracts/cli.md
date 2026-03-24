# CLI Contract: anti-slop-writer

**Version**: 1.0.0 (MVP)
**Interface Type**: Command Line Interface
**Entry Point**: `anti-slop-writer` (installed via pip/uv)

---

## Commands

### `rewrite` - Rewrite text to reduce AI patterns

**Synopsis**:
```bash
anti-slop-writer rewrite [TEXT] [OPTIONS]
```

**Description**:
Takes input text and rewrites it to sound more natural and human-like by reducing AI-typical vocabulary patterns. The core rewriting is performed by an LLM via a configurable provider.

---

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| TEXT | string | Conditional | Text to rewrite (mutually exclusive with `--input`) |

---

## Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--input` | `-i` | PATH | - | Read text from file |
| `--output` | `-o` | PATH | - | Write output to file (default: stdout) |
| `--style` | `-s` | TEXT | neutral | Output style: neutral, formal, casual |
| `--provider` | `-p` | TEXT | default | Provider config name |
| `--help` | `-h` | - | - | Show help message |

---

## Exit Codes

| Code | Meaning | Example Cause |
|------|---------|---------------|
| 0 | Success | Text rewritten successfully |
| 1 | Input Error | Empty text, file not found, invalid style |
| 2 | Configuration Error | Missing API key, invalid endpoint |
| 3 | Provider Error | API authentication failed, rate limited |
| 4 | Network Error | Timeout after retries, connection refused |
| 5 | Processing Error | Malformed API response, internal error |

---

## Input Modes

### Mode 1: Direct Text
```bash
anti-slop-writer rewrite "This is my AI-generated text that needs rewriting."
```

### Mode 2: File Input (stdout output)
```bash
anti-slop-writer rewrite --input article.txt
```

### Mode 3: File Input → File Output
```bash
anti-slop-writer rewrite --input article.txt --output article_rewritten.txt
# Or rely on default naming:
anti-slop-writer rewrite --input article.txt --output article_rewritten.txt
# When --output omitted: creates article_rewritten.txt
```

---

## Output Behavior

| Scenario | Output Location | Default Filename |
|----------|-----------------|------------------|
| Text argument only | stdout | N/A |
| `--input` only | stdout | N/A |
| `--input` + `--output` | specified file | as specified |
| `--input` only + file output flag | same directory | `{input}_rewritten.{ext}` |

**File Output Examples**:
- `article.txt` → `article_rewritten.txt`
- `my-draft.md` → `my-draft_rewritten.md`
- `document` → `document_rewritten`

---

## Error Messages

### Input Errors (Exit 1)
```
Error: Input text cannot be empty
Error: File not found: /path/to/missing.txt
Error: Invalid style 'unknown'. Must be: neutral, formal, casual
```

### Configuration Errors (Exit 2)
```
Error: API key not found. Set ANTI_SLOP_WRITER_API_KEY or configure in config.toml
Error: Invalid endpoint URL: not-a-url
```

### Provider Errors (Exit 3)
```
Error: Authentication failed. Check your API key.
Error: Rate limited. Please wait and try again.
```

### Network Errors (Exit 4)
```
Error: Request timed out after 3 retries.
Error: Could not connect to API endpoint.
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTI_SLOP_WRITER_API_KEY` | Yes* | API key for LLM provider |
| `ANTI_SLOP_WRITER_ENDPOINT` | No | Override default endpoint |
| `ANTI_SLOP_WRITER_MODEL` | No | Override default model |

*Required unless configured in config file.

---

## Configuration File

**Location**: `~/.config/anti-slop-writer/config.toml`

**Schema**:
```toml
[provider]
endpoint = "https://api.openai.com/v1"
model = "gpt-4o-mini"
api_key = ""  # Prefer environment variable

[rewrite]
style = "neutral"
max_retries = 3
timeout = 60
```

---

## Library Interface (FR-016)

The CLI wraps a callable Python module. Direct usage:

```python
from anti_slop_writer import Rewriter, RewriteRequest, ProviderConfig

config = ProviderConfig(
    endpoint="https://api.openai.com/v1",
    api_key="sk-...",
)

rewriter = Rewriter(config)
result = rewriter.rewrite("Your text here", style="neutral")

print(result.rewritten_text)
print(f"Patterns reduced: {result.pattern_count_before} → {result.pattern_count_after}")
```

**Contract Guarantees**:
- No CLI dependency required
- No subprocess spawning
- All core functionality accessible via Python API
- Same validation and error handling as CLI

---

## Versioning

The CLI follows semantic versioning:
- `--version` flag shows current version
- Breaking changes require major version bump
- New options are backwards compatible
