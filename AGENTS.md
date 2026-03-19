# AGENTS.md - anti-slop-writer

> Repository-level specification for AI coding agents

## Project Overview

**anti-slop-writer** is a CLI-based text rewriting tool that reduces "AI-sounding" patterns in text. It takes input text and rewrites it to sound more human and natural while preserving the original meaning.

**Core Value**: Output quality over everything — natural phrasing, reduced AI patterns, preserved meaning, complete structure.

**Target Users**: Content creators, academic workers, individual developers.

---

## Repository Structure

```
anti-slop-writer/
├── src/
│   └── anti_slop_writer/       # Main package
│       ├── core/               # Core rewriting logic
│       ├── language_packs/     # Language-specific rules
│       ├── providers/          # LLM provider integrations
│       └── interfaces/         # CLI and API interfaces
├── tests/                      # Test suite
├── references/                 # Reference documentation
│   ├── vocabulary-banlist.md   # Banned AI phrases
│   └── structural-patterns.md  # Patterns to avoid
├── AGENTS.md                   # This file
├── CLAUDE.md                   # Claude-specific guidance
├── PRODUCT.md                  # Product specification
├── ARCHITECTURE.md             # Architecture documentation
└── pyproject.toml              # Project configuration
```

---

## Module Boundaries

### Core (`src/anti_slop_writer/core/`)
- **Responsibility**: Text processing pipeline, rule application, output formatting
- **Dependencies**: None (pure logic)
- **Exports**: Rewriter class, TextProcessor, RuleEngine

### Language Packs (`src/anti_slop_writer/language_packs/`)
- **Responsibility**: Language-specific vocabulary bans, structural rules, discourse markers
- **Dependencies**: None (configuration/data only)
- **Exports**: EnglishPack (MVP), future: ChinesePack, IndonesianPack

### Providers (`src/anti_slop_writer/providers/`)
- **Responsibility**: LLM API integrations, authentication, response handling
- **Dependencies**: External SDKs (openai, anthropic, etc.)
- **Exports**: BaseProvider, OpenAIProvider, AnthropicProvider

### Interfaces (`src/anti_slop_writer/interfaces/`)
- **Responsibility**: CLI entry point, argument parsing, user interaction
- **Dependencies**: Core, Providers, typer
- **Exports**: CLI commands, main entry point

### Dependency Direction
```
Interfaces → Core ← Language Packs
    ↓
Providers
```

**Rules**:
- Core never imports from Interfaces
- Language Packs never import from Core
- Providers never import from Core

---

## Commands

### Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/anti_slop_writer

# Type check
uv run mypy src/

# Lint and format
uv run ruff check src/
uv run ruff format src/

# Run all checks
uv run ruff check src/ && uv run mypy src/ && uv run pytest
```

### CLI Usage (post-install)

```bash
# Basic rewrite
anti-slop-writer rewrite "Your text here"

# From file
anti-slop-writer rewrite --input article.txt

# With specific provider
anti-slop-writer rewrite --provider openai "Your text"

# Specify output style
anti-slop-writer rewrite --style formal "Your text"
```

---

## Done Definition

A feature is complete when:

1. **Tests Pass**: All new and existing tests pass (`uv run pytest`)
2. **Type Check Passes**: No mypy errors (`uv run mypy src/`)
3. **Lint Passes**: No ruff errors (`uv run ruff check src/`)
4. **Coverage Maintained**: Test coverage ≥ 80% for new code
5. **Documentation Updated**: Docstrings for all public functions/classes
6. **CLI Works**: Manual test of CLI command succeeds
7. **No Regressions**: Rewriting quality maintained (manual spot-check)

---

## Constraints

### Technical Constraints
- **Python Version**: 3.11+ (for `tomllib` and modern type hints)
- **No External TOML Parser**: Use built-in `tomllib`
- **CLI Framework**: typer (with click compatibility)

### MVP Scope (Do Not Add)
- Chinese language support
- Web frontend
- Cloud/hosted service
- User accounts
- Batch processing API
- Plugin system

### Security
- Never log or store user text content
- API keys only via environment variables or config files
- No telemetry or usage tracking
- Validate all user inputs before processing

### Code Style
- Use ruff for formatting (line length: 88)
- Use mypy in strict mode
- Prefer composition over inheritance
- No premature abstraction

---

## Rules Reference

For detailed rules, see:

- `references/vocabulary-banlist.md` — Words and phrases to ban
- `references/structural-patterns.md` — Sentence patterns to avoid
- `.claude/rules/testing.md` — Testing requirements
- `.claude/rules/python.md` — Python code standards
- `.claude/rules/security.md` — Security requirements

---

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Python Version | 3.11+ | Built-in TOML, modern type hints |
| CLI Framework | typer | Type-hint driven, auto docs |
| Test Framework | pytest | Best ecosystem, plugin support |
| Linter/Formatter | ruff | Fast, replaces flake8/black/isort |
| Type Checker | mypy | Industry standard |
| License | Apache 2.0 (future) | Permissive, enterprise-friendly |

---

## Agent Instructions

When working on this codebase:

1. **Read before editing**: Understand the module structure first
2. **Follow module boundaries**: Respect dependency direction
3. **Write tests first**: New features need tests before implementation
4. **Check done definition**: Verify all criteria before marking complete
5. **No scope creep**: MVP only — defer non-essential features