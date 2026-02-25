# Tasks: Deterministic Synthesis via Chief Justice (Layer 3)

**Input**: Design documents from `/specs/009-deterministic-synthesis/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Tests are REQUESTED in `spec.md` and `quickstart.md`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure for Chief Justice node in `src/nodes/justice.py`
- [ ] T002 Ensure `uv` environment is ready and dependencies synced

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 [P] Update `CriterionResult` in `src/state.py` with `judge_opinions`, `dissent_summary`, `remediation`, `applied_rules`, `execution_log`, and `re_evaluation_required`
- [ ] T004 [P] Update `AuditReport` in `src/state.py` to include `global_score` and `results` per enhanced data model
- [ ] T005 [P] Implement `round_half_up` helper function in `src/nodes/justice.py` using `decimal.ROUND_HALF_UP`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Resolving Conflicting Judicial Opinions (Priority: P1) 🎯 MVP

**Goal**: Resolve conflicting judge scores using weighted rule-based engine and deterministic rounding.

**Independent Test**: Provide 3 `JudicialOpinion` objects with high variance (1, 3, 5); verify synthesized score matches weighted outcome with correct rounding.

### Tests for User Story 1

- [ ] T006 [P] [US1] Create unit tests for `FUNCTIONALITY_WEIGHT` and deterministic rounding in `tests/unit/test_justice.py`
- [ ] T007 [P] [US1] Create unit tests for missing judge fallback (mean of remaining two) in `tests/unit/test_justice.py`

### Implementation for User Story 1

- [ ] T008 [US1] Implement `ChiefJusticeNode` core orchestration loop in `src/nodes/justice.py`
- [ ] T009 [US1] Implement `FUNCTIONALITY_WEIGHT` (TechLead = 2x) weighted average logic in `src/nodes/justice.py`
- [ ] T010 [US1] Implement missing judge fallback logic and "Degraded Synthesis" logging in `src/nodes/justice.py`

**Checkpoint**: User Story 1 (Core Synthesis) functional and testable.

---

## Phase 4: User Story 2 - Security Constraint Enforcement (Priority: P1)

**Goal**: Confirmed security vulnerabilities automatically cap the project's score at 3.

**Independent Test**: Provide high judge scores but include evidence of `os.system` usage; verify final score is capped at 3.

### Tests for User Story 2

- [ ] T011 [P] [US2] Create unit tests for `SECURITY_OVERRIDE` triggers (evidence vs judge keywords) in `tests/unit/test_justice.py`

### Implementation for User Story 2

- [ ] T012 [US2] Implement evidence search logic for security violations (e.g., `os.system`, `shell=True`) in `src/nodes/justice.py`
- [ ] T013 [US2] Implement Prosecutor keyword scan for "Security Violation" signals in `src/nodes/justice.py`
- [ ] T014 [US2] Apply score capping logic to override final calculations when security triggers are active in `src/nodes/justice.py`

**Checkpoint**: Security overrides enforced.

---

## Phase 5: User Story 3 - Fact-Checking Judicial Arguments (Priority: P2)

**Goal**: Invalidate/penalize judicial claims that cite non-existent or false evidence.

**Independent Test**: Provide opinion citing `evidence_id: missing_01` where `found=False`; verify judge score influence is penalized.

### Tests for User Story 3

- [ ] T015 [P] [US3] Create unit tests for `FACT_SUPREMACY` score penalization in `tests/unit/test_justice.py`

### Implementation for User Story 3

- [ ] T016 [US3] Implement evidence cross-reference logic to validate citations against the state evidence pool in `src/nodes/justice.py`
- [ ] T017 [US3] Implement score penalty logic (`adjusted_score = max(1, original_score - 2)`) for hallucinated citations in `src/nodes/justice.py`

**Checkpoint**: Fact supremacy enforced.

---

## Phase 6: User Story 4 - Variance Re-evaluation (Priority: P2)

**Goal**: Automatically flag and re-evaluate criteria with high score variance (>2).

**Independent Test**: Provide scores 1, 1, 5; verify `re_evaluation_required` is set to `True` and `execution_log` contains variance details.

### Tests for User Story 4

- [ ] T018 [P] [US4] Create unit tests for `VARIANCE_RE_EVALUATION` triggers and flag setting in `tests/unit/test_justice.py`

### Implementation for User Story 4

- [ ] T019 [US4] Implement variance calculation logic and flag triggering in `src/nodes/justice.py`
- [ ] T020 [US4] Implement automated evidence quality check during re-evaluation in `src/nodes/justice.py`

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T021 [P] Implement template-based `dissent_summary` generation for variance > 2 in `src/nodes/justice.py`
- [ ] T022 [P] Implement detailed narrative `execution_log` generation in `src/nodes/justice.py`
- [ ] T023 [P] Create integration test for full synthesis workflow in `tests/integration/test_synthesis_workflow.py`
- [ ] T024 [P] Benchmark processing time to verify SC-004 (< 50ms) in `tests/performance/test_synthesis_perf.py`
- [ ] T025 [P] Update `docs/` and verify `quickstart.md` steps pass against current implementation
- [ ] T026 Run full test suite with `uv run pytest`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all story implementation.
- **User Stories (Phase 3+)**: Depend on Foundational (Phase 2).
  - US1 (P1) is the MVP and should be prioritized.
  - US2 (P1) and US3 (P2) can proceed in parallel once US1 core structure is in place.
- **Polish (Phase 6)**: Depends on completion of all US phases.

### Parallel Opportunities

- T003, T004, T005 can run in parallel.
- All US test tasks (T006, T007, T011, T015) can run in parallel.
- Integration tests and polish tasks can run in parallel after implementation is stable.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup + Foundational (T001-T005).
2. Complete US1 implementation (T006-T010).
3. **VALIDATE**: Ensure weighted scoring and rounding work perfectly.

### Incremental Delivery

1. Foundation + US1 -> Verifiable core.
2. Add US2 -> Security hardening.
3. Add US3 -> Hallucination prevention.
4. Add Polish -> Production readiness.
