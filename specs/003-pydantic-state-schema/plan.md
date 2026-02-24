# Implementation Plan: Pydantic State Schema and Annotated Reducers

**Branch**: `003-pydantic-state-schema` | **Date**: 2026-02-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-pydantic-state-schema/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

This feature implements the foundational data models and state management for the Digital Courtroom project. Using Pydantic v2 and LangGraph, we will define **strictly typed schemas** for `Evidence`, `JudicialOpinion`, `CriterionResult`, and `AuditReport`. The implementation enforces **zero-tolerance for extra fields or type coercion**, uses **custom reducers** for parallel-safe merge (`evidences`, `criterion_results`) with deduplication, and integrates **Constitution XI** scoring logic (Security Overrides and Weighted Averages: Architecture=1.5, Security=2.0).

## Technical Context

**Language/Version**: Python 3.12+ (Requires Generic Type hints and Pydantic v2)
**Primary Dependencies**: `pydantic>=2.6.0`, `langgraph`, `typing_extensions`
**Storage**: N/A (Internal state management)
**Testing**: `pytest` (Unit tests for validation and reducers)
**Target Platform**: Multi-platform (Linux/Windows)
**Project Type**: Core Infrastructure / Data Modeling
**Performance Goals**: Sub-millisecond validation for parallel graph execution.
**Constraints**:

- **FORBID EXTRA**: `extra='forbid'` on all models.
- **STRICT TYPE**: `strict=True` to prevent LLM type hallucinations.
- **FATAL REDUCERS**: Custom merge functions raise `TypeError` on structural mismatch.
  **Scale/Scope**: 4 core Pydantic models, 1 AgentState TypedDict, 2 custom reducer functions.

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- **IV.1 (Schema-First Design)**: All models use Pydantic `BaseModel`. (Status: PASS)
- **IV.2 (Annotated Reducers)**: `AgentState` uses `Annotated` with custom deduplicating/confidence-based reducers. (Status: PASS)
- **V.1 (Type Annotations)**: Full PEP-484 compliance required in `src/state.py`. (Status: PASS)
- **V.3 (Evidence Confidence)**: Field constraint `[0.0, 1.0]` implemented. (Status: PASS)
- **V.4 (Judicial Score)**: Field constraint `[1, 5]` implemented. (Status: PASS)
- **VI.1 (Parallel Evidences)**: `Annotated[Dict[str, List[Evidence]], merge_evidences]` used. (Status: PASS)
- **VI.2 (Parallel Opinions)**: `Annotated[List[JudicialOpinion], operator.add]` used. (Status: PASS)
- **XI.1 (Security Override)**: `security_violation_found` flag integrated for score capping. (Status: PASS)
- **XX.1 (File Structure)**: State models strictly placed in `src/state.py`. (Status: PASS)

## Project Structure

### Documentation (this feature)

```text
specs/003-pydantic-state-schema/
├── plan.md              # This file
├── research.md          # Custom reducer and validation patterns
├── data-model.md        # Detailed Pydantic class definitions
├── quickstart.md        # Usage examples for models and state
└── tasks.md             # Sequential implementation tasks
```

### Source Code (repository root)

```text
src/
└── state.py             # Pydantic models, reducers, and AgentState

tests/
└── unit/
    └── test_state.py    # Validation, merging, and weighted scoring tests
```

**Structure Decision**: A single `src/state.py` file will contain all models and reducers to consolidate the "State of Truth" as per Architectural Principle XX.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

_(No violations detected. All clarified requirements align with or exceed Constitutional standards.)_
