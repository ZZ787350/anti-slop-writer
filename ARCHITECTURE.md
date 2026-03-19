# ARCHITECTURE.md - anti-slop-writer

> Technical architecture documentation

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                      CLI Interface                       │
│                    (interfaces/cli.py)                   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Core Pipeline                         │
│              (core/rewriter.py, core/processor.py)       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Text Input  │→ │ Rule Engine │→ │ LLM Client  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌───────────┐    ┌───────────┐    ┌───────────┐
    │ Language  │    │  Provider │    │References │
    │   Packs   │    │    SDKs   │    │  (Rules)  │
    └───────────┘    └───────────┘    └───────────┘
```

## Module Design

### Core Module (`core/`)

**Responsibility**: Orchestrate the rewriting pipeline

```
core/
├── __init__.py
├── rewriter.py      # Main Rewriter class
├── processor.py     # Text preprocessing/postprocessing
├── rule_engine.py   # Apply language rules
└── prompts.py       # LLM prompt templates
```

### Language Packs (`language_packs/`)

**Responsibility**: Language-specific configuration

```
language_packs/
├── __init__.py
├── base.py          # BasePack abstract class
└── english.py       # English language rules (MVP)
```

Each pack provides:
- Vocabulary ban list
- Structural pattern rules
- Discourse markers
- Register shift suggestions

### Providers (`providers/`)

**Responsibility**: LLM API abstraction

```
providers/
├── __init__.py
├── base.py          # BaseProvider abstract class
├── openai.py        # OpenAI implementation
└── anthropic.py     # Anthropic implementation
```

### Interfaces (`interfaces/`)

**Responsibility**: User interaction layer

```
interfaces/
├── __init__.py
└── cli.py           # Typer CLI commands
```

## Data Flow

```
Input Text
    │
    ▼
┌─────────────────┐
│   Preprocess    │  Clean, normalize, segment
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Load Rules     │  Language pack → Rule set
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Build Prompt   │  Text + Rules → Prompt
└─────────────────┘
    │
    ▼
┌─────────────────┐
│   Call LLM      │  Provider API request
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Postprocess    │  Validate, format output
└─────────────────┘
    │
    ▼
Output Text
```

## Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | Python 3.11+ | TOML built-in, modern types |
| CLI | typer | Type-driven, auto docs |
| HTTP | httpx | Async support, modern |
| Config | pydantic | Validation, settings |
| Testing | pytest | Ecosystem, plugins |
| Linting | ruff | Fast, all-in-one |
| Typing | mypy | Strict mode |

## Deployment

**Target**: Local CLI tool

**Distribution**:
- PyPI package (future)
- Direct clone + uv install (MVP)

**Requirements**:
- Python 3.11+
- LLM API key (OpenAI or Anthropic)

## Security Model

1. **No Data Storage**: Text is processed in-memory only
2. **API Keys**: Environment variables or config file (not in code)
3. **No Telemetry**: No usage tracking or analytics
4. **Input Validation**: Sanitize all user inputs

## Future Architecture

Post-MVP considerations:

```
Phase 2: Chinese Language Pack
├── language_packs/chinese.py
└── Update rule engine for CJK handling

Phase 3: HTTP API
├── interfaces/api.py
└── FastAPI wrapper

Phase 4: Editor Plugins
├── editors/vscode/
└── editors/neovim/
```

## Design Decisions

| Decision | Choice | Alternatives Considered |
|----------|--------|------------------------|
| CLI-first | Yes | Library-first, API-first |
| Sync I/O | MVP | Async (post-MVP) |
| Single output | MVP | Multiple style variants |
| Rule file format | Markdown | JSON, YAML, TOML |