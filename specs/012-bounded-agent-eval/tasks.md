# Tasks: Bounded-Concurrency Multi-Agent Evaluation

**Input**: Design documents from `/specs/012-bounded-agent-eval/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Included as per constitutional requirement for TDD.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize environment with `uv` and ensure `tenacity` is installed
- [ ] T002 [P] Create placeholder files for new tests: `tests/unit/test_concurrency_controller.py`, `tests/unit/test_config_sync.py`, and `tests/integration/test_bounded_eval.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Update `JudicialSettings` in `src/config.py` with new Pydantic fields from data-model.md (Default `retry_max_attempts=3`)
- [ ] T004 Setup centralized logging for concurrency events ("Queueing", "Acquired", "Release", "Timeout") in `src/utils/logging.py`
- [ ] T005 [P] Define `ConcurrencyController` or shared semaphore in `src/nodes/judicial_nodes.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Stable Parallel Evaluation (Priority: P1) 🎯 MVP

**Goal**: Enforce global concurrency limit with semaphore, retry logic (max 3), and timeouts to prevent 429 errors and hung requests.

**Independent Test**: Configure concurrency to 5. Trigger 3 agents x 10 dimensions. Verify max 5 active calls and proper timeout recovery.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T006 [P] [US1] Implement unit tests for semaphore lock/unlock in `tests/unit/test_concurrency_controller.py`
- [ ] T007 [P] [US1] Implement integration test for 429 retry behavior (verified at 3 attempts max) in `tests/integration/test_bounded_eval.py`
- [ ] T008 [P] [US1] Implement unit test for request timeouts in `tests/unit/test_timeouts.py`

### Implementation for User Story 1

- [ ] T009 [US1] Implement `asyncio.Semaphore` throttling in `src/nodes/judicial_nodes.py`
- [ ] T010 [US1] Apply `tenacity` retry decorator with exponential backoff (multiplier=1, min=1, max=60, stop=3) to LLM calls in `src/nodes/judicial_nodes.py`
- [ ] T011 [US1] Wrap LLM calls in `asyncio.wait_for` with configurable timeout to handle hung requests
- [ ] T012 [US1] Add "Queueing...", "Acquired...", and "Timeout" log markers around semaphore and LLM blocks

**Checkpoint**: User Story 1 is functional: evaluations are throttled, retried (max 3), and timed out if hung.

---

## Phase 4: User Story 2 - Performance Optimization (Priority: P2)

**Goal**: Allow fine-grained control over throughput via environment configuration.

**Independent Test**: Modify `MAX_CONCURRENT_LLM_CALLS` in `.env` and verify scale of execution.

### Tests for User Story 2

- [ ] T013 [P] [US2] Implement unit tests in `tests/unit/test_config_sync.py` to verify `JudicialSettings` correctly loads and validates environment variables

### Implementation for User Story 2

- [ ] T014 [US2] Create or update `.env` with variables from `quickstart.md`
- [ ] T015 [US2] Ensure `JudicialSettings` correctly injects configuration into the concurrency semaphore and retry policy

**Checkpoint**: System is now tunable without code changes.

---

## Phase 5: User Story 3 - Structured Evaluation Batching (Priority: P3)

**Goal**: Further reduce overhead by consolidating dimension evaluations into single calls.

**Independent Test**: Enable batching. Verify a judge makes 1 call for 10 dimensions instead of 10 individual calls.

### Tests for User Story 3

- [ ] T016 [P] [US3] Implement parsing tests for partial JSON responses in `tests/unit/test_batch_parsing.py`

### Implementation for User Story 3

- [ ] T017 [US3] Update prompt template in `src/nodes/judicial_nodes.py` to request structured JSON list of opinions
- [ ] T018 [US3] Implement partial success logic: accept returned dimensions and trigger individual retries for missing ones

**Checkpoint**: Batching reduces request count while maintaining reliability for failed items.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [ ] T019 [P] Update `README.md` with new `JudicialSettings` configuration documentation
- [ ] T020 Run all validation steps outlined in `quickstart.md`
- [ ] T021 Code cleanup: Ensure all semaphore releases and timeout handlers are robust

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1 completion. Blocks all User Stories.
- **User Stories (Phase 3+)**: All depend on Phase 2. US1 is P1 (MVP).
- **Polish (Final Phase)**: Depends on all user stories being complete.

### Parallel Opportunities

- T002, T005, T006, T007, T008, T013, T016 can run in parallel with other tasks in their phases.

---

## Parallel Example: User Story 1

```bash
# Writing tests in parallel:
Task: "Implement unit tests for semaphore lock/unlock in tests/unit/test_concurrency_controller.py"
Task: "Implement integration test for 429 retry behavior in tests/integration/test_bounded_eval.py"
Task: "Implement unit test for request timeouts in tests/unit/test_timeouts.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup + Foundational.
2. Complete US1 (Semaphore + Retry + Timeouts).
3. **VALIDATE**: Run a full evaluation and check for zero 429 errors and successful timeout recovery.
