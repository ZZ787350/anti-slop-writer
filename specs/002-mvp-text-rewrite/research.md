# Research: MVP Text Rewrite Engine

**Branch**: `002-mvp-text-rewrite` | **Date**: 2026-03-24

## Research Items

### 1. LLM Provider Integration Pattern

**Decision**: Use httpx with async support for OpenAI-compatible API calls

**Rationale**:
- httpx is already a common dependency for async HTTP in Python
- OpenAI-compatible protocol is widely supported (智谱 GLM, DeepSeek, OpenAI)
- Async support enables future batch processing without blocking
- Simpler than maintaining multiple provider SDKs

**Alternatives Considered**:
- `openai` SDK: Rejected - locks to OpenAI-specific features, adds unnecessary dependency
- `httpx` with sync only: Rejected - limits future extensibility
- Multiple SDKs per provider: Rejected - increases maintenance burden, violates Constitution VII

**Implementation Notes**:
- Use `httpx.AsyncClient` with configurable `base_url` and `timeout`
- Standard `/v1/chat/completions` endpoint
- API key via `Authorization: Bearer` header

---

### 2. Pattern Matching Strategy

**Decision**: Compile vocabulary banlist to regex patterns at runtime

**Rationale**:
- `vocabulary-banlist.md` contains ~100 phrases across 8 categories
- Regex compilation provides O(1) lookup after initial compile
- Case-insensitive matching handles natural text variation
- Tier 1 (hard ban) vs Tier 2 (soft guidance) distinction preserved

**Alternatives Considered**:
- Simple string search: Rejected - misses case variations, word boundaries
- spaCy NLP: Rejected - adds heavy dependency for simple matching
- Trie structure: Rejected - over-engineering for ~100 patterns

**Implementation Notes**:
```python
# Example structure
PATTERNS = {
    "tier1": re.compile(r"\b(delve|leverage|embark)\b", re.IGNORECASE),
    "tier2": re.compile(r"\b(furthermore|moreover)\b", re.IGNORECASE),
}
```

---

### 3. Prompt Engineering for Rewriting

**Decision**: Use structured system prompt with vocabulary constraints

**Rationale**:
- LLM needs explicit guidance on what patterns to avoid
- System prompt sets global behavior, user prompt contains text
- Include examples of "before/after" transformations
- Specify style parameter (formal/casual/neutral) in prompt

**Alternatives Considered**:
- Few-shot examples only: Rejected - inconsistent behavior
- Fine-tuned model: Rejected - out of MVP scope
- Post-processing only: Rejected - can't fix structural AI patterns

**Prompt Template Structure**:
```
System: You are a text editor that removes AI-sounding language.
Avoid these patterns: [tier1 list]
Use simpler alternatives: [tier2 replacements]
Style: {style}

User: Rewrite this text to sound more natural:
{text}
```

---

### 4. Error Handling & Retry Strategy

**Decision**: Exponential backoff with max 3 retries, 60s timeout

**Rationale**:
- Matches FR-011 specification (clarified in Session 2026-03-20)
- Exponential backoff prevents thundering herd on API recovery
- 60s timeout accommodates slow LLM responses for long texts
- Non-retryable errors (401, 400) fail immediately

**Retry Configuration**:
```python
retry_config = {
    "max_retries": 3,
    "timeout": 60.0,
    "retry_on": [408, 429, 500, 502, 503, 504],
    "backoff_factor": 2.0,  # 1s, 2s, 4s
}
```

---

### 5. Configuration Management

**Decision**: Pydantic Settings with environment variable + TOML file support

**Rationale**:
- `pydantic-settings` provides type-safe configuration
- Environment variables for secrets (API keys)
- TOML file for non-secret defaults (model, endpoint)
- Follows Constitution IV (API Key 安全)

**Configuration Hierarchy** (priority high to low):
1. Environment variables (`ANTI_SLOP_WRITER_API_KEY`)
2. Config file (`~/.config/anti-slop-writer/config.toml`)
3. Built-in defaults

**Config File Example**:
```toml
[provider]
endpoint = "https://open.bigmodel.cn/api/paas/v4"
model = "glm-4-flash"

[rewrite]
style = "neutral"
max_retries = 3
timeout = 60
```

---

### 6. CLI Framework Integration

**Decision**: Typer with rich formatting for better UX

**Rationale**:
- AGENTS.md specifies typer as CLI framework
- Rich integration provides colored output, progress indicators
- Type hints drive automatic argument parsing
- Consistent with project's Python-first approach

**CLI Structure**:
```python
app = typer.Typer()

@app.command()
def rewrite(
    text: str | None = typer.Argument(None),
    input_file: Path | None = typer.Option(None, "--input", "-i"),
    output: Path | None = typer.Option(None, "--output", "-o"),
    style: str = typer.Option("neutral", "--style", "-s"),
) -> None:
    ...
```

---

### 7. Output File Naming

**Decision**: `{input_filename}_rewritten.{extension}` in same directory

**Rationale**:
- Clarified in Session 2026-03-20 (Option A)
- Preserves original filename for context
- Suffix before extension is common convention (e.g., `draft_rewritten.txt`)
- Easy to identify processed files

**Examples**:
- `article.txt` → `article_rewritten.txt`
- `my-draft.md` → `my-draft_rewritten.md`

---

## Open Questions Resolution

| Question | Status | Resolution |
|----------|--------|------------|
| Q003 (Retry Strategy) | ✅ Resolved | Exponential backoff, max 3 retries, 60s timeout |
| Q007 (AI Taste Quantification) | ⏸️ Deferred | Using FR-006 conditional threshold; percentage target post-MVP |

---

## Dependencies Summary

| Package | Version | Purpose |
|---------|---------|---------|
| typer | >=0.12.0 | CLI framework |
| rich | >=13.0.0 | Terminal formatting (typer dependency) |
| httpx | >=0.27.0 | Async HTTP client |
| pydantic | >=2.0.0 | Data validation |
| pydantic-settings | >=2.0.0 | Configuration management |
| pytest | >=8.0.0 | Testing (dev) |
| pytest-cov | >=5.0.0 | Coverage (dev) |
| pytest-asyncio | >=0.23.0 | Async test support (dev) |
