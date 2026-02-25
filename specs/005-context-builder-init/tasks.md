# Tasks: ContextBuilder Initialization Node

**Input**: Design documents from `/specs/005-context-builder-init/`
**Prerequisites**: [plan.md](./plan.md) (required), [spec.md](./spec.md) (required for user stories), [research.md](./research.md), [data-model.md](./data-model.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create source and test directories for nodes at `src/nodes/` and `tests/nodes/`
- [ ] T002 [P] Verify project environment and dependencies (`langgraph`, `pydantic`, `python-json-logger`) using `uv sync` and `uv run pytest`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Define custom exception hierarchy (`ContextBuilderError`, `InvalidURLError`, `RubricLoadError`) in `src/exceptions.py`
- [ ] T004 Define/Update `AgentState` schema in `src/state.py` to include `rubric_dimensions`, `synthesis_rules`, `evidences`, `opinions`, `criterion_results`, and `errors` per `data-model.md`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Successful Audit Initialization (Priority: P1) 🎯 MVP

**Goal**: Bootstrap the execution state and load the default evaluation rubric.

**Independent Test**: Invoke `ContextBuilder` node with valid inputs and verify the returned state contains loaded rubric dimensions and initialized collections.

### Tests for User Story 1

- [ ] T005 [P] [US1] Create unit test for successful rubric loading and state bootstrapping in `tests/nodes/test_context_builder.py`

### Implementation for User Story 1

- [ ] T006 [US1] Implement `ContextBuilder` node function in `src/nodes/context_builder.py` with basic rubric loading logic (FR-001, FR-005: load dimensions and synthesis_rules)
- [ ] T007 [US1] Implement state initialization for `evidences`, `opinions`, and `criterion_results` as empty structures in `src/nodes/context_builder.py` (FR-009)

**Checkpoint**: User Story 1 is functional (can load rubric and init state).

---

## Phase 4: User Story 2 - Input Validation Fast-Fail (Priority: P2)

**Goal**: Fail immediately if inputs (`repo_url`, `pdf_path`) are malformed or missing.

**Independent Test**: Pass invalid URL formats or non-existent file paths and verify that error messages are appended to the `errors` state.

### Tests for User Story 2

- [ ] T008 [P] [US2] Create unit tests for input validation (GitHub URL regex, local path existence) in `tests/nodes/test_context_builder.py`

### Implementation for User Story 2

- [ ] T009 [US2] Implement strict regex validation for `repo_url` in `src/nodes/context_builder.py` (FR-002, FR-003)
- [ ] T010 [US2] Implement `pdf_path` existence check using `os.path.exists()` in `src/nodes/context_builder.py` (FR-004)
- [ ] T011 [US2] Implement "fail gracefully" logic by appending descriptive messages to `state['errors']` in `src/nodes/context_builder.py` (FR-007)

**Checkpoint**: User Story 2 is functional (validates inputs and handles errors).

---

## Phase 5: User Story 3 - Dynamic Rubric Configuration (Priority: P3)

**Goal**: Allow specifying a custom rubric file path via the `AgentState`.

**Independent Test**: Configure a custom rubric path in the initial state and verify the node loads that specific file.

### Tests for User Story 3

- [ ] T012 [P] [US3] Create unit test for custom `rubric_path` loading in `tests/nodes/test_context_builder.py`

### Implementation for User Story 3

- [ ] T013 [US3] Update `ContextBuilder` to use `rubric_path` from the state with a default fallback in `src/nodes/context_builder.py` (FR-008)

**Checkpoint**: All user stories are functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T014 [P] Implement mandatory structured logging for `context_builder_entry` and `context_builder_exit` with rubric metadata in `src/nodes/context_builder.py` (FR-006, Const. XXII)
- [ ] T015 Verify that the node execution (validation + loading) takes less than 500ms (SC-001)
- [ ] T016 Ensure all node activities use the correct `correlation_id` and `event_type` in logs (SC-004)
- [ ] T017 Final review of implementation against the Constitution and Architectural Notes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001.
- **User Stories (Phases 3-5)**: Depend on Phase 2 completion.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### Parallel Opportunities

- T002, T003, T004 can theoretically run in parallel if split by file, but T004 is foundational.
- Once Phase 2 is done, US1, US2, and US3 tests (T005, T008, T012) can be written in parallel.
- Implementation tasks within a story can follow the Test -> Implementation flow.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate that the node can at least bootstrap a valid state with a default rubric.

### Incremental Delivery

1. Foundation Ready (Phase 1-2).
2. Audit Intro (Phase 3).
3. Safety Net (Phase 4).
4. Customization (Phase 5).
5. Production Hardening (Phase 6).
