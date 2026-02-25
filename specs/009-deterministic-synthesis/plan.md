# Implementation Plan: Deterministic Synthesis via Chief Justice (Layer 3)

**Branch**: `009-deterministic-synthesis` | **Date**: 2026-02-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-deterministic-synthesis/spec.md`

## Summary

This feature implements the final synthesis layer (Layer 3) of the Digital Courtroom. The `ChiefJusticeNode` will be a pure Python component responsible for consolidating opinions from the Prosecutor, Defense, and Tech Lead into a final `AuditReport`. It uses deterministic rules (Security Override, Fact Supremacy, Functionality Weight, Variance Re-evaluation) to ensure the verdict is grounded in forensic evidence and strictly prioritized by security mandates, eliminating LLM non-determinism in the final scoring.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: LangGraph, Pydantic, operator (for reducers)
**Storage**: N/A (State-managed in LangGraph)
**Testing**: pytest (unit tests for node logic, integration for graph fan-in)
**Target Platform**: CLI / LangGraph Orchestrator
**Project Type**: Agent Orchestration Node
**Performance Goals**: < 50ms per criterion synthesis
**Constraints**: ZERO LLM calls in ChiefJusticeNode; Round Half Up (2.5 -> 3) logic.
**Scale/Scope**: 10 rubric dimensions; 3 judicial opinions per dimension.

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- [x] **Principle III.5**: Synthesis rules in `ChiefJusticeNode` MUST be fully deterministic Python logic — no LLM calls.
- [x] **Principle XI**: Rule-Based Synthesis (Security Override, Fact Supremacy, Functionality Weight, Dissent Requirement, Variance Re-evaluation) must be enforced.
- [x] **Principle XXIV.3**: Synthesis engine MUST produce identical verdicts given identical inputs.
- [x] **Principle XXIX**: Unit tests MUST verify Security Override caps, Fact Supremacy nullification, and high-variance triggers.
- [x] **Principle IV**: Results MUST be validated against Pydantic schemas.

## Project Structure

### Documentation (this feature)

```text
specs/009-deterministic-synthesis/
├── plan.md              # This file
├── research.md          # Phase 0 research output
├── data-model.md        # Phase 1 data model output
├── quickstart.md        # Phase 1 quickstart guide
└── tasks.md             # Phase 2 tasks output (via /speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── nodes/
│   └── justice.py       # Implementation of ChiefJusticeNode
└── state.py             # CriterionResult and AuditReport schemas

tests/
├── unit/
│   └── test_justice.py  # Unit tests for synthesis rules
└── integration/
    └── test_synthesis_workflow.py # Integration with judge fan-in
```

**Structure Decision**: Single project structure. Logic resides in `src/nodes/justice.py` following principle XX.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |
