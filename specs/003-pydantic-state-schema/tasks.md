# Tasks: Pydantic State Schema and Annotated Reducers

**Input**: Design documents from `/specs/003-pydantic-state-schema/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P] [Story] Description`

- **[P]**: Can run in parallel (different files or non-conflicting edits)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- File paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Update dependencies in `pyproject.toml` (pydantic>=2.6.0, langgraph, typing_extensions)
- [x] T002 [P] Create `src/state.py` with base imports and Pydantic configuration
- [x] T003 [P] Create `tests/unit/test_state.py` with basic test scaffolding

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T004 Implement `StrictModel` base class with `extra='forbid'`, `strict=True`, and `frozen=True` in `src/state.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Evidence Validation (Priority: P1) 🎯 MVP

**Goal**: Implement strict schema for `Evidence` and `JudicialOpinion` with validation bounds.

**Independent Test**: Instantiate `Evidence` with confidence > 1.0 or < 0.0 and verify `ValidationError` is raised.

### Tests for User Story 1

- [x] T005 [P] [US1] Create validation tests for `Evidence` (confidence bounds) in `tests/unit/test_state.py`
- [x] T006 [P] [US1] Create validation tests for `JudicialOpinion` (optional fields/defaults) in `tests/unit/test_state.py`

### Implementation for User Story 1

- [x] T007 [US1] Implement `Evidence` model in `src/state.py` using `Field(ge=0, le=1)`
- [x] T008 [US1] Implement `JudicialOpinion` model in `src/state.py` with default values for `case_id` and `court_name` (plural naming applied to opinions list downstream)

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Parallel State Merging (Priority: P1)

**Goal**: Implement custom deduplicating and confidence-based reducers for `AgentState`.

**Independent Test**: Invoke `merge_evidence` with duplicate items and verify the count; invoke `merge_criterion_results` with same ID and verify highest confidence wins.

### Tests for User Story 2

- [x] T009 [P] [US2] Create unit tests for `merge_evidences` (SHA-256 deduplication/dict structure/fatal type error) in `tests/unit/test_state.py`
- [x] T010 [P] [US2] Create unit tests for `merge_criterion_results` (confidence resolution/fatal type error) in `tests/unit/test_state.py`

### Implementation for User Story 2

- [x] T011 [US2] Implement `merge_evidences` reducer in `src/state.py` (plural, dict-based, SHA-256 deduplication)
- [x] T012 [US2] Implement `merge_criterion_results` reducer in `src/state.py` (highest confidence wins)
- [x] T013 [US2] Define `AgentState` TypedDict with `Annotated` reducers in `src/state.py` (naming: `evidences`, `opinions`, `criterion_results`)

**Checkpoint**: Parallel state aggregation logic is valid.

---

## Phase 5: User Story 3 - Criterion Scoring Constraints (Priority: P1)

**Goal**: Implement `CriterionResult` constraints and `AuditReport` with weighted scoring logic.

**Independent Test**: Create `AuditReport` with a security violation and verify the `global_score` is capped per Constitution XI.

### Tests for User Story 3

- [x] T014 [P] [US3] Create validation tests for `CriterionResult` (score bounds [1,5]) in `tests/unit/test_state.py`
- [x] T015 [P] [US3] Create tests for `AuditReport.global_score` calculation and rounding in `tests/unit/test_state.py`

### Implementation for User Story 3

- [x] T016 [US3] Implement `CriterionResult` model in `src/state.py` using `Field(ge=1, le=5)`
- [x] T017 [US3] Implement `AuditReport` model in `src/state.py` with `@property` or validator for `global_score` (Constitution XI weighted average)

**Checkpoint**: All data models and scoring logic are complete and verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and cleanup.

- [x] T018 [P] Verify all code examples in `quickstart.md` against implementation in `src/state.py`
- [x] T019 Run full test suite with coverage report and fix any linting issues
- [x] T020 [P] Document any implementation variations in `research.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1-2**: Blocking - Must complete before User Stories.
- **Phase 3-5**: Can run in parallel if independent files were used, but since they share `src/state.py`, sequential execution (US1 -> US2 -> US3) is recommended to avoid merge conflicts.
- **Phase 6**: Final verification.

### Parallel Opportunities

- Test files can be prepared in parallel with model definitions.
- US1 and US2 models can be drafted in parallel if using temporary files, though final consolidation is needed in `src/state.py`.

---

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Complete Setup & Foundation.
2. Implement US1 (Evidence) and US2 (Reducers) to enable basic graph flow.
3. Validate with basic tests.

### Incremental Delivery

1. Foundation -> Core State -> Merging Logic -> Scoring Logic.
2. Each phase adds a layer of validation or aggregation.
