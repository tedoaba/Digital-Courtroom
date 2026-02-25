# Tasks: E2E LangGraph Orchestration & Edge Wiring

**Input**: Design documents from `/specs/011-e2e-langgraph-wiring/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Integration and unit tests are requested to verify SC-003 and SC-004.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 [NFR-002] Verify all existing node modules in `src/nodes/` are importable by running `uv run python -c "import src.nodes.detectives; import src.nodes.judges"`
- [ ] T002 Initialize `src/graph.py` with basic LangGraph imports and logger setup
- [ ] T003 [P] [NFR-001] Configure global `StructuredLogger` in `src/utils/logger.py` (if not already present) for node lifecycle events

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Update `AgentState` in `src/state.py` to include `re_eval_count`, `re_eval_needed`, and `final_report` per `data-model.md`
- [ ] T005 Implement `timeout_wrapper` decorator in `src/utils/orchestration.py` to enforce 300s layer limits (Research Decision 4)
- [ ] T006 Create `ErrorHandler` logic in `src/nodes/evidence_aggregator.py` (or new file) to capture and log non-fatal node errors
- [ ] T007 Create initial `ReportGenerator` shell in `src/nodes/report_generator.py`
- [ ] T008 [P] [FR-009] Implement `ManifestManager` in `src/utils/manifest.py` to handle `run_manifest.json` serialization per Constitution XVII.2

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Full Audit Pipeline Execution (Priority: P1) 🎯 MVP

**Goal**: Orchestrate the entire swarm (ContextBuilder -> Detectives -> Aggregator -> Judges -> Justice -> Report) via a single command.

**Independent Test**: Invoke `uv run audit --repo <URL> --spec <PDF>` and verify `audit/reports/.../Report.md` and `run_manifest.json` are generated.

### Implementation for User Story 1

- [ ] T009 [P] [US1] Define nodes for all Layer 1-3 components in `src/graph.py`
- [ ] T010 [US1] Wire Layer 1 Detective fan-out (ContextBuilder -> Detectives) and fan-in (Detectives -> Aggregator) in `src/graph.py`
- [ ] T011 [US1] Wire Layer 2 Judge fan-out (Aggregator -> Judges) and fan-in (Judges -> ChiefJustice) in `src/graph.py`
- [ ] T012 [US1] Wire Layer 3 (ChiefJustice -> ReportGenerator) final edges in `src/graph.py`
- [ ] T013 [US1] Implement full Markdown report rendering in `src/nodes/report_generator.py` per `contracts/cli_and_report.md`
- [ ] T014 [US1] Implement manifest serialization in `src/nodes/report_generator.py` using `ManifestManager` (from T008)
- [ ] T015 [US1] Create CLI entry point in `src/main.py` using the command schema from `contracts/cli_and_report.md`
- [ ] T016 [US1] Integration test for successful E2E run in `tests/integration/test_full_workflow.py`

**Checkpoint**: At this point, the core audit pipeline is functional (MVP reached).

---

## Phase 4: User Story 2 - Fault-Tolerant Forensic Routing (Priority: P2)

**Goal**: Handle node failures gracefully by routing through ErrorHandler and producing partial reports.

**Independent Test**: Mock failure in `VisionInspector` and verify `Report.md` contains "Node Failed: VisionInspector" note but still finishes.

### Implementation for User Story 2

- [ ] T017 [US2] Add conditional edges in `src/graph.py` to route node/layer exceptions to the `ErrorHandler`
- [ ] T018 [US2] Update `ReportGenerator` in `src/nodes/report_generator.py` to handle entries in `state["errors"]` and missing evidence
- [ ] T019 [US2] Implement node-level timeout enforcement using the wrapper from T005 in `src/graph.py`
- [ ] T020 [US2] Integration test for detective failure and partial report in `tests/integration/test_fault_tolerance.py`
- [ ] T021 [US2] Integration test for "Empty Repository" edge case in `tests/integration/test_fault_tolerance.py`

**Checkpoint**: System is robust against individual node failures.

---

## Phase 5: User Story 3 - Deterministic Parallel Synchronization (Priority: P3)

**Goal**: Ensure deterministic synchronization, re-evaluation loops, and manifest enforcement.

**Independent Test**: Verify judges are re-executed when `ChiefJustice` detects variance > 2 using a topographical trace.

### Implementation for User Story 3

- [ ] T019 [P] [US3] Implement high-variance re-evaluation logic in `src/nodes/justice.py` (ChiefJustice node)
- [ ] T020 [US3] Add conditional cycle edge from `ChiefJustice` back to `Judges` (max 1 retry) in `src/graph.py`
- [ ] T021 [US3] Implement synchronization barrier logic to ensure all nodes in a layer finish before the next layer starts (per FR-008)
- [ ] T022 [US3] Add unit test to verify graph topology (fan-out count) in `tests/unit/test_graph_wiring.py`

**Checkpoint**: All advanced orchestration features are complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T023 [P] Document E2E workflow and CLI options in `docs/orchestration.md`
- [ ] T024 Perform performance audit to ensure < 5min execution for standard repos (SC-001)
- [ ] T025 Run full `quickstart.md` validation on a clean environment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1 completion.
- **User Stories (Phase 3+)**: All depend on Phase 2. US1 is priority 1 (MVP).
- **Polish**: Depends on all user stories.

### Parallel Opportunities

- T003, T008, T019 can run in parallel with other tasks in their phases.
- Once Phase 2 is done, US1 work can start. US2 and US3 have some dependencies on US1 wiring but can be planned in parallel.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phases 1 & 2.
2. Complete all US1 tasks (T008-T014).
3. **STOP and VALIDATE**: Test with a real repo/spec.

### Incremental Delivery

1. Foundation -> MVP (US1) -> Fault-Tolerance (US2) -> Advanced Synchronization (US3) -> Polish.
2. Each phase is independently testable.
