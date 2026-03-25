# Tasks: MVP Text Rewrite Engine

**Input**: Design documents from `/specs/002-mvp-text-rewrite/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/cli.md ✓

**Tests**: Included per AGENTS.md Done Definition (tests required before marking complete)

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Project initialization and basic structure

- [X] T001 Verify pyproject.toml has all dependencies per research.md
- [X] T002 [P] Create core module structure in src/anti_slop_writer/core/__init__.py
- [X] T003 [P] Create language_packs module structure in src/anti_slop_writer/language_packs/__init__.py
- [X] T004 [P] Create providers module structure in src/anti_slop_writer/providers/__init__.py
- [X] T005 [P] Create interfaces module structure in src/anti_slop_writer/interfaces/__init__.py
- [X] T006 Create main package exports in src/anti_slop_writer/__init__.py

---

## Phase 2: Foundational

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Implement ProviderConfig model in src/anti_slop_writer/providers/config.py
- [X] T008 [P] Implement RewriteRequest model in src/anti_slop_writer/core/models.py
- [X] T009 [P] Implement RewriteResult model in src/anti_slop_writer/core/models.py
- [X] T010 [P] Implement RewriteContext model in src/anti_slop_writer/core/models.py
- [X] T011 Implement BaseProvider abstract class in src/anti_slop_writer/providers/base.py
- [X] T012 Implement LanguagePack abstract class in src/anti_slop_writer/language_packs/base.py
- [X] T013 Implement EnglishPack with compiled regex patterns and style_prompts in src/anti_slop_writer/language_packs/english.py
- [X] T014 Implement RuleEngine for pattern matching in src/anti_slop_writer/core/rule_engine.py
- [X] T015 Implement settings/configuration loader in src/anti_slop_writer/core/config.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Basic Text Rewriting (Priority: P1) 🎯 MVP

**Goal**: Core text rewriting capability - reduce AI patterns while preserving meaning

**Independent Test**: Provide sample AI-generated text via CLI, verify output has fewer AI patterns and maintains semantic equivalence

### Tests for User Story 1

- [X] T016 [P] [US1] Unit test for Rewriter in tests/unit/test_rewriter.py
- [X] T017 [P] [US1] Unit test for RuleEngine pattern counting and FR-007 (no new Tier 1) in tests/unit/test_rule_engine.py
- [X] T018 [P] [US1] Integration test for CLI rewrite command in tests/integration/test_cli.py

### Implementation for User Story 1

- [X] T019 [US1] Implement OpenAI-compatible provider in src/anti_slop_writer/providers/openai_compatible.py
- [X] T020 [US1] Implement Rewriter class with LLM integration in src/anti_slop_writer/core/rewriter.py
- [X] T021 [US1] Implement text processing utilities in src/anti_slop_writer/core/processor.py
- [X] T022 [US1] Implement CLI rewrite command in src/anti_slop_writer/interfaces/cli.py
- [X] T023 [US1] Add error handling with exit codes 0-5 per contracts/cli.md
- [X] T024 [US1] Add logging (metadata only, no text content) per FR-014
- [X] T025 [US1] Add word count warning (FR-017) when input exceeds 5,000 words in src/anti_slop_writer/core/processor.py

**Checkpoint**: User Story 1 complete - basic text rewriting functional

---

## Phase 4: User Story 2 - File-Based Processing (Priority: P2)

**Goal**: Process text from files and save to files with default naming

**Independent Test**: Provide file path as input, verify output file created with `_rewritten` suffix

### Tests for User Story 2

- [ ] T026 [P] [US2] Unit test for file I/O handling in tests/unit/test_processor.py
- [ ] T027 [P] [US2] Integration test for file input/output in tests/integration/test_cli.py

### Implementation for User Story 2

- [ ] T028 [US2] Add --input option handling in src/anti_slop_writer/interfaces/cli.py
- [ ] T029 [US2] Add --output option handling with default naming in src/anti_slop_writer/interfaces/cli.py
- [ ] T030 [US2] Add file validation (exists, readable) in src/anti_slop_writer/core/processor.py
- [ ] T031 [US2] Add stdin support (`-` argument) in src/anti_slop_writer/interfaces/cli.py

**Checkpoint**: User Story 2 complete - file-based processing functional

---

## Phase 5: User Story 3 - Style Selection (Priority: P3)

**Goal**: Allow users to choose output style (neutral, formal, casual)

**Independent Test**: Run rewrite with different --style options, verify output tone matches

### Tests for User Story 3

- [ ] T032 [P] [US3] Unit test for style prompt injection in tests/unit/test_rewriter.py
- [ ] T033 [P] [US3] Integration test for style options in tests/integration/test_cli.py

### Implementation for User Story 3

- [ ] T034 [US3] Add --style option in src/anti_slop_writer/interfaces/cli.py
- [ ] T035 [US3] Integrate style prompts into Rewriter in src/anti_slop_writer/core/rewriter.py

**Checkpoint**: User Story 3 complete - style selection functional

---

## Phase 6: User Story 4 - Provider Configuration (Priority: P3)

**Goal**: Allow users to configure LLM provider endpoints and credentials

**Independent Test**: Configure custom endpoint, verify tool connects to specified service

### Tests for User Story 4

- [ ] T036 [P] [US4] Unit test for ProviderConfig validation in tests/unit/test_provider.py
- [ ] T037 [P] [US4] Integration test for custom endpoint in tests/integration/test_provider.py

### Implementation for User Story 4

- [ ] T038 [US4] Implement config file loading in src/anti_slop_writer/core/config.py
- [ ] T039 [US4] Add environment variable support (ANTI_SLOP_WRITER_*) in src/anti_slop_writer/core/config.py
- [ ] T040 [US4] Add --provider option in src/anti_slop_writer/interfaces/cli.py
- [ ] T041 [US4] Add credential validation with clear error messages in src/anti_slop_writer/providers/openai_compatible.py

**Checkpoint**: User Story 4 complete - provider configuration functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, documentation, and verification

- [ ] T042 [P] Create shared test fixtures in tests/conftest.py
- [ ] T043 [P] Add comprehensive docstrings to all public APIs
- [ ] T044 Verify FR-016 (Library-First): test direct module import without CLI
- [ ] T045 Run full test suite: `uv run pytest --cov=src/anti_slop_writer`
- [ ] T046 Run quality checks: `uv run ruff check src/ && uv run mypy src/`
- [ ] T047 Validate quickstart.md scenarios manually
- [ ] T048 [P] Create example config file at examples/config.toml

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
- **Polish (Phase 7)**: Depends on User Story 1 minimum (MVP)

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Phase 2 - Independent of US1 but extends CLI
- **User Story 3 (P3)**: Can start after Phase 2 - Independent, modifies Rewriter prompts
- **User Story 4 (P3)**: Can start after Phase 2 - Independent, extends config

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models/config before core logic
- Core logic before CLI integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks T002-T006 can run in parallel
- All Foundational models T008-T010 can run in parallel
- All tests within a user story can run in parallel
- User Stories 2, 3, 4 can be worked on in parallel after US1 is stable

---

## Parallel Example: Phase 2 Foundational

```bash
# Launch all model definitions together:
Task: "Implement RewriteRequest model in src/anti_slop_writer/core/models.py"
Task: "Implement RewriteResult model in src/anti_slop_writer/core/models.py"
Task: "Implement RewriteContext model in src/anti_slop_writer/core/models.py"
```

## Parallel Example: User Story 1 Tests

```bash
# Launch all US1 tests together:
Task: "Unit test for Rewriter in tests/unit/test_rewriter.py"
Task: "Unit test for RuleEngine in tests/unit/test_rule_engine.py"
Task: "Integration test for CLI in tests/integration/test_cli.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test independently with `uv run pytest`
5. Manual test: `anti-slop-writer rewrite "test text"`

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. User Story 1 → Test → **MVP Deployable**
3. User Story 2 → File I/O capability
4. User Story 3 → Style customization
5. User Story 4 → Provider flexibility

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests fail first, then implement
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- FR-016 verification in T044 ensures Library-First architecture
- T025 implements FR-017 word count warning (5,000+ words)