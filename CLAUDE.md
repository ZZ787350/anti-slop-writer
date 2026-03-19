# CLAUDE.md - anti-slop-writer

> Claude-specific guidance for this repository

@AGENTS.md

## Claude-Specific Additions

### Planning
- For significant changes, enter plan mode first to explore and design
- Do not implement across phases — complete the current phase fully
- Update this file if new patterns emerge worth documenting

### Context
- This project is inspired by [anti-slop-writing](https://github.com/adenaufal/anti-slop-writing)
- The goal is a CLI tool, not a library or web service
- English support first; other languages are post-MVP

### Quality Checks
Before marking work complete:
1. Run `uv run ruff check src/ && uv run mypy src/ && uv run pytest`
2. Verify all tests pass
3. Do a manual CLI test if applicable