# Tasks: Sandboxed Forensic Execution Interfaces

**Input**: Design documents from `/specs/004-forensic-tools-sandbox/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are requested in the spec (User Scenarios & Testing section) and are included in the phases below.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- All tools in `src/tools/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure: `src/tools/`, `src/models/`, `tests/unit/tools/`, `tests/integration/tools/`
- [ ] T002 Initialize project dependencies (`docling`, `pydantic`) using `uv add`
- [ ] T003 [P] Configure `ruff` for linting and formatting in `pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Implement `ToolResult` generic wrapper in `src/tools/base.py`
- [ ] T005 Implement foundational models (`Evidence`, `Commit`) in `src/models/forensic.py`
- [ ] T006 [P] Implement URL validation utility with domain/protocol whitelist in `src/tools/utils.py` (FR-006)
- [ ] T007 [P] Implement common timeout and disk limit decorators/utilities in `src/tools/utils.py` (FR-002, FR-009)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Secure External Evidence Collection (Priority: P1) 🎯 MVP

**Goal**: Retrieve external source code and history into an isolated environment without side effects.

**Independent Test**: Provide a valid Git URL and verify `repo_tools.py` clones it to a temp dir, extracts history as `Commit` objects, and cleans up.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T008 [P] [US1] Unit tests for `clone_repo` (success, timeout, injection attempt) in `tests/unit/tools/test_repo_tools.py`
- [ ] T009 [P] [US1] Unit tests for `extract_git_history` in `tests/unit/tools/test_repo_tools.py`
- [ ] T010 [US1] Integration test for "Secure External Evidence Collection" scenario in `tests/integration/tools/test_forensic_suite.py`

### Implementation for User Story 1

- [ ] T011 [US1] Implement `clone_repo` using `tempfile.TemporaryDirectory` and `subprocess` list-args in `src/tools/repo_tools.py` (FR-001, FR-003)
- [ ] T012 [US1] Implement `extract_git_history` to return `List[Commit]` with hash, author, date, message in `src/tools/repo_tools.py`
- [ ] T013 [US1] Ensure `repo_tools.py` uses data-derivation timestamps for determinism (FR-008)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Safe Structural Code Analysis (Priority: P1)

**Goal**: Scan source code for structural patterns (classes, functions, framework calls) without executing it.

**Independent Test**: Provide a file with `BaseModel` and `StateGraph` definitions and a "poisonous" top-level `os.system` call; verify structure is extracted and poison is NOT executed.

### Tests for User Story 2

- [ ] T014 [P] [US2] Unit tests for `scan_repository` with valid and invalid syntax in `tests/unit/tools/test_ast_tools.py`
- [ ] T015 [P] [US2] Security test for Zero-Execution guarantee (poison script test) in `tests/unit/tools/test_ast_tools.py` (SC-004)

### Implementation for User Story 2

- [ ] T016 [P] [US2] Implement `ASTFinding` Pydantic model in `src/models/forensic.py`
- [ ] T017 [US2] Implement `scan_repository` using `ast.parse` and `ast.walk` in `src/tools/ast_tools.py` (FR-004)
- [ ] T018 [US2] Add support for detecting `StateGraph` wiring and `BaseModel` fields specifically (FR-004)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Document and Visual Evidence Extraction (Priority: P2)

**Goal**: Extract text and embedded images from PDF reports for automated verification.

**Independent Test**: Provide a PDF with known text and 1 image; verify extraction returns correct text chunks and saved image path.

### Tests for User Story 3

- [ ] T019 [P] [US3] Unit tests for `ingest_pdf` (success, corrupt PDF) in `tests/unit/tools/test_doc_tools.py`
- [ ] T020 [P] [US3] Unit tests for `extract_visuals` in `tests/unit/tools/test_vision_tools.py`

### Implementation for User Story 3

- [ ] T021 [US3] Implement `ingest_pdf` using `docling` with graceful failure handling in `src/tools/doc_tools.py` (FR-005)
- [ ] T022 [US3] Implement `extract_visuals` to save images to the isolated temporary workspace in `src/tools/vision_tools.py` (FR-007)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T023 [P] Update `README.md` with forensic tool usage examples
- [ ] T024 [P] Validate `quickstart.md` steps against final implementation
- [ ] T025 Performance audit: Ensure all tool calls complete under 60s (SC-003)
- [ ] T026 Determinism audit: Verify bit-identical results for repeated runs (SC-005)
- [ ] T027 Final security audit: Verify 100% cleanup of temporary artifacts (SC-001)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 and US2 are P1 and can proceed in parallel.
  - US3 is P2 and should follow US1/US2.
- **Polish (Final Phase)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent after Phase 2.
- **User Story 2 (P1)**: Independent after Phase 2.
- **User Story 3 (P2)**: Independent after Phase 2.

### Parallel Opportunities

- T003 (Linting) can run parallel with T001/T002.
- T006 and T007 (Utils) can run parallel with T004/T005.
- All test tasks marked [P] can run in parallel.
- Once Phase 2 is done, Developers can work on US1, US2, and US3 in parallel.

---

## Parallel Example: User Stories 1 & 2

```bash
# Developer A: Implement Repo Tools
Task: T008 [P] [US1] Unit tests for clone_repo...
Task: T011 [US1] Implement clone_repo...

# Developer B: Implement AST Tools
Task: T014 [P] [US2] Unit tests for scan_repository...
Task: T017 [US2] Implement scan_repository...
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2)

1. Complete Phase 1 & 2 (Setup & Foundational).
2. Complete Phase 3 (User Story 1 - Secure Cloning).
3. Complete Phase 4 (User Story 2 - Safe AST Analysis).
4. **STOP and VALIDATE**: Test both stories independently. This provides a complete "Source Code Forensic" capability.

### Incremental Delivery

1. Foundation ready.
2. Add US1 → Test independently → Source retrieval capability ready.
3. Add US2 → Test independently → Source analysis capability ready.
4. Add US3 → Test independently → Document verification capability ready.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Always verify tests fail before implementing (Red-Green-Refactor)
- Ensure all subprocess calls include `timeout=60` and `shell=False`.
- Maximum disk limit (1GB) must be checked during cloning and PDF processing.
