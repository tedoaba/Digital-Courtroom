# Tasks: DevOps Hardening — Containerization, Automation & CI/CD

**Input**: Design documents from `/specs/014-devops-hardening/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 [P] Initialize `.dockerignore` file in repository root
- [ ] T002 [P] Create `.hadolint.yaml` for Dockerfile quality standards in repository root
- [ ] T003 [P] Setup basic `Makefile` structure with variables (REPO, SPEC, RUBRIC) in repository root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create DevOps validation script in `tests/devops/test_infrastructure.py` to verify Makefile targets and Dockerfile existence (TDD Red Phase)
- [ ] T005 Implement pre-flight check targets (`.check-uv`, `.check-env`, `.check-dirs`) in `Makefile` with fail-fast instructions for missing prerequisites
- [ ] T006 [P] Configure `ruff` in `pyproject.toml` with strict rulesets aligning with Constitution Principle XXI

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Unified Command Interface (Priority: P1) 🎯 MVP

**Goal**: Provide a technology-agnostic entry point for developers and CI.

**Independent Test**: Run `make run REPO=... SPEC=...` and verify it triggers the python entrypoint correctly.

### Implementation for User Story 1

- [ ] T007 [US1] Implement `run` and `cli` targets in `Makefile` using `uv run`
- [ ] T008 [US1] Implement `test` and `lint` targets in `Makefile` using `pytest` and `ruff`
- [ ] T009 [P] [US1] Implement `clean` target in `Makefile` to remove build artifacts and logs

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Standardized Execution via Docker (Priority: P1)

**Goal**: Deliver an isolated, non-root execution environment using Docker and `uv`.

**Independent Test**: Build with `make docker-build` and run with `make docker-run`, verifying access to host volumes.

### Implementation for User Story 2

- [ ] T010 [US2] Create multi-stage `Dockerfile` using `ghcr.io/astral-sh/uv` binary copy and pinned `python:3.12.9-slim` base image
- [ ] T011 [US2] Configure non-root user `courtroom_user` and specific volume permissions (`/reports` as `ro`, `/audit` as `rw`)
- [ ] T012 [US2] Implement `docker-build` target in `Makefile` tagging as `digital-courtroom:latest`
- [ ] T013 [US2] Implement `docker-run` target in `Makefile` with correct volume mapping and environment variable verification in entrypoint

**Checkpoint**: User Story 2 is ready; the application can now run identical to production locally.

---

## Phase 5: User Story 3 - Automated Quality Gates (Priority: P2)

**Goal**: Enforce code quality, security, and functional correctness on every push.

**Independent Test**: Verifying the GitHub Actions status on the branch `014-devops-hardening`.

### Implementation for User Story 3

- [ ] T014 [US3] Create GitHub Actions workflow at `.github/workflows/main.yml` triggering on `main`, `rc/*`, and PRs
- [ ] T015 [P] [US3] Implement linting job in `main.yml` using `ruff` (errors/warnings) and `hadolint/hadolint-action` (severity `info`+)
- [ ] T016 [US3] Implement security audit job in `main.yml` using `pypa/gh-action-pip-audit` v2.x
- [ ] T017 [US3] Implement testing job in `main.yml` using `pytest` with coverage report (gate ≥ 80% on Core Modules)
- [ ] T018 [US3] Implement Docker build verification job in `main.yml`
- [ ] T022 [P] [US3] Add `docker system prune` step to CI to cleanup failed/dangling build artifacts

**Checkpoint**: CI/CD pipeline is active and blocking regressions.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and documentation

- [ ] T019 [P] Update `specs/014-devops-hardening/quickstart.md` with any discovered nuances during implementation
- [ ] T020 Run `make lint` and `make test` project-wide to ensure 100% compliance
- [ ] T021 Verify containerized TUI responsiveness via `make docker-run`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup.
- **User Stories (Phase 3+)**: Depend on Foundational (Phase 2). US1 and US2 can run in parallel. US3 depends on US1/US2 targets existing to be fully effective in CI.
- **Polish (Final Phase)**: Depends on all user stories.

### Parallel Opportunities

- T001/T002/T003 can run in parallel.
- US1 and US2 can be implemented in parallel by different developers.
- Within US3, CI jobs (T015, T016, T017) can run in parallel on the GitHub runners.

---

## Parallel Example: User Story 1 & 2

```bash
# Developer A works on US1:
Task: "Implement run and cli targets in Makefile"

# Developer B works on US2:
Task: "Create multi-stage Dockerfile"
```

---

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Complete Setup and Foundational.
2. Complete User Story 1 (Makefile) to enable local standardized commands.
3. Complete User Story 2 (Docker) to ensure isolation.
4. **VALIDATE**: Run `make docker-run` locally.

### Incremental Delivery

1. Foundation ready.
2. US1 adds value for local dev.
3. US2 adds value for environment parity.
4. US3 protects the branch from regressions automatically.
