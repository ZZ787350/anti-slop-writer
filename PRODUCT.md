# PRODUCT.md - anti-slop-writer

> Product specification document

## Product Overview

**anti-slop-writer** is a command-line tool that rewrites text to reduce recognizable AI writing patterns. It produces more natural, human-sounding text while preserving the original meaning.

## Problem Statement

AI-generated text has become detectable through:
- Predictable vocabulary choices (significance puffers, analytical verbs)
- Formulaic sentence structures
- Uniform sentence lengths and rhythm
- Hedging and vague attributions

This creates problems for:
- Content creators wanting authentic voice
- Academic writers needing natural prose
- Developers documenting projects

## Solution

A CLI tool that:
1. Takes input text (string or file)
2. Processes it through an LLM with anti-AI-pattern rules
3. Outputs rewritten text that sounds more human

## Target Users

| User Type | Use Case |
|-----------|----------|
| Content creators | Blog posts, social media, newsletters |
| Academic workers | Papers, research summaries, proposals |
| Individual developers | Documentation, README files, comments |

## MVP Scope

### Included
- English language support
- CLI interface
- OpenAI-compatible provider support
- Core rewriting functionality
- Basic style options (formal, casual)

### Excluded (Post-MVP)
- Chinese language support
- Web frontend
- Cloud/hosted service
- User accounts
- Batch processing API
- Plugin system

## Success Criteria

1. **Quality**: Rewritten text passes AI detection at higher rates
2. **Usability**: Single command to rewrite text
3. **Reliability**: Preserves original meaning in >95% of cases
4. **Speed**: Processes 1000 words in under 30 seconds

## Out of Scope

- Machine learning model training
- Real-time collaboration
- Mobile applications
- Enterprise features (SSO, audit logs)

## Future Considerations

- Additional language packs (Chinese, Indonesian, etc.)
- HTTP API wrapper
- Editor integrations (VS Code, Neovim)
- Custom rule sets