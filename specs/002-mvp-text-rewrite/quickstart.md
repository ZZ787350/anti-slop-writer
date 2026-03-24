# Quickstart: MVP Text Rewrite Engine

**Branch**: `002-mvp-text-rewrite` | **Date**: 2026-03-24

## Prerequisites

- Python 3.11+
- uv (recommended) or pip
- LLM API access (OpenAI-compatible endpoint)

---

## Installation

```bash
# Clone and install
git clone https://github.com/your-org/anti-slop-writer.git
cd anti-slop-writer
uv sync

# Or with pip
pip install -e .
```

---

## Configuration

### Step 1: Set API Key

```bash
# Option A: Environment variable (recommended)
export ANTI_SLOP_WRITER_API_KEY="your-api-key-here"

# Option B: Config file
mkdir -p ~/.config/anti-slop-writer
cat > ~/.config/anti-slop-writer/config.toml << EOF
[provider]
endpoint = "https://api.openai.com/v1"
model = "gpt-4o-mini"
EOF
```

### Step 2: Configure Provider (if not using defaults)

For 智谱 GLM:
```bash
export ANTI_SLOP_WRITER_ENDPOINT="https://open.bigmodel.cn/api/paas/v4"
export ANTI_SLOP_WRITER_MODEL="glm-4-flash"
```

For DeepSeek:
```bash
export ANTI_SLOP_WRITER_ENDPOINT="https://api.deepseek.com/v1"
export ANTI_SLOP_WRITER_MODEL="deepseek-chat"
```

---

## Basic Usage

### Rewrite Direct Text

```bash
anti-slop-writer rewrite "In today's fast-paced world, it's crucial to delve into the transformative power of AI."
```

**Expected Output**:
```
AI has changed how we work and live. Let's look at what this means.
```

### Rewrite from File

```bash
# Input file
anti-slop-writer rewrite --input article.txt

# Output to specific file
anti-slop-writer rewrite --input article.txt --output processed.txt

# Output with default naming (article_rewritten.txt)
anti-slop-writer rewrite --input article.txt
```

### Choose Style

```bash
# Formal tone
anti-slop-writer rewrite --style formal "Your text here"

# Casual tone
anti-slop-writer rewrite --style casual "Your text here"

# Neutral (default)
anti-slop-writer rewrite "Your text here"
```

---

## Programmatic Usage (Library)

```python
from anti_slop_writer import Rewriter, ProviderConfig

# Configure
config = ProviderConfig(
    endpoint="https://api.openai.com/v1",
    api_key="sk-your-key",
    model="gpt-4o-mini",
)

# Create rewriter
rewriter = Rewriter(config)

# Rewrite text
result = rewriter.rewrite(
    "In conclusion, it's worth noting that this technology is groundbreaking.",
    style="neutral"
)

# Access results
print(result.rewritten_text)
print(f"Patterns: {result.pattern_count_before} → {result.pattern_count_after}")
print(f"Time: {result.processing_time_ms}ms")
```

---

## Common Workflows

### Batch Processing Multiple Files (Manual)

```bash
for file in drafts/*.txt; do
    anti-slop-writer rewrite --input "$file"
done
```

### Integration with Other Tools

```bash
# Pipe from clipboard (macOS)
pbpaste | anti-slop-writer rewrite -

# Pipe to clipboard
anti-slop-writer rewrite "text" | pbcopy

# Redirect to file
anti-slop-writer rewrite "text" > output.txt
```

---

## Troubleshooting

### "API key not found"

```bash
# Check environment variable
echo $ANTI_SLOP_WRITER_API_KEY

# Or check config file
cat ~/.config/anti-slop-writer/config.toml
```

### "Request timed out"

```bash
# Increase timeout in config
[rewrite]
timeout = 120  # seconds
```

### "Authentication failed"

1. Verify API key is correct
2. Check endpoint URL matches your provider
3. Ensure API key has credits/access

---

## Verification

Run the test suite to verify installation:

```bash
uv run pytest
```

Expected output: All tests pass, coverage ≥ 80%

---

## Next Steps

1. Review `references/vocabulary-banlist.md` for pattern details
2. Customize `~/.config/anti-slop-writer/config.toml` for your workflow
3. See [contracts/cli.md](./contracts/cli.md) for full CLI reference