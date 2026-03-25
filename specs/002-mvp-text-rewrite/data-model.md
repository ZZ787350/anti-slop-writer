# Data Model: MVP Text Rewrite Engine

**Branch**: `002-mvp-text-rewrite` | **Date**: 2026-03-24

## Core Entities

### RewriteRequest

Represents a user's request to rewrite text.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | str | Yes* | Input text to rewrite (*mutually exclusive with file_path) |
| file_path | Path \| None | No | Path to input file (alternative to text) |
| style | str | No | Output style: "neutral" (default), "formal", "casual" |
| output_path | Path \| None | No | Output file path (default: stdout) |

**Validation Rules**:
- Exactly one of `text` or `file_path` must be provided
- If `file_path` provided, file must exist and be readable
- `text` must be non-empty after stripping whitespace
- `style` must be one of: "neutral", "formal", "casual"

**State Transitions**: N/A (immutable request object)

---

### RewriteResult

Represents the outcome of a rewrite operation.

| Field | Type | Description |
|-------|------|-------------|
| original_text | str | The input text (not logged, not stored) |
| rewritten_text | str | The processed output |
| pattern_count_before | int | Number of AI patterns found in input |
| pattern_count_after | int | Number of AI patterns in output |
| processing_time_ms | int | Time taken for LLM call |
| style_used | str | The style applied |

**Computed Properties**:
- `pattern_reduction`: `pattern_count_before - pattern_count_after`
- `meets_threshold`: Boolean based on FR-006 conditional rules

---

### LanguagePack (Abstract)

Contains language-specific rules for pattern detection.

| Field | Type | Description |
|-------|------|-------------|
| language_code | str | ISO 639-1 code (e.g., "en") |
| tier1_patterns | list[Pattern] | Hard-ban patterns (must not appear in output) |
| tier2_patterns | list[Pattern] | Soft-guidance patterns (should be reduced) |
| style_prompts | dict[str, str] | Style-specific prompt modifiers |

**Pattern Structure**:
```python
@dataclass
class Pattern:
    regex: re.Pattern  # Compiled regex
    category: str      # e.g., "significance_puffers"
    replacement: str | None  # Suggested alternative (for tier2)
```

---

### EnglishPack (LanguagePack Implementation)

MVP implementation of LanguagePack for English.

| Field | Value |
|-------|-------|
| language_code | "en" |
| tier1_patterns | Compiled from `references/vocabulary-banlist.md` sections: Significance Puffers, Poetic Nouns, Promotional Adjectives, Opening/Closing Crutches |
| tier2_patterns | Compiled from: Analytical Verbs, Formal Connectives, Puffery Adverbs |
| style_prompts | See below |

**style_prompts values**:

```python
style_prompts = {
    "formal": (
        "Use complete sentences and avoid contractions. "
        "Prefer precise, professional vocabulary. "
        "Maintain an objective, third-person tone where appropriate."
    ),
    "casual": (
        "Use contractions freely (e.g., it's, don't, we're). "
        "Keep sentences short and conversational. "
        "Write as if speaking directly to the reader."
    ),
    "neutral": "",  # No additional instruction; LLM uses default register
}
```

**Source of Truth**: `references/vocabulary-banlist.md`

---

### ProviderConfig

Configuration for connecting to an LLM service.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| endpoint | str | Yes | API base URL (e.g., "https://api.openai.com/v1") |
| api_key | str | Yes | API key (from env or config file) |
| model | str | No | Model identifier (default: "gpt-4o-mini") |
| max_retries | int | No | Max retry attempts (default: 3) |
| timeout | float | No | Request timeout in seconds (default: 60.0) |

**Validation Rules**:
- `endpoint` must be valid HTTPS URL
- `api_key` must be non-empty
- `max_retries` must be 0-5
- `timeout` must be 1-300

**Security**: `api_key` is never logged or serialized

---

### RewriteContext

Runtime context passed through the rewrite pipeline.

| Field | Type | Description |
|-------|------|-------------|
| request | RewriteRequest | The user's request |
| config | ProviderConfig | Provider configuration |
| language_pack | LanguagePack | Language-specific rules |

**Usage**: Created at CLI entry, passed to Rewriter, contains all necessary context for processing.

---

## Entity Relationships

```
RewriteRequest ──┐
                 │
ProviderConfig ──┼──► RewriteContext ──► Rewriter ──► RewriteResult
                 │
LanguagePack ────┘
```

**Direction**:
- `Rewriter` depends on `RewriteContext` (composition)
- `RewriteContext` depends on `RewriteRequest`, `ProviderConfig`, `LanguagePack` (composition)
- `EnglishPack` implements `LanguagePack` (inheritance/interface)
- No circular dependencies

---

## Data Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  CLI Arguments  │────►│ RewriteRequest   │────►│ RewriteContext  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
                        ┌──────────────────┐           │
                        │ ProviderConfig   │───────────┤
                        │ (env/config)     │           │
                        └──────────────────┘           │
                                                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ vocabulary-     │────►│ EnglishPack      │────►│ Rewriter        │
│ banlist.md      │     └──────────────────┘     └─────────────────┘
└─────────────────┘                                      │
                                                         ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ LLM API         │────►│ Raw LLM Response │────►│ RewriteResult   │
│ (external)      │     └──────────────────┘     └─────────────────┘
└─────────────────┘                                      │
                                                         ▼
                                                 ┌─────────────────┐
                                                 │ Output (stdout  │
                                                 │ or file)        │
                                                 └─────────────────┘
```

---

## Validation Rules Summary

| Entity | Validation | Error Code |
|--------|------------|------------|
| RewriteRequest.text | Non-empty after strip | `EMPTY_TEXT` |
| RewriteRequest.file_path | File exists and readable | `FILE_NOT_FOUND` |
| RewriteRequest.style | In ["neutral", "formal", "casual"] | `INVALID_STYLE` |
| ProviderConfig.endpoint | Valid HTTPS URL | `INVALID_ENDPOINT` |
| ProviderConfig.api_key | Non-empty | `MISSING_API_KEY` |
| RewriteResult | FR-006 threshold check | N/A (warning only) |
