# Tasks: Parallel Detective Agents (Layer 1)

**Input**: Design documents from `/specs/006-parallel-detectives/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are requested in the feature specification (Unit tests with 100% pass rate SC-001).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project structure as defined in plan.md
- Source: `src/`
- Tests: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize directory structure for detectives in `src/nodes/` and `src/tools/`
- [ ] T002 [P] Create `__init__.py` files in `src/nodes/`, `src/tools/`, `tests/unit/nodes/`, and `tests/unit/tools/`
- [ ] T003 Ensure `uv` environment has `docling`, `gitingest`, and `pydantic` installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Verify state consolidation of `Evidence`, `Commit`, and `ASTFinding` in `src/state.py`
- [ ] T005 Update `merge_evidences` reducer in `src/state.py` to handle the updated `Evidence` schema
- [ ] T006 Update `AgentState` in `src/state.py` to ensure `evidences` and `errors` fields match `data-model.md`
- [ ] T007 Define shared timeout and logging utility constants for detectives in `src/config.py` (60s limit)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - RepoInvestigator (Priority: P1) 🎯 MVP

**Goal**: Implement `RepoInvestigator` for Git cloning and AST forensic analysis.

**Independent Test**: Invoke `RepoInvestigator` node with a test repository URL and verify it returns `Evidence` objects containing AST findings.

### Tests for User Story 1

- [ ] T008 [P] [US1] Create unit tests for `repo_tools` in `tests/unit/tools/test_repo_tools.py` (mocking git and subprocess)
- [ ] T009 [P] [US1] Create unit tests for `RepoInvestigator` node in `tests/unit/nodes/test_detectives.py`

### Implementation for User Story 1

- [ ] T010 [US1] Implement `repo_tools.py` with `tempfile` isolation and AST parsing logic in `src/tools/repo_tools.py`
- [ ] T011 [US1] Implement `RepoInvestigator` node logic with 60s timeout and error handling in `src/nodes/detectives.py`
- [ ] T012 [US1] Add structured logging for `RepoInvestigator` duration and file count per FR-009

**Checkpoint**: User Story 1 (RepoInvestigator) is functional and testable independently.

---

## Phase 4: User Story 2 - DocAnalyst (Priority: P1)

**Goal**: Implement `DocAnalyst` for PDF text extraction and architectural claim verification.

**Independent Test**: Provide a sample PDF to `DocAnalyst` and verify it extracts text chunks and citations into `Evidence` objects.

### Tests for User Story 2

- [ ] T013 [P] [US2] Create unit tests for `doc_tools` in `tests/unit/tools/test_doc_tools.py` (mocking docling)
- [ ] T014 [P] [US2] Create unit tests for `DocAnalyst` node in `tests/unit/nodes/test_detectives.py`

### Implementation for User Story 2

- [ ] T015 [US2] Implement `doc_tools.py` for PDF to Markdown conversion and chunking in `src/tools/doc_tools.py`
- [ ] T016 [US2] Implement `DocAnalyst` node logic with 60s timeout and error handling in `src/nodes/detectives.py`
- [ ] T017 [US2] Add structured logging for `DocAnalyst` duration and page count per FR-009

**Checkpoint**: User Story 2 (DocAnalyst) is functional and testable independently.

---

## Phase 5: User Story 3 - VisionInspector (Priority: P2)

**Goal**: Implement `VisionInspector` for classifying architectural diagrams via Multimodal LLM.

**Independent Test**: Provide diagram images to `VisionInspector` and verify it returns classification `Evidence` ('Parallel Flow', etc.).

### Tests for User Story 3

- [ ] T018 [P] [US3] Create unit tests for `vision_tools` in `tests/unit/tools/test_vision_tools.py` (mocking LLM and image extraction)
- [ ] T019 [P] [US3] Create unit tests for `VisionInspector` node in `tests/unit/nodes/test_detectives.py`

### Implementation for User Story 3

- [ ] T020 [US3] Implement `vision_tools.py` for diagram classification using Multimodal LLM in `src/tools/vision_tools.py`
- [ ] T021 [US3] Implement `VisionInspector` node logic with 60s timeout and error handling in `src/nodes/detectives.py`
- [ ] T022 [US3] Add structured logging for `VisionInspector` duration and image count per FR-009

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T023 [P] Validate all detective nodes return `found=False` on failures/timeouts without crashing system
- [ ] T024 [P] Verify no interpretation or scoring logic is present in any detective node (Fact-only Principle)
- [ ] T025 [P] Performance optimization: Ensure all parallel executions fit within 60-second window
- [ ] T026 Update `quickstart.md` with verified execution examples

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup. BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational completion.
- **Polish (Final Phase)**: Depends on completion of all stories.

### User Story Dependencies

- **User Story 1 (P1)**: Independent after Phase 2.
- **User Story 2 (P1)**: Independent after Phase 2.
- **User Story 3 (P2)**: Independent after Phase 2.

### Parallel Opportunities

- T002, T003 can run in parallel.
- All tasks marked [P] in Phases 3, 4, 5 (tests and tools design) can run in parallel within their stories.
- Once Phase 2 is done, implementation of US1, US2, and US3 can proceed in parallel.

---

## Parallel Example: MVP (User Story 1)

```bash
# Prepare tests in parallel
Task: "Create unit tests for repo_tools in tests/unit/tools/test_repo_tools.py"
Task: "Create unit tests for RepoInvestigator node in tests/unit/nodes/test_detectives.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2 (Scaffolding and State alignment).
2. Complete Phase 3 (RepoInvestigator).
3. **STOP and VALIDATE**: Verify RepoInvestigator works with real/mock repos.

### Incremental Delivery

1. Deploy RepoInvestigator (MVP).
2. Add DocAnalyst (Story 2).
3. Add VisionInspector (Story 3).
