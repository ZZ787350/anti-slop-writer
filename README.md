# anti-slop-writer

A CLI tool that rewrites text to reduce "AI-sounding" patterns. Makes text more human and natural while preserving original meaning.

Based on research into AI writing detection and the [anti-slop-writing](https://github.com/adenaufal/anti-slop-writing) project.

## Why?

AI-generated text has recognizable patterns:
- Overused vocabulary ("pivotal", "crucial", "tapestry")
- Formulaic structures (Rule of Three, staccato triplets)
- Predictable sentence lengths
- Hedging and vague attributions

anti-slop-writer rewrites text to break these patterns.

## Before vs After

**Input:**
> The festival serves as a vibrant testament to the region's rich cultural heritage, showcasing the intricate tapestry of traditions that have endured through the ages, contributing to the broader social fabric of the community.

**Output:**
> The festival has run every April since 1987. Locals build their own stalls. The goat cheese and handmade pottery sell out by noon.

## Installation

```bash
# Clone and install
git clone https://github.com/yourname/anti-slop-writer.git
cd anti-slop-writer
uv sync
```

## Quick Start

```bash
# Basic rewrite
uv run anti-slop-writer rewrite "Your text here"

# From file
uv run anti-slop-writer rewrite --input article.txt

# Specify output style
uv run anti-slop-writer rewrite --style formal "Your text"
```

## Configuration

Set your LLM provider API key:

```bash
export OPENAI_API_KEY="your-key"
# or
export ANTHROPIC_API_KEY="your-key"
```

## Documentation

- [PRODUCT.md](PRODUCT.md) — Product specification
- [ARCHITECTURE.md](ARCHITECTURE.md) — Technical architecture
- [CONTRIBUTING.md](CONTRIBUTING.md) — Development guide

## License

Apache 2.0 (planned)