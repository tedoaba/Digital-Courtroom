# Tasks: Core Observability and Error Handling Framework

**Input**: Design documents from `/specs/002-observability-error-handling/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Test tasks are included as TDD is mandated by the implementation plan and project constitution.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize feature branch `002-observability-error-handling` and install dependencies `python-json-logger` and `langsmith` using `uv add`
- [ ] T002 [P] Verify `src/utils/` and `tests/unit/` directories exist per project structure in `plan.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Implement exception hierarchy (`AppException`, `RetryableException`, `FatalException`, and subclasses) in `src/exceptions.py`
- [ ] T004 [P] Create unit tests for the exception hierarchy in `tests/unit/test_exceptions.py` to verify `fatal` attribute and inheritance
- [ ] T005 Create base `src/utils/logger.py` with standard library logging setup placeholder

**Checkpoint**: Foundation ready - exception classes and basic structure are in place.

---

## Phase 3: User Story 1 - Machine-Readable Logging (Priority: P1) 🎯 MVP

**Goal**: Standardized, JSON-formatted logging with automatic PII masking.

**Independent Test**: Run `tests/unit/test_logger.py` and verify all logs are valid JSON and PII (emails/phones) are masked.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T006 [P] [US1] Create unit tests in `tests/unit/test_logger.py` for JSON structure, required fields (`timestamp`, `event_type`, `severity`), and PII masking

### Implementation for User Story 1

- [ ] T007 [P] [US1] Implement `PIIRedactionFilter` in `src/utils/logger.py` using regex-based masking for emails and phone numbers
- [ ] T008 [US1] Implement `StructuredLogger` class in `src/utils/logger.py` using `python-json-logger` or standard JSON formatter
- [ ] T009 [US1] Add dedicated methods to `StructuredLogger` for node events: `log_node_entry`, `log_evidence_created`, `log_opinion_rendered`

**Checkpoint**: User Story 1 functional - system can now emit redacted JSON logs to stdout.

---

## Phase 4: User Story 2 - Execution Flow Visualization (Priority: P1)

**Goal**: Trace execution paths and parent-child relationships using LangSmith.

**Independent Test**: Enable tracing via environment variables and verify traces appear in LangSmith with correct hierarchy in `tests/integration/test_observability_context.py`.

### Tests for User Story 2

- [ ] T010 [P] [US2] Create integration test `tests/integration/test_observability_context.py` to verify `langsmith` context propagation across simulated node transitions

### Implementation for User Story 2

- [ ] T011 [US2] Configure LangSmith environment variables and tracing settings in `src/config.py` using Pydantic `BaseSettings`
- [ ] T012 [US2] Verify or apply `@traceable` decorators to core entry points to ensure automatic context linkage

**Checkpoint**: User Story 2 functional - execution traces are captured and visualized when enabled.

---

## Phase 5: User Story 3 - Categorized Error Handling (Priority: P2)

**Goal**: Automated recovery decisions based on exception types (Retryable vs. Fatal).

**Independent Test**: Simulate errors and verify the logger maps `FatalException` to `CRITICAL` severity and `RetryableException` to `WARNING`.

### Implementation for User Story 3

- [ ] T013 [US3] Implement log level mapping logic in `StructuredLogger` to automatically use `CRITICAL` for fatal errors and `WARNING` for retryable ones
- [ ] T014 [US3] Update `tests/unit/test_logger.py` to verify the automated severity mapping for different exception categories

**Checkpoint**: User Story 3 functional - system distinguishes error types for intelligent alerting and recovery.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements and alignment with the project constitution.

- [ ] T015 [P] Update `src/state.py` with structured error/log fields if required for node-level state tracking
- [ ] T016 [P] Update `docs/quickstart.md` with final API examples and PII masking confirmation
- [ ] T017 Final run of `tests/unit/` and `tests/integration/` ensuring 100% pass rate
- [ ] T018 Run `check-prerequisites.ps1` to ensure no regression in documentation quality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1 completion.
- **User Stories (Phase 3+)**: All depend on Phase 2 completion.
  - US1 and US2 can proceed in parallel.
  - US3 should follow US1 as it enhances the logging logic.
- **Polish (Phase 6)**: Depends on all stories being complete.

### Within Each User Story

- Tests MUST be written first and fail as per Constitution C-II.
- Base utilities (PII filter) before high-level classes (Logger).
- Core logic before integrated severity mapping.

---

## Parallel Example: Logging & Tracing Setup

```bash
# Launch Foundational tasks together:
Task: "Create unit tests for the exception hierarchy in tests/unit/test_exceptions.py"
Task: "Implement exception hierarchy... in src/exceptions.py"

# Launch US1 & US2 testing setup together:
Task: "[US1] Create unit tests in tests/unit/test_logger.py"
Task: "[US2] Create integration test ... in tests/integration/test_observability_context.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Focus)

1. Complete Setup and Foundational Exception hierarchy.
2. Complete User Story 1 (Structured Logging).
3. **VALIDATE**: Run `tests/unit/test_logger.py`. This provides the minimum observability needed for other features.

### Incremental Delivery

1. Foundation + US1 -> Basic JSON logs ready.
2. Add US2 -> Distributed tracing enabled.
3. Add US3 -> Smart error categorization and critical alerting.
4. Final Polish -> Documentation and state alignment.
