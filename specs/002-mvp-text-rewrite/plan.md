# Implementation Plan: MVP Text Rewrite Engine

**Branch**: `002-mvp-text-rewrite` | **Date**: 2026-03-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-mvp-text-rewrite/spec.md`

## Summary

Build a CLI-based text rewriting tool that reduces "AI-sounding" patterns in text while preserving meaning and structure. The core rewriting capability is designed as a callable Python module (Library-First), with the CLI as a thin wrapper. The system uses configurable LLM providers via OpenAI-compatible protocol and applies pattern matching against a vocabulary banlist to verify output quality.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: typer (CLI), httpx (HTTP client), pydantic (config/validation), pydantic-settings (settings)
**Storage**: N/A (in-memory processing only)
**Testing**: pytest with pytest-cov
**Target Platform**: WSL2, Linux, macOS (local execution)
**Project Type**: CLI tool with library-first core
**Performance Goals**: <60s timeout per request, max 3 retries, process 5,000 words without degradation
**Constraints**: No persistent storage of user text, API keys via env/config only, no telemetry
**Scale/Scope**: Single-user local tool, 100-5,000 word documents

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. 质量优先 | ✅ PASS | FR-006 conditional threshold ensures measurable quality improvement |
| II. 库优先设计 (Library-First) | ✅ PASS | FR-016 explicitly requires callable core interface; CLI is wrapper |
| III. 模块边界清晰 | ✅ PASS | Dependency direction: Interfaces → Core ← Language Packs, Providers |
| IV. API Key 安全 | ✅ PASS | FR-010: credentials from env vars or config files only |
| V. 数据隐私 | ✅ PASS | FR-014: log metadata only, no text content |
| VI. Core 不依赖 CLI | ✅ PASS | FR-016 verification: import core module directly without CLI |
| VII. Provider 可切换 | ✅ PASS | FR-009: configurable endpoints; OpenAI-compatible protocol |

**Gate Result**: ✅ ALL GATES PASSED - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/002-mvp-text-rewrite/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI contract)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/anti_slop_writer/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── rewriter.py      # Main Rewriter class
│   ├── text_processor.py # Text processing utilities
│   └── rule_engine.py   # Pattern matching engine
├── language_packs/
│   ├── __init__.py
│   └── english.py       # English Pack (MVP)
├── providers/
│   ├── __init__.py
│   ├── base.py          # BaseProvider abstract class
│   └── openai_compatible.py # OpenAI-compatible implementation
└── interfaces/
    ├── __init__.py
    └── cli.py           # Typer CLI entry point

tests/
├── unit/
│   ├── test_rewriter.py
│   ├── test_rule_engine.py
│   └── test_text_processor.py
├── integration/
│   ├── test_cli.py
│   └── test_provider.py
└── conftest.py

references/
├── vocabulary-banlist.md
└── structural-patterns.md
```

**Structure Decision**: Single project with library-first core. The `core/` module contains all business logic with zero external dependencies on CLI or providers. `interfaces/cli.py` is a thin wrapper. `providers/` implements the OpenAI-compatible HTTP client.

## Complexity Tracking

> No constitution violations detected. Table not required.
