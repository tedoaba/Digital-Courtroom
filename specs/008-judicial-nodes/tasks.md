# Tasks: Dialectical Judicial Agents (Layer 2)

**Input**: Design documents from `/specs/008-judicial-nodes/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Tests are included as they are mandatory per the specification's "User Scenarios & Testing" section.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create `specs/008-judicial-nodes/checklists/requirements.md` per implementation plan documentation structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T002 Update `src/state.py` with `JudicialOpinion` Pydantic model (including mandatory fields: `opinion_id`, `judge`, `criterion_id`, `score`, `argument`, `cited_evidence`)
- [ ] T003 Update `AgentState` in `src/state.py` to include `opinions` list with `operator.add` reducer
- [ ] T004 Define `JudicialTask` TypedDict in `src/nodes/judges.py` for LangGraph `Send` pattern
- [ ] T005 [P] Ensure `src/config.py` enforces `temperature=0` for judicial LLM calls

**Checkpoint**: Foundation ready - Judicial state and configuration are in place.

---

## Phase 3: User Story 1 - Multi-Perspective Adversarial Review (Priority: P1) 🎯 MVP

**Goal**: Implement three distinct persona-based LLM nodes (Prosecutor, Defense, TechLead) to interpret evidence objectively based on character philosophies.

**Independent Test**: Feed a mock evidence payload and verify three distinct `JudicialOpinion` objects are produced with different reasoning and scores.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T006 [P] [US1] Create unit tests for persona prompt divergence (< 10% overlap) in `tests/unit/test_judges.py`
- [ ] T007 [P] [US1] Create unit test for judicial fan-out logic using `Send` in `tests/unit/test_judges.py`

### Implementation for User Story 1

- [ ] T008 [US1] Implement "Philosophy Blocks" for Prosecutor, Defense, and TechLead in `src/nodes/judges.py`
- [ ] T009 [US1] Implement `evaluate_criterion` node in `src/nodes/judges.py` using `.with_structured_output(JudicialOpinion)`
- [ ] T010 [US1] Implement integration test for the full fan-out/fan-in workflow in `tests/integration/test_judicial_workflow.py`

**Checkpoint**: User Story 1 is functional - 3 judges can now evaluate a single criterion in parallel.

---

## Phase 4: User Story 2 - Structured Judicial Feedback (Priority: P2)

**Goal**: Ensure judges provide structured feedback citing specific evidence IDs and providing persona-specific insights.

**Independent Test**: Verify that `cited_evidence` IDs exist in the input `evidences` dictionary and that persona-specific fields are populated.

### Tests for User Story 2

- [ ] T011 [P] [US2] Add unit tests for evidence citation validation in `tests/unit/test_judges.py`
- [ ] T012 [P] [US2] Add unit tests for persona-specific field population (mitigations, charges, remediation) in `tests/unit/test_judges.py`

### Implementation for User Story 2

- [ ] T013 [P] [US2] Update `JudicialOpinion` model in `src/state.py` with optional fields: `mitigations`, `charges`, `remediation`
- [ ] T014 [US2] Refine persona system prompts in `src/nodes/judges.py` to enforce strict evidence citation (`evidence_id`)
- [ ] T015 [US2] Update `evaluate_criterion` in `src/nodes/judges.py` to handle persona-specific field expectations

**Checkpoint**: User Story 2 is functional - Judges now provide detailed, cited feedback with specialized fields.

---

## Phase 5: User Story 3 - Resilient Execution (Priority: P3)

**Goal**: Handle LLM schema violations and timeouts gracefully without halting the audit process.

**Independent Test**: Mock LLM failures (invalid JSON, timeouts) and verify the system retries 2 times before returning a fallback opinion.

### Tests for User Story 3

- [ ] T016 [P] [US3] Create unit tests for schema violation retry logic and final fallback in `tests/unit/test_judges.py`
- [ ] T017 [P] [US3] Create unit tests for exponential backoff during HTTP timeouts in `tests/unit/test_judges.py`

### Implementation for User Story 3

- [ ] T018 [US3] Implement recursive retry helper with "schema reminder" prompt injection per Principle VII.3 in `src/nodes/judges.py`
- [ ] T019 [US3] Implement exponential backoff for LLM calls in `src/nodes/judges.py`
- [ ] T020 [US3] Implement final fallback `JudicialOpinion` (score 3, error argument) in `src/nodes/judges.py` for terminal failures

**Checkpoint**: User Story 3 is functional - The judicial layer is now resilient to transient LLM errors.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T021 [P] Update `README.md` or `docs/` with details on Layer 2 architecture
- [ ] T022 [P] Finalize `quickstart.md` local execution guide instructions
- [ ] T023 Run `tests/harness/run_judicial_mock.py` to validate full Layer 2 flow end-to-end
- [ ] T024 Perform final code cleanup and ensure compliance with project constitution

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1 - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Phase 2.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Foundation for all judicial evaluations.
- **User Story 2 (P2)**: Extends US1 with citation and persona fields.
- **User Story 3 (P3)**: Adds resilience to the execution flow.

### Parallel Opportunities

- All tasks marked [P] can run in parallel if they target different files.
- Phase 3, 4, 5 tests [P] can be written in parallel.
- Once Foundational is done, work on different personas or resilience logic can be parallelized if separated into helper modules.

---

## Parallel Example: User Story 1

```bash
# Launch unit tests for US1
Task: "Create unit tests for persona prompt divergence (< 10% overlap) in tests/unit/test_judges.py"
Task: "Create unit test for judicial fan-out logic using Send in tests/unit/test_judges.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (The core 3-judge evaluation)
4. **STOP and VALIDATE**: Run `tests/integration/test_judicial_workflow.py`

### Incremental Delivery

1. Foundation ready.
2. Add US 1 → MVP judicial review.
3. Add US 2 → Grounded feedback with citations.
4. Add US 3 → Production-grade resilience.
