# Tasks: Evidence Aggregation Sync Node (Layer 1.5)

**Input**: Design documents from `/specs/007-evidence-aggregator/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Tests are included as requested in the feature specification and to verify forensic accuracy.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Includes exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 [P] Verify project dependencies in `pyproject.toml` (langgraph, pydantic)
- [x] T002 Ensure node directory exists at `src/nodes/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Update `src/state.py` with `merge_evidences` reducer and ensure `AgentState` supports `evidences` field
- [x] T004 [P] Implement internal path validation utility within `src/nodes/evidence_aggregator.py` for sandbox safety (FR-008)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Consolidate Detective Evidence (Priority: P1) 🎯 MVP

**Goal**: Merge parallel detective outputs (`repo`, `docs`, `vision`) into a unified state and deduplicate findings via `evidence_id`.

**Independent Test**: Provide multiple mock evidence dictionaries with overlapping `evidence_id` and unique IDs, verify unified output length and content.

### Tests for User Story 1

- [x] T005 [P] [US1] Create unit tests for basic evidence merging and deduplication in `tests/unit/test_evidence_aggregator.py`

### Implementation for User Story 1

- [x] T006 [US1] Implement `aggregator_node` skeleton and basic source merging logic in `src/nodes/evidence_aggregator.py`
- [x] T007 [US1] Implement `evidence_id` deduplication within each source list in `src/nodes/evidence_aggregator.py` (FR-006)
- [x] T008 [US1] Ensure the output provides a "clean" dictionary ready for Judge nodes (FR-007)

**Checkpoint**: User Story 1 complete - system can now synchronize parallel detective flows.

---

## Phase 4: User Story 2 - Cross-Reference File Paths (Priority: P1)

**Goal**: Verify if file paths mentioned in documentation actually exist in the repository and flag discrepancies as hallucinations.

**Independent Test**: Mock `docs` evidence citing a non-existent path and `repo` evidence listing real paths; verify a `DOCUMENT_CLAIM` evidence item with `found=False` is created.

### Tests for User Story 2

- [x] T009 [P] [US2] Add unit tests for path cross-referencing and "Hallucinated Path" generation in `tests/unit/test_evidence_aggregator.py`

### Implementation for User Story 2

- [x] T010 [US2] Implement logic to extract file manifest from `repo` evidence content in `src/nodes/evidence_aggregator.py`
- [x] T011 [US2] Implement path sanitization and cross-reference logic against the repo manifest in `src/nodes/evidence_aggregator.py`
- [x] T012 [US2] Implement generation of `DOCUMENT_CLAIM` evidence for hallucinated paths in `src/nodes/evidence_aggregator.py` (FR-004)

**Checkpoint**: User Story 2 complete - system can now detect documentation hallucinations.

---

## Phase 5: User Story 3 - Missing Source Handling (Priority: P2)

**Goal**: Warn operators if 'vision' is missing and log errors to `state.errors` if 'repo' or 'docs' are entirely absent.

**Independent Test**: Run node with missing `vision` key (check logs) and then with missing `repo` key (verify error appended to `state.errors`).

### Tests for User Story 3

- [x] T013 [P] [US3] Add unit tests for missing source validation and error handling in `tests/unit/test_evidence_aggregator.py`

### Implementation for User Story 3

- [x] T014 [US3] Implement mandatory source validation (repo, docs) and error logging to `state.errors` in `src/nodes/evidence_aggregator.py` (FR-005)
- [x] T015 [US3] Implement warning log for missing `vision` evidence in `src/nodes/evidence_aggregator.py`

**Checkpoint**: All user stories complete - robust fan-in synchronization is established.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and integration verification

- [x] T016 [P] Implement integration test for complete graph fan-in behavior in `tests/integration/test_graph_sync.py`
- [x] T017 [P] Perform overhead benchmark to ensure <50ms processing time (SC-002)
- [x] T018 [P] Update `specs/007-evidence-aggregator/quickstart.md` with finalized implementation examples

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - US1 and US2 can proceed in parallel once T003/T004 are done.
  - US3 depends on the node structure established in US1.

### Parallel Opportunities

- T001 and T002 in Setup.
- T004 (Utility logic) can be worked on in parallel with T003 (State schema).
- All tests marked [P] can run in parallel with their respective implementation tasks.
- Integration tests (T016) can be prepared while implementation progresses.

---

## Implementation Strategy

1. **Phase 1 & 2**: Establish the contract (State) and the safety utility (Paths).
2. **Phase 3 (MVP)**: Get the basic merge working. This is the "Happy Path" for the graph.
3. **Phase 4**: Add the "Forensic" value (Hallucination detection).
4. **Phase 5**: Add robustness (Error handling).
5. **Phase 6**: Verify integration and performance.
