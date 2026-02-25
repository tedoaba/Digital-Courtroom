# Tasks: Final Report Generation and Audit Artifacts

**Input**: Design documents from `/specs/010-report-generation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 [P] Create `src/templates/` directory for Jinja2 templates
- [ ] T002 Add `jinja2` to project dependencies in `pyproject.toml` or `requirements.txt`
- [ ] T003 [P] Initialize `audit/reports/` directory in `.gitignore` to prevent committing local reports

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create base Jinja2 template `src/templates/report.md.j2` with basic GFM structure
- [ ] T005 [P] Implement OS-agnostic path management using `pathlib` in `src/nodes/justice.py`
- [ ] T006 Configure `StructuredLogger` for the `ReportGenerator` node in `src/nodes/justice.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Generate Comprehensive Audit Report (Priority: P1) 🎯 MVP

**Goal**: Translate the synthesized `AuditReport` Pydantic model into a structured Markdown document.

**Independent Test**: Provide a mocked `AuditReport` and verify the resulting `.md` file contains Executive Summary, Criteria, and Remediation Plan.

### Tests for User Story 1

- [ ] T007 [P] [US1] Create unit tests for Markdown rendering in `tests/unit/nodes/test_report.py`
- [ ] T008 [US1] Implement rendering check for Executive Summary and Scorebox in `tests/unit/nodes/test_report.py`

### Implementation for User Story 1

- [ ] T009 [US1] Implement Executive Summary and Scorebox block in `src/templates/report.md.j2`
- [ ] T010 [US1] Implement Criterion Breakdown loop with Dimension Name and Score in `src/templates/report.md.j2`
- [ ] T011 [US1] Implement Judicial Debate (collapsible) and Dissenting Opinion logic in `src/templates/report.md.j2`
- [ ] T012 [US1] Implement Remediation Plan section grouped by Criterion in `src/templates/report.md.j2`
- [ ] T013 [US1] Implement `report_generator` node logic in `src/nodes/justice.py` to render the `report.md.j2` template

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Forensic Evidence Traceability (Priority: P2)

**Goal**: Include a "Checksum Log" and "Evidence Manifest" linking findings to forensic sources.

**Independent Test**: Verify that every `evidence_id` cited in the report links to an entry in the "Forensic Evidence Manifest".

### Tests for User Story 2

- [ ] T014 [P] [US2] Update `tests/unit/nodes/test_report.py` to include evidence citation and manifest validation

### Implementation for User Story 2

- [ ] T015 [US2] Implement Forensic Evidence Manifest table in `src/templates/report.md.j2`
- [ ] T016 [US2] Implement Checksum Log as a collapsible `<details>` block with raw JSON in `src/templates/report.md.j2`
- [ ] T017 [US2] Implement `run_manifest.json` file generation in `src/nodes/justice.py`
- [ ] T018 [US2] Ensure all `evidence_id` references in the report are consistent with the manifest

**Checkpoint**: User Stories 1 and 2 are functional and provide full traceability.

---

## Phase 5: User Story 3 - Resilient Reporting on Partial Failures (Priority: P2)

**Goal**: Handle missing data gracefully without crashing, producing a "Partial Report".

**Independent Test**: Pass an `AuditReport` with missing criteria/opinions and verify the output contains "Audit Error" placeholders.

### Tests for User Story 3

- [ ] T019 [P] [US3] Add test case for partial data handling in `tests/unit/nodes/test_report.py`

### Implementation for User Story 3

- [ ] T020 [US3] Add Jinja2 conditionals to handle null or empty fields in `src/templates/report.md.j2`
- [ ] T021 [US3] Implement `fallback_render` exception handling in `src/nodes/justice.py`

**Checkpoint**: The generator is now resilient to node failures.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements and integration

- [ ] T022 [P] Update docstrings and technical notes in `src/nodes/justice.py`
- [ ] T023 [P] Implement Jinja2 `trim_blocks` and `lstrip_blocks` to optimize Markdown formatting
- [ ] T024 Created integration test for full report generation pipeline in `tests/integration/test_full_pipeline.py`
- [ ] T025 [P] Verify `quickstart.md` manual trigger instructions against final implementation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on T001, T002.
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion. **MVP Target**.
- **User Story 2 (Phase 4)**: Depends on Phase 3 completion.
- **User Story 3 (Phase 5)**: Depends on Phase 3 completion.
- **Polish (Phase 6)**: Depends on all user stories.

### Parallel Opportunities

- T001, T002, T003 can run in parallel.
- T005 and T006 can run in parallel within Phase 2.
- Once User Story 1 starts, test tasks (T007, T008) can be developed alongside template skeletal work.
- User Story 2 and 3 can technically be developed in parallel after US1 foundation is laid.

---

## Parallel Example: User Story 1

```bash
# Writing tests and template segments in parallel:
Task: "Implement rendering check for Executive Summary and Scorebox in tests/unit/nodes/test_report.py"
Task: "Implement Executive Summary and Scorebox block in src/templates/report.md.j2"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational phases.
2. Complete Phase 3 (User Story 1).
3. **STOP and VALIDATE**: Verify Markdown report matches `report-structure.md`.

### Incremental Delivery

1. Foundation -> Core Reporting (US1) -> Traceability (US2) -> Resilience (US3).
2. Each step adds a significant required artifact (Report -> Manifest -> Errors).

---

## Notes

- [P] tasks = different files or decoupled logic.
- [Story] labels ensure task progress maps to user requirements.
- Citations MUST use `evidence_id` from `src/state.py`.
- Deterministic output is a requirement (check for random hash keys in JSON).
