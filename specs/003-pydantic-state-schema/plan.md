# Implementation Plan: Pydantic State Schema and Annotated Reducers

**Branch**: `003-pydantic-state-schema` | **Date**: 2026-02-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-pydantic-state-schema/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

This feature implements the foundational data models and state management for the Digital Courtroom project. Using Pydantic v2 and LangGraph, we will define strongly typed schemas for `Evidence`, `JudicialOpinion`, `CriterionResult`, and `AuditReport`. We will also implement the central `AgentState` with custom reducers for parallel-safe merging, ensuring that evidence is deduplicated and criterion results are resolved based on the highest confidence.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Pydantic v2, LangGraph, typing_extensions
**Storage**: N/A (Internal state management)
**Testing**: pytest
**Target Platform**: Linux/Windows (Python environment)
**Project Type**: Internal State Management / Data Modeling
**Performance Goals**: Sub-millisecond validation and merging for state transitions.
**Constraints**: Immutability for core entities, strict range validation for confidence and scores.
**Scale/Scope**: 4 core Pydantic models, 1 AgentState TypedDict with 2 custom reducer functions.

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- **IV.1 (Schema-First Design)**: Models use `BaseModel` and `TypedDict`. (Status: PASS)
- **IV.2 (Annotated Reducers)**: `AgentState` uses `Annotated` with reducers. (Status: PASS)
- **V.3 (Evidence Confidence)**: `ge=0.0, le=1.0` enforced. (Status: PASS)
- **V.4 (Judicial Score)**: `ge=1, le=5` enforced. (Status: PASS)
- **VI.1/2 (Reducer Standards)**: Custom reducers follow append/merge patterns. (Status: PASS)
- **XX.1 (File Structure)**: State definitions placed in `src/state.py`. (Status: PASS)

## Project Structure

### Documentation (this feature)

```text
specs/003-pydantic-state-schema/
├── plan.md              # This file
├── research.md          # Custom reducer implementation patterns
├── data-model.md        # Detailed Pydantic class definitions
├── quickstart.md        # Usage examples for models and state
└── tasks.md             # Task decomposition
```

### Source Code (repository root)

```text
src/
├── state.py             # Pydantic models and AgentState definition
└── reducers.py          # Custom reducer functions (optional separation)

tests/
└── unit/
    └── test_state.py    # Validation and merge logic tests
```

**Structure Decision**: Models will live in `src/state.py` to satisfy Constitution principle XX. Custom reducers for state merging will be placed in the same file or a utility file if they become complex.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

_(No violations detected)_
