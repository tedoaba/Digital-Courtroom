# Tasks: Bounded-Concurrency Multi-Agent Evaluation

**Input**: Design documents from `/specs/012-bounded-agent-eval/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Included as per constitutional requirement for TDD.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize environment with `uv` and ensure `tenacity` is installed
- [x] T002 [P] Create placeholder files for new tests: `tests/unit/test_concurrency_controller.py`, `tests/unit/test_config_sync.py`, `tests/unit/test_timeouts.py`, `tests/unit/test_batch_parsing.py`, and `tests/integration/test_bounded_eval.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Update `JudicialSettings` in `src/config.py` with new Pydantic fields from data-model.md: add `max_concurrent_llm_calls` (int, default=5, `ge=1, le=50`), `retry_max_attempts` (int, default=3), `llm_call_timeout` (float, default=120.0), `batching_enabled` (bool, default=False). Raise `ValueError` at startup if `max_concurrent_llm_calls < 1` per FR-001
- [x] T004 Setup centralized logging helpers in `src/utils/logging.py` that emit structured JSON events per SC-003: `queueing`, `acquired`, `released`, `retry`, `timeout` — each with agent name, dimension ID, and slot/queue counters
- [x] T005 [P] Define `ConcurrencyController` or shared semaphore in `src/nodes/judicial_nodes.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Stable Parallel Evaluation (Priority: P1) 🎯 MVP

**Goal**: Enforce global concurrency limit with semaphore, retry logic (max 3), and timeouts to prevent 429 errors and hung requests.

**Independent Test**: Configure concurrency to 5. Trigger 3 agents x 10 dimensions. Verify max 5 active calls and proper timeout recovery.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T006 [P] [US1] Implement unit tests for semaphore lock/unlock in `tests/unit/test_concurrency_controller.py`
- [x] T007 [P] [US1] Implement integration test for 429 retry behavior (verified at 3 attempts max, targeting status codes 429/502/503/408) in `tests/integration/test_bounded_eval.py`
- [x] T008 [P] [US1] Implement unit test for request timeouts (`asyncio.TimeoutError` after `LLM_CALL_TIMEOUT`) in `tests/unit/test_timeouts.py`

### Implementation for User Story 1

- [x] T009 [US1] Implement `asyncio.Semaphore` throttling using `async with` context manager (FR-007) to guarantee slot release on success, error, and timeout in `src/nodes/judicial_nodes.py`
- [x] T010 [US1] Apply `tenacity` retry decorator with exponential backoff (`delay = min(1s * 2^(n-1) + jitter, 60s)`, jitter ∈ [0, 0.5s], stop=3) targeting HTTP status codes 429, 502, 503, 408 in `src/nodes/judicial_nodes.py`
- [x] T011 [US1] Wrap LLM calls in `asyncio.wait_for(timeout=settings.llm_call_timeout)` to handle hung requests; on `TimeoutError`, log WARNING and retry per FR-002 in `src/nodes/judicial_nodes.py`
- [x] T012 [US1] Emit structured JSON log events (per SC-003 formats) for queueing, acquired, released, retry, and timeout via helpers from T004 in `src/nodes/judicial_nodes.py`
- [x] T013 [US1] Log active concurrency limit at job start (INFO) and enforce that `MAX_CONCURRENT_LLM_CALLS` is immutable during an active job per FR-009 in `src/nodes/judicial_nodes.py`

**Checkpoint**: User Story 1 is functional: evaluations are throttled, retried (max 3), timed out if hung, and fully observable via structured logs.

---

## Phase 4: User Story 2 - Performance Optimization (Priority: P2)

**Goal**: Allow fine-grained control over throughput via environment configuration.

**Independent Test**: Modify `MAX_CONCURRENT_LLM_CALLS` in `.env` and verify scale of execution.

### Tests for User Story 2

- [x] T014 [P] [US2] Implement unit tests in `tests/unit/test_config_sync.py` to verify `JudicialSettings` correctly loads, validates (range 1–50), and rejects invalid environment variables

### Implementation for User Story 2

- [x] T015 [US2] Create or update `.env` with all 6 variables from `quickstart.md` (including `LLM_CALL_TIMEOUT`)
- [x] T016 [US2] Ensure `JudicialSettings` correctly injects configuration into the concurrency semaphore, retry policy, and timeout wrapper at initialization

**Checkpoint**: System is now tunable without code changes.

---

## Phase 5: User Story 3 - Structured Evaluation Batching (Priority: P3)

**Goal**: Further reduce overhead by consolidating dimension evaluations into single calls.

**Independent Test**: Enable batching. Verify a judge makes 1 call for 10 dimensions instead of 10 individual calls.

### Tests for User Story 3

- [x] T017 [P] [US3] Implement parsing tests for partial JSON responses and corrupt/malformed entries in `tests/unit/test_batch_parsing.py`

### Implementation for User Story 3

- [x] T018 [US3] Update prompt template in `src/nodes/judicial_nodes.py` to request structured JSON list of opinions per `data-model.md § Batching Contract`
- [x] T019 [US3] Implement partial success logic: accept valid dimensions, discard malformed/corrupt entries (log WARNING with raw payload), and trigger individual retries for both missing and invalid dimensions in `src/nodes/judicial_nodes.py`
- [x] T020 [US3] Implement provider fallback: if provider does not support structured output, fall back to individual-dimension calls even when `BATCHING_ENABLED=true` per FR-004 in `src/nodes/judicial_nodes.py`

**Checkpoint**: Batching reduces request count while maintaining reliability for failed and corrupt items.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [x] T021 [P] Update `README.md` with new `JudicialSettings` configuration documentation (all 6 env vars)
- [x] T022 Run all validation steps outlined in `quickstart.md`
- [x] T023 Code cleanup: Verify all semaphore releases use `async with` or `try/finally`, confirm structured JSON logs match SC-003 formats

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1 completion. Blocks all User Stories.
- **User Stories (Phase 3+)**: All depend on Phase 2. US1 is P1 (MVP).
- **Polish (Final Phase)**: Depends on all user stories being complete.

### Parallel Opportunities

- T002, T005 can run in parallel within their phases.
- T006, T007, T008 (US1 tests) can all run in parallel.
- T014 (US2 tests), T017 (US3 tests) can run in parallel with other tasks in their phases.

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
2. Complete US1 (Semaphore + Retry + Timeouts + Structured Logging + FR-009).
3. **VALIDATE**: Run a full evaluation and check for zero 429 errors, successful timeout recovery, and correct structured JSON log output.
