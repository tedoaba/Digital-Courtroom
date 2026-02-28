# Tasks: Operation Ironclad Swarm — Production-Grade Hardening

**Input**: Design documents from `/specs/013-ironclad-hardening/`
**Prerequisites**: [plan.md](file:///c:/Users/user/tedoaba/Digital-Courtroom/specs/013-ironclad-hardening/plan.md), [spec.md](file:///c:/Users/user/tedoaba/Digital-Courtroom/specs/013-ironclad-hardening/spec.md), [research.md](file:///c:/Users/user/tedoaba/Digital-Courtroom/specs/013-ironclad-hardening/research.md), [data-model.md](file:///c:/Users/user/tedoaba/Digital-Courtroom/specs/013-ironclad-hardening/data-model.md)

**Tests**: Generation of test tasks is required as per implementation plan's commitment to TDD (Constitution Check Principle II).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure for `src/judicial/` and `src/utils/` per `plan.md`
- [x] T002 [P] Update `pyproject.toml` with `cryptography`, `rich`, `psutil`, and `langsmith` dependencies
- [x] T003 [P] Configure LangSmith project environment variables in `.env.example`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and state models that MUST be complete before user stories begin

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement `HardenedConfig` Pydantic model in `src/config.py` per `data-model.md`
- [x] T005 Create `CircuitBreakerState` and `EvidenceChain` models in `src/state.py`
- [x] T006 [P] Create `TraceAuditTrail` schema in `src/utils/observability.py`
- [x] T007 [P] Initialize base `src/utils/security.py` with empty `HardenedVault` and `SandboxEnvironment` classes
- [x] T008 [P] Initialize `src/utils/orchestration.py` with `CircuitBreaker` skeleton

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Hardened Execution & Configuration (Priority: P1) 🎯 MVP

**Goal**: Zero hardcoded configuration and secure tool execution in sandboxed environments.

**Independent Test**: Verify system fails to start without complete `.env` and verify detective tools cannot write outside ephemeral directories.

### Tests for User Story 1

- [x] T009 [P] [US1] Create unit tests for vault encryption/decryption in `tests/unit/test_security.py`
- [x] T010 [P] [US1] Create unit tests for sandbox resource limiting in `tests/unit/test_security.py`
- [x] T011 [US1] Create integration test for config loading in `tests/integration/test_config.py`

### Implementation for User Story 1

- [x] T012 [P] [US1] Implement `HardenedVault` with AES-256 (Fernet) in `src/utils/security.py`
- [x] T013 [P] [US1] Implement `SandboxEnvironment` with `psutil` resource monitoring (512MB RAM, 1 CPU core) in `src/utils/security.py`
- [x] T014 [US1] Implement Pydantic-based input/output validation and sanitization logic in `src/utils/security.py`
- [x] T015 [US1] Refactor `src/config.py` to pull all model names and endpoints from environment variables
- [x] T016 [US1] Audit and remove all hardcoded strings from existing nodes in `src/nodes/`
- [x] T017 [US1] Update detective nodes to execute tools via `SandboxEnvironment`

**Checkpoint**: User Story 1 is functional. System is hardened against basic configuration leaks and tool escapes.

---

## Phase 4: User Story 2 - Real-time Swarm Observability (Priority: P1)

**Goal**: Real-time TUI dashboard and comprehensive LangSmith tracing for all node executions.

**Independent Test**: Run a swarm execution and observe live updates in the TUI while verifying traces appear in LangSmith.

### Tests for User Story 2

- [x] T018 [P] [US2] Create unit tests for dashboard state updates in `tests/unit/test_observability.py`
- [x] T019 [P] [US2] Verify LangSmith instrumentation wrapper in `tests/unit/test_observability.py`

### Implementation for User Story 2

- [x] T020 [P] [US2] Implement real-time TUI dashboard using `rich.live` with interactive keys (`p`, `r`, `c`) in `src/utils/observability.py`
- [x] T021 [US2] Apply `@traceable` instrumentation to all graph nodes in `src/nodes/`
- [x] T022 [US2] Implement structured JSON trace export in `src/utils/observability.py`
- [x] T023 [US2] Update `src/main.py` entry point to support the `--dashboard` flag

**Checkpoint**: User Story 2 is functional. Swarm execution is fully transparent and auditable.

---

## Phase 5: User Story 3 - Report Integrity & Graph Resilience (Priority: P2)

**Goal**: Cryptographic evidence chaining and circuit breaker patterns for API resilience.

**Independent Test**: Simulate 3 API failures to trigger circuit breaker; modify an evidence file to trigger hash chain failure.

### Tests for User Story 3

- [x] T024 [P] [US3] Create unit tests for `CircuitBreaker` state transitions (Closed -> Open) in `tests/unit/test_resilience.py`
- [x] T025 [P] [US3] Create unit tests for sequential SHA-256 hashing in `tests/unit/test_security.py`
- [x] T026 [US3] Create integration test for disaster recovery rollback in `tests/integration/test_disaster_recovery.py`

### Implementation for User Story 3

- [x] T027 [P] [US3] Implement sequential SHA-256 hash chain logic in `src/utils/security.py`
- [x] T028 [US3] Implement `CircuitBreaker` logic (3-failure threshold, 1-success recovery) in `src/utils/orchestration.py`
- [x] T029 [US3] Integrate `CircuitBreaker` into LangGraph orchestration nodes and implement cascading failure detection for core streams (FR-011) in `src/utils/orchestration.py`
- [x] T030 [US3] Implement automated state rollback for orchestration recovery in `src/utils/orchestration.py`
- [x] T031 [US3] Implement evidence verification utility method in `src/utils/security.py`

**Checkpoint**: User Story 3 is functional. The system is resilient to API outages and ensures evidence integrity.

---

## Phase 6: User Story 4 - Judicial Dialectics Abstraction (Priority: P2)

**Goal**: Separate reasoning strategies and scoring rubrics from core orchestration logic.

**Independent Test**: Swap a reasoning strategy in the judicial layer and verify the output reflects the new strategy without changing nodes.

### Tests for User Story 4

- [x] T032 [P] [US4] Create unit tests for strategy swapping in `tests/unit/test_judicial.py`
- [x] T033 [US4] Create unit tests for multi-factorial rubric scoring in `tests/unit/test_judicial.py`

### Implementation for User Story 4

- [x] T034 [P] [US4] Implement `BaseReasoningStrategy` in `src/judicial/layer.py`
- [x] T035 [P] [US4] Implement concrete reasoning strategies in `src/judicial/strategies.py`
- [x] T036 [P] [US4] Implement rubric loading and scoring logic in `src/judicial/rubrics.py`
- [x] T037 [US4] Refactor `src/nodes/judicial_nodes.py` to delegate to `src/judicial/layer.py`

**Checkpoint**: User Story 4 is functional. Judicial logic is modular and maintainable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, documentation, and performance tuning.

- [x] T038 [P] Update `README.md` with hardening features and CLI usage
- [x] T039 Optimize TUI refresh rate and resource consumption in `src/utils/observability.py`
- [x] T040 Perform final security audit for credential leakage in logs
- [x] T041 Run `quickstart.md` validation to ensure project is ready for handover
- [x] T042 [P] Cleanup temporary test files and artifacts
- [x] T043 Perform recovery performance benchmark to verify < 10s recovery (SC-006)
- [x] T044 Verify zero mock implementation in production node path (SC-007)
- [x] T045 [US3] Implement cryptographic mid-execution failure recovery and partial reporting in `src/utils/security.py`
- [x] T046 [US1] Implement 50ms latency check for cryptographic operations in security unit tests

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Setup (Phase 1)**: Must complete first.
2. **Foundational (Phase 2)**: Depends on Phase 1. Blocks all subsequent phases.
3. **User Stories (Phases 3 & 4)**: Priority P1. Can be executed in parallel after Phase 2.
4. **User Stories (Phases 5 & 6)**: Priority P2. Depends on Phase 2. Recommended to follow P1 completion.
5. **Polish (Phase 7)**: Depends on completion of all required user stories.

### Parallel Opportunities

- [P] tasks within any phase can be executed concurrently.
- User Story 1 and User Story 2 can be developed in parallel by separate developers.
- User Story 3 and User Story 4 can be developed in parallel.

---

## Implementation Strategy

### MVP First (User Stories 1 & 2)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (Hardened Execution).
3. Complete Phase 4 (Observability).
4. **VALIDATE**: Ensure the system runs securely with visible tracing.

### Incremental Delivery

- Add Phase 5 (Resilience & Integrity) to ensure production stability.
- Add Phase 6 (Judicial Abstraction) for long-term maintainability.
- Final Polish and Audit.
