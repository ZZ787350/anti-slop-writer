# Feature Specification: MVP Text Rewrite Engine

**Feature Branch**: `002-mvp-text-rewrite`
**Created**: 2026-03-20
**Status**: Ready for Planning
**Input**: User description: "MVP text rewriting capability to reduce AI-sounding patterns"

## Clarifications

### Session 2026-03-20

- Q: What is the maximum number of retries and request timeout for LLM API calls? → A: Max 3 retries, 60s timeout
- Q: When rewriting `draft.txt` without specifying output path, what should the output filename be? → A: `draft_rewritten.txt` (suffix before extension)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Text Rewriting (Priority: P1)

A content creator has drafted an article using an AI assistant and wants to reduce obvious "AI-sounding" language before publishing. They provide their text to the tool and receive a rewritten version that sounds more natural and human-like while preserving the original meaning and structure.

**Why this priority**: This is the core value proposition - without this capability, the tool has no purpose. It's the minimum viable feature that delivers immediate user value.

**Independent Test**: Can be fully tested by providing sample AI-generated text and verifying the output contains fewer AI-typical phrases while maintaining semantic equivalence.

**Acceptance Scenarios**:

1. **Given** a user has AI-generated text containing phrases like "delve into", "it's worth noting", and "in conclusion", **When** they run the rewrite command, **Then** the output replaces these phrases with more natural alternatives
2. **Given** a user provides a 500-word article, **When** they run the rewrite command, **Then** the output maintains the same paragraph structure and key information
3. **Given** a user provides empty text, **When** they run the rewrite command, **Then** they receive a clear error message indicating text cannot be empty

---

### User Story 2 - File-Based Processing (Priority: P2)

An academic worker has a research paper draft in a file that was refined with AI assistance. They want to process the entire file and save the rewritten version without manually copying and pasting content.

**Why this priority**: File I/O significantly improves workflow efficiency for longer documents, but users can still use the tool with direct text input if this isn't available.

**Independent Test**: Can be fully tested by providing a file path as input and verifying a new file is created with rewritten content.

**Acceptance Scenarios**:

1. **Given** a user has a file `draft.txt` with AI-generated content, **When** they run the rewrite command with the file path (no output path specified), **Then** a new file `draft_rewritten.txt` is created in the same directory
2. **Given** a user specifies a non-existent file path, **When** they run the rewrite command, **Then** they receive a clear error message indicating the file was not found
3. **Given** a user specifies an output path, **When** they run the rewrite command, **Then** the rewritten content is saved to the specified location

---

### User Story 3 - Style Selection (Priority: P3)

A developer wants to rewrite technical documentation to sound more formal, while a blogger wants their content to sound more casual. Both users want to choose the appropriate output tone for their audience.

**Why this priority**: Style selection adds customization value, but the default neutral style handles most use cases adequately.

**Independent Test**: Can be fully tested by running rewrite with different style options and verifying the output tone matches the selected style.

**Acceptance Scenarios**:

1. **Given** a user specifies formal style, **When** they run the rewrite command, **Then** the output uses more formal language patterns
2. **Given** a user specifies casual style, **When** they run the rewrite command, **Then** the output uses more conversational language patterns
3. **Given** a user does not specify a style, **When** they run the rewrite command, **Then** the output uses the default neutral style

---

### User Story 4 - Provider Configuration (Priority: P3)

A user has access to multiple LLM providers that support standard API protocols. They want to configure which provider powers the rewriting based on cost, availability, or quality preferences.

**Why this priority**: Provider configuration enables user choice, but a single default provider configuration is sufficient for MVP functionality.

**Independent Test**: Can be fully tested by configuring different provider endpoints and verifying the tool connects to the specified service.

**Acceptance Scenarios**:

1. **Given** a user has configured a custom API endpoint, **When** they run the rewrite command, **Then** the tool uses the configured endpoint for processing
2. **Given** a user runs the command without custom configuration, **When** a default provider is configured, **Then** the tool uses the default provider
3. **Given** a user's API credentials are invalid, **When** they run the rewrite command, **Then** they receive a clear authentication error

---

### Edge Cases

- What happens when the input text is very long?
  - System warns the user about potential quality impact but continues processing
- How does the system handle network failures during API calls?
  - System retries with appropriate error recovery behavior, then reports a clear error if recovery fails
- What happens when the API credentials are missing or invalid?
  - System reports a clear authentication error without exposing sensitive details
- How does the system handle text with mixed languages (English + other)?
  - See Assumptions section for mixed language handling
- What happens when the API returns malformed or unexpected output?
  - System validates response structure and reports a processing error if invalid
  - *Malformed response definition*: Response missing `choices[0].message.content` field, or the field is empty/null after stripping whitespace, or the response body cannot be parsed as valid JSON

## Requirements *(mandatory)*

### Functional Requirements

**Text Input & Output**
- **FR-001**: System MUST accept text input via command-line argument or file path
- **FR-002**: System MUST validate that input text is non-empty
- **FR-003**: System MUST produce output with overall **word count** within ±20% of input word count
- **FR-004**: System MUST preserve the original text's paragraph structure
- **FR-005**: System MUST preserve the original text's main topics and key information
  - *Verification method*: LLM-assisted semantic equivalence check + 10% human spot-check on random samples
  - *Pass threshold*: ≥90% of samples rated as "main topics preserved" by evaluator

**AI Pattern Reduction**
- **FR-006**: System MUST reduce the occurrence count of phrases listed in `references/vocabulary-banlist.md` Tier 1 and Tier 2 categories
  - *Verification method*: Count occurrences before and after rewrite using pattern matching
  - *Pass threshold* (conditional):
    - When pre-rewrite count ≥ 3: post-rewrite count ≤ pre-rewrite count - 1 (reduce by at least 1) OR post-rewrite count ≤ pre-rewrite count × 50%
    - When pre-rewrite count < 3: post-rewrite count ≤ pre-rewrite count (no increase)
    - When pre-rewrite count = 0: no constraint (tool still rewrites; pattern threshold does not apply)
- **FR-007**: System MUST NOT introduce new occurrences of phrases from `references/vocabulary-banlist.md` Tier 1 category in the output
  - *Verification method*: Pattern matching on output text
  - *Pass threshold*: Zero new Tier 1 phrase introductions in test samples
- **FR-008**: System MUST produce output that reads naturally to native English speakers
  - *Verification method*: Human readability review on sample outputs
  - *Pass threshold*: ≥80% of samples rated as "natural" by reviewer

**Provider Integration**
- **FR-009**: System MUST support configurable LLM API endpoints
- **FR-010**: System MUST load API credentials from secure sources (environment variables or configuration files)
- **FR-011**: System MUST implement automatic error recovery for transient network failures
  - *Max retries*: 3 attempts
  - *Request timeout*: 60 seconds per request
  - *Verification scenarios* (Given/When/Then):
    - **Given** a network request times out, **When** the system detects timeout, **Then** it automatically retries at least once
    - **Given** retry still fails after maximum attempts, **When** max retries exhausted, **Then** system returns actionable error message + non-zero exit code
- **FR-012**: System MUST provide clear, user-friendly error messages without exposing internal details
  - Error messages MUST NOT contain: API key values, user input text content, or internal file system paths
  - Error messages SHOULD identify the error category and suggest a corrective action (see `contracts/cli.md` Error Messages section for required formats)

**Architecture**
- **FR-016**: System MUST provide a programmatically callable core rewrite interface
  - *CLI is only a wrapper layer* over this interface
  - *Core interface can be called directly by other programs* without CLI dependency
  - *Verification method*: Import core module in test script and call rewrite function directly (no CLI subprocess)

**Output & Logging**
- **FR-013**: System MUST output rewritten text to stdout or a specified file
  - *Default file naming*: `<input_filename>_rewritten.<extension>` (e.g., `draft.txt` → `draft_rewritten.txt`)
  - *Output location*: Same directory as input file when no explicit output path provided
- **FR-014**: System MUST log metadata only (processing status, timing) without logging actual text content
- **FR-015**: System MUST exit with appropriate status codes (0 for success, non-zero for errors)
- **FR-017**: System MUST emit a warning message to stderr when input word count exceeds 5,000 words, before proceeding with rewriting
  - *Warning format*: `Warning: Input exceeds 5,000 words ({count} words). Output quality may be reduced.`
  - *Behavior*: Warning is non-blocking; rewriting proceeds normally after warning is emitted

### Key Entities

- **RewriteRequest**: Represents a user's request to rewrite text; includes the input text, desired style, and output destination
- **RewriteResult**: Represents the outcome of a rewrite operation; includes the rewritten text and processing status
- **LanguagePack**: Contains language-specific rules including vocabulary patterns and structural guidance; English Pack is the MVP implementation
- **ProviderConfig**: Configuration for connecting to an LLM service; includes endpoint URL and credentials

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Output Quality**
- **SC-001**: Rewritten text shows reduction in AI-typical vocabulary patterns
  - *Verification*: Pattern matching count on `references/vocabulary-banlist.md` phrases (see FR-006)
  - *Target* (conditional):
    - When pre-rewrite count ≥ 3: post-rewrite count ≤ pre-rewrite count - 1 OR ≤ pre-rewrite count × 50%
    - When pre-rewrite count < 3: post-rewrite count ≤ pre-rewrite count
- **SC-002**: Rewritten text maintains semantic equivalence with original
  - *Verification*: LLM-assisted check + 10% human spot-check
  - *Target*: ≥90% pass rate on evaluated samples
- **SC-003**: Rewritten text preserves structural elements
  - *Paragraphs*: 100% retention (same number of paragraphs)
  - *Main topics*: ≥90% retention (verified by human review)

**System Behavior**
- **SC-004**: System processes valid inputs without crashing or producing malformed output
  - *Verification*: Run on 10 test samples with diverse content
  - *Sample composition*: 2 blog posts, 2 technical documents, 2 academic abstracts, 2 short texts (<100 words), 1 formal report, 1 text with high AI-pattern density (>=10 banlist phrases)
  - *Target*: At least 9 of 10 complete successfully with valid output
- **SC-005**: System handles error conditions with actionable error messages
  - *Verification*: Test with missing API key, invalid endpoint, malformed input
  - *Target*: Each error produces a message that identifies the problem and suggests resolution

### Quality Attributes

- **Correctness**: Rewritten text must be grammatically correct and coherent
- **Naturalness**: Output should read as if written by a native English speaker without obvious AI patterns
- **Completeness**: No key information from the original text should be lost in the rewriting process
- **Privacy**: User text is never stored, logged, or transmitted beyond the configured LLM endpoint

## Review Protocol

### Semantic Equivalence Review (FR-005, SC-002)
- **Sample size**: 10 random samples per batch
- **Reviewers**: 1 person (team member)
- **Rating criteria**: Pass/Fail with written justification
  - Pass: Main topics and key information preserved
  - Fail: Significant information lost or meaning changed
- **Pass threshold**: ≥9/10 samples rated Pass

### Naturalness Review (FR-008)
- **Sample size**: 10 random samples per batch
- **Reviewers**: 1 person (native English speaker or equivalent proficiency)
- **Rating criteria**: "Natural" / "Unnatural" with examples
  - Natural: Reads like human-written text without obvious AI patterns
  - Unnatural: Contains jarring phrases or obvious AI-typical constructions
- **Pass threshold**: ≥8/10 samples rated "Natural"

## Assumptions

1. **LLM Provider Availability**: Users have access to an LLM API service with a standard protocol interface
2. **English Proficiency**: Target users are proficient in English and can evaluate output quality
3. **Local Execution**: Tool runs on user's local machine (WSL2, Linux, or macOS)
4. **Network Connectivity**: Users have stable internet connection for API calls
5. **Text Format**: Input text is plain text or can be easily converted to plain text
6. **Reasonable Length**: Users typically process documents under 5,000 words; longer texts may have reduced quality (see FR-017 for warning behavior)
7. **Pure English Input**: Input is expected to be primarily English; mixed language text may produce undefined results and is not guaranteed to preserve non-English segments unchanged

**Pending Quantification** (to be refined after corresponding Open Questions are resolved):
- AI-typical pattern reduction percentage → depends on Q007 resolution
- Semantic equivalence verification protocol → may be refined based on Q006/Q007 outcomes

## Out of Scope (MVP)

The following are explicitly excluded from MVP but may be considered for future versions:

- Chinese and other non-English language support
- Web-based user interface or hosted service
- User accounts and authentication
- Batch processing of multiple files
- Plugin/extension system for custom rules
- Real-time collaborative editing
- Integration with word processors or content management systems
- Fine-tuned local models (offline processing)
- Detailed AI detection scores or metrics display
- Provider-specific native SDK integrations (only standard protocol endpoints supported)
- Guaranteed handling of mixed-language input