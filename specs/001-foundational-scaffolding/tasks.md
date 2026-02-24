# Tasks: Foundational Scaffolding & Configuration Strategy

**Input**: Design documents from `/specs/001-foundational-scaffolding/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Included as part of the "Automated Verification Readiness" story and "Secure Configuration" story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize repository with `uv init` and project metadata in `pyproject.toml`
- [ ] T002 Create root directory structure: `src/`, `tests/`, `rubric/`, `audit/`
- [ ] T003 [P] Create `.gitignore` with Python and environment variable exclusions
- [ ] T004 [P] Create `.python-version` file specifying Python 3.12+

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 [P] Configure `ruff` for linting and formatting in `pyproject.toml`
- [ ] T006 [P] Configure `pytest` and `pytest-asyncio` in `pyproject.toml`
- [ ] T007 Initialize `src/__init__.py` and `tests/__init__.py` to mark package boundaries

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Consistent Development Environment (Priority: P1) 🎯 MVP

**Goal**: Standardized environment setup using `uv` to ensure reproducibility across all machines.

**Independent Test**: Running `uv sync` in a fresh environment results in all dependencies installed and `src/` structure validated.

### Implementation for User Story 1

- [ ] T008 [US1] Add primary dependencies to `pyproject.toml` (`langgraph`, `langchain`, `pydantic`, `python-dotenv`, `pydantic-settings`)
- [ ] T009 [US1] Add development dependencies to `pyproject.toml` (`pytest`, `pytest-asyncio`, `ruff`)
- [ ] T010 [US1] Create placeholder nodes and tools directories with `src/nodes/.placeholder` and `src/tools/.placeholder`
- [ ] T011 [US1] Create initial `src/graph.py` as a placeholder for the StateGraph

---

## Phase 4: User Story 2 - Secure and Validated Configuration (Priority: P1)

**Goal**: Implement a fail-fast configuration framework that validates all mandatory API keys and settings at startup.

**Independent Test**: Running the application or settings test without an `.env` file containing `OPENAI_API_KEY` causes an immediate termination with a clear error message.

### Implementation for User Story 2

- [ ] T012 [P] [US2] Create `.env.example` following the `SystemSettings` schema in `specs/001-foundational-scaffolding/data-model.md`
- [ ] T013 [US2] Create `tests/test_config.py` to verify that the config loader correctly identifies and reports missing mandatory environment variables (Red Phase)
- [ ] T014 [US2] Implement `SystemSettings` Pydantic model in `src/config.py` using `pydantic-settings` (Green Phase)
- [ ] T015 [US2] Implement fail-fast loader in `src/config.py` that raises a descriptive error on missing mandatory keys (Green Phase)
- [ ] T016 [US2] Implement regex-based secret scanner in `src/config.py` to detect hardcoded keys during validation (FR-008)
- [ ] T017 [US2] Create `src/state.py` containing the initial `AppState` model as defined in `data-model.md`

**Checkpoint**: Configuration system is robust and secure - subsequent nodes can now safely access settings.

---

## Phase 5: User Story 3 - Automated Verification Readiness (Priority: P2)

**Goal**: Establish a pre-integrated testing framework so developers can verify code quality and functionality from day one.

**Independent Test**: Executing `uv run pytest` identifies and runs all tests in the `tests/` directory, providing a summary report of results.

### Implementation for User Story 3

- [ ] T018 [US3] Create `tests/conftest.py` with shared fixtures for configuration mocking during tests
- [ ] T019 [US3] Implement `tests/test_scaffolding.py` to verify that the file system structure matches the architectural requirements in `plan.md`
- [ ] T020 [US3] Verify `ruff` configuration by running `uv run ruff check .` across the newly created foundation

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Final quality checks and documentation validation.

- [ ] T021 Run `uv run ruff format .` to ensure all generated code meets project standards
- [ ] T022 [P] Validate `quickstart.md` instructions against the actual implemented CLI commands
- [ ] T023 [P] Verify SC-001: Measure environment sync time (Target: < 15s)
- [ ] T024 [P] Verify SC-004: Measure config failure response time (Target: < 1s)
- [ ] T025 Final audit of `src/` structure against Appendix A of Architecture Notes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 completion.
- **User Stories (Phase 3+)**: All depend on Phase 2 completion.
  - US1 and US2 are P1 and should be completed first.
  - US3 (P2) can follow.
- **Polish (Final Phase)**: Depends on all stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Sets up the base requirements and structure.
- **User Story 2 (P2)**: Depends on the source structure from US1.
- **User Story 3 (P3)**: Depends on the testing dependencies from US1 and the config tests from US2.

### Parallel Opportunities

- T003, T004 (Phase 1)
- T005, T006 (Phase 2)
- T012 can be done in parallel with other US2 tasks as it is a template.
- T021 can be done in parallel with T022.

---

## Parallel Example: Phase 2 Foundation

```bash
# Configure quality tools in parallel:
Task: "Configure ruff for linting and formatting in pyproject.toml"
Task: "Configure pytest and pytest-asyncio in pyproject.toml"
```

---

## Implementation Strategy

### MVP First (US1 & US2 Only)

1. Complete Phase 1 and 2 to get the repo "online".
2. Complete User Story 1 to establish the environment and `src/` layout.
3. Complete User Story 2 to ensure security and configuration safety.
4. **STOP and VALIDATE**: Verify that a developer can sync the environment and the system fails-fast without an `.env`.

### Incremental Delivery

1. Foundation ready.
2. US1 adds structure.
3. US2 adds security/config.
4. US3 adds verification.
5. Polish ensures quality.
