# Tasks: Bounded-Concurrency Multi-Agent Evaluation

**Input**: Design documents from `/specs/012-bounded-agent-eval/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Included as per constitutional requirement for TDD.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize environment with `uv` and ensure `tenacity` is installed
- [ ] T002 [P] Create placeholder files for new tests: `tests/unit/test_concurrency_controller.py` and `tests/integration/test_bounded_eval.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Update `JudicialSettings` in `src/config.py` with new Pydantic fields from data-model.md
- [ ] T004 Setup centralized logging for concurrency events ("Queueing", "Acquired", "Release") in `src/utils/logging.py`
- [ ] T005 [P] Define `ConcurrencyController` or shared semaphore in `src/nodes/judicial_nodes.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Stable Parallel Evaluation (Priority: P1) 🎯 MVP

**Goal**: Enforce global concurrency limit with semaphore and retry logic to prevent 429 errors.

**Independent Test**: Configure concurrency to 5. Trigger 3 agents x 10 dimensions. Verify max 5 active calls in logs.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T006 [P] [US1] Implement unit tests for semaphore lock/unlock in `tests/unit/test_concurrency_controller.py`
- [ ] T007 [P] [US1] Implement integration test for 429 retry behavior in `tests/integration/test_bounded_eval.py`

### Implementation for User Story 1

- [ ] T008 [US1] Implement `asyncio.Semaphore` throttling in `src/nodes/judicial_nodes.py`
- [ ] T009 [US1] Apply `tenacity` retry decorator with exponential backoff to LLM calls in `src/nodes/judicial_nodes.py`
- [ ] T010 [US1] Add "Queueing..." and "Acquired..." log markers around semaphore blocks

**Checkpoint**: User Story 1 is functional: evaluations are throttled and retried on failure.

---

## Phase 4: User Story 2 - Performance Optimization (Priority: P2)

**Goal**: Allow fine-grained control over throughput via environment configuration.

**Independent Test**: Modify `MAX_CONCURRENT_LLM_CALLS` in `.env` and verify scale of execution.

### Implementation for User Story 2

- [ ] T011 [US2] Create or update `.env` with variables from `quickstart.md`
- [ ] T012 [US2] Ensure `JudicialSettings` correctly injects configuration into the concurrency semaphore

**Checkpoint**: System is now tunable without code changes.

---

## Phase 5: User Story 3 - Structured Evaluation Batching (Priority: P3)

**Goal**: Further reduce overhead by consolidating dimension evaluations into single calls.

**Independent Test**: Enable batching. Verify a judge makes 1 call for 10 dimensions instead of 10 individual calls.

### Tests for User Story 3

- [ ] T013 [P] [US3] Implement parsing tests for partial JSON responses in `tests/unit/test_batch_parsing.py`

### Implementation for User Story 3

- [ ] T014 [US3] Update prompt template in `src/nodes/judicial_nodes.py` to request structured JSON list of opinions
- [ ] T015 [US3] Implement partial success logic: accept returned dimensions and trigger individual retries for missing ones

**Checkpoint**: Batching reduces request count while maintaining reliability for failed items.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [ ] T016 [P] Update `README.md` with new `JudicialSettings` configuration documentation
- [ ] T017 Run all validation steps outlined in `quickstart.md`
- [ ] T018 Code cleanup: Ensure all semaphore releases happen in `finally` blocks

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1 completion. Blocks all User Stories.
- **User Stories (Phase 3+)**: All depend on Phase 2. US1 is P1 (MVP).
- **Polish (Final Phase)**: Depends on all user stories being complete.

### Parallel Opportunities

- T002, T005 can run in parallel with other tasks in their phases.
- Once Phase 2 is done, US1 and US2 can be worked on in parallel (though US2 is small).
- T006 and T007 (Tests for US1) can be written in parallel.

---

## Parallel Example: User Story 1

```bash
# Writing tests in parallel:
Task: "Implement unit tests for semaphore lock/unlock in tests/unit/test_concurrency_controller.py"
Task: "Implement integration test for 429 retry behavior in tests/integration/test_bounded_eval.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup + Foundational.
2. Complete US1 (Semaphore + Retry).
3. **VALIDATE**: Run a full evaluation and check for zero 429 errors.
