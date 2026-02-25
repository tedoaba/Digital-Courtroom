# Implementation Plan: Dialectical Judicial Agents (Layer 2)

**Branch**: `008-judicial-nodes` | **Date**: 2026-02-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-judicial-nodes/spec.md`

## Summary

Implement the Layer 2 Judicial Layer consisting of three persona-based agents (`Prosecutor`, `Defense`, `TechLead`). These agents will execute in parallel to evaluate forensic evidence collected in Layer 1. The implementation enforces adversarial review through distinct system prompts with < 10% overlap, utilizes `.with_structured_output()` for schema-strict responses, and implements granular parallelization (per dimension per judge) to ensure resilience and high-quality feedback.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: LangGraph, Pydantic, LangChain (for LLM orchestration), `config.py` (internal configuration system)  
**Storage**: N/A (Transient state resides in LangGraph `AgentState`)  
**Testing**: pytest (unit and integration)  
**Target Platform**: Python 3.12+ (managed via `uv`)
**Project Type**: Multi-agent orchestration layer  
**Performance Goals**: Support ~30 parallel LLM calls per audit run; latency managed via asynchronous fan-out.  
**Constraints**: `temperature=0` (mandatory), max 2 retries on schema failure, exponential backoff (max 3 retries) on HTTP/timeout errors.  
**Scale/Scope**: 3 judge personas evaluating ~10 rubric criteria independently.

## Constitution Check

| Principle                        | Condition                                                    | Status |
| -------------------------------- | ------------------------------------------------------------ | ------ |
| I. Spec-Driven                   | Spec defined and references Constitutional principles.       | ✅     |
| III. Deterministic Transitions   | `temperature=0` applied; judicial variance bounded.          | ✅     |
| IV. Schema-First                 | `JudicialOpinion` uses Pydantic with field constraints.      | ✅     |
| V. Typing/Validation             | Schema violation retry logic (max 2) enforced.               | ✅     |
| VI. Parallel-Safe Reducers       | `opinions` field uses `Annotated[..., operator.add]`.        | ✅     |
| VII. Error Handling              | Fallback `score=3` defined; exponential backoff on timeouts. | ✅     |
| VIII. Evidence Precedes Judgment | Prompt forces citation of detective `evidence_id`.           | ✅     |
| X. Dialectical Execution         | 3 personas with < 10% prompt overlap.                        | ✅     |
| XIV. Parallel Fan-Out/Fan-In     | Judges execute in parallel branches from sync point.         | ✅     |

## Project Structure

### Documentation (this feature)

```text
specs/008-judicial-nodes/
├── plan.md              # This file
├── research.md          # Domain research & prompt analysis
├── data-model.md        # JudicialOpinion & Judge definitions
├── quickstart.md        # Local execution guide for judicial layer
├── checklists/
│   └── requirements.md  # Requirement validation
└── tasks.md             # Implementation tasks (Phase 2)
```

### Source Code (repository root)

```text
src/
├── nodes/
│   └── judges.py        # Prosecutor, Defense, TechLead node definitions
├── state.py             # JudicialOpinion schema and AgentState update
└── config.py            # temperature=0 and model constraints

tests/
├── integration/
│   └── test_judicial_workflow.py # Fan-out/fan-in verification
└── unit/
    └── test_judges.py   # Persona prompts & fallback tests
```

**Structure Decision**: Option 1 (Single Project) is used as it aligns with the existing codebase structure where nodes are grouped by responsibility in `src/nodes/`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |
